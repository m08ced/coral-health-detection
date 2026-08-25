import os
import uuid
import cv2
import numpy as np
from flask import Flask, render_template, request, jsonify, url_for
from waitress import serve

app = Flask(__name__)

UPLOAD_FOLDER = os.path.join('static', 'uploads')
RESULT_FOLDER = os.path.join('static', 'results')
os.makedirs(UPLOAD_FOLDER, exist_ok=True)
os.makedirs(RESULT_FOLDER, exist_ok=True)

stage1_model = None
stage2_model = None

def load_models():
    global stage1_model, stage2_model
    try:
        from ultralytics import YOLO
        stage1_path = os.path.join('models', 'stage1_best.pt')
        stage2_path = os.path.join('models', 'stage2_best.pt')
        if os.path.exists(stage1_path):
            stage1_model = YOLO(stage1_path)
            print('Stage 1 model loaded.')
        else:
            print(f'Stage 1 weights not found at {stage1_path}')
        if os.path.exists(stage2_path):
            stage2_model = YOLO(stage2_path)
            print('Stage 2 model loaded.')
        else:
            print(f'Stage 2 weights not found at {stage2_path}')
    except Exception as e:
        print(f'Model loading error: {e}')

def run_inference(image_path):
    image = cv2.imread(image_path)
    if image is None:
        return None, {}

    annotated = image.copy()

    COLOR_ALIVE = (54, 243, 137)
    COLOR_DEAD = (0, 0, 255)
    COLOR_NON_HARD = (255, 255, 255)

    counts = {'alive': 0, 'dead': 0, 'non_hard': 0}

    if stage1_model is None or stage2_model is None:
        h, w = annotated.shape[:2]
        cv2.rectangle(annotated, (50, 50), (w - 50, h - 50), COLOR_ALIVE, 12)
        cv2.putText(annotated, 'alive (demo)', (55, 45),
                    cv2.FONT_HERSHEY_SIMPLEX, 1.0, COLOR_ALIVE, 2, lineType=cv2.LINE_AA)
        return annotated, {'alive': 1, 'dead': 0, 'non_hard': 0}

    stage1_results = stage1_model(image, imgsz=416, conf=0.10)[0]

    font = cv2.FONT_HERSHEY_SIMPLEX
    font_scale = 1.0
    thickness = 2

    for box in stage1_results.boxes:
        cls_id = int(box.cls[0])
        x1, y1, x2, y2 = map(int, box.xyxy[0])
        conf1 = float(box.conf[0])

        if cls_id == 1:
            counts['non_hard'] += 1
            box_color = COLOR_NON_HARD
            label_text = f'non-hard coral {conf1:.2f}'
            text_color = (0, 0, 0)
            
            cv2.rectangle(annotated, (x1, y1), (x2, y2), box_color, 8)
            (tw, th), baseline = cv2.getTextSize(label_text, font, font_scale, thickness)
            
            tag_y1 = max(0, y1 - th - 15)
            tag_y2 = y1
            tag_x1 = x1
            tag_x2 = x1 + tw + 15
            
            cv2.rectangle(annotated, (tag_x1, tag_y1), (tag_x2, tag_y2), box_color, cv2.FILLED)
            cv2.putText(annotated, label_text, (tag_x1 + 8, tag_y2 - baseline - 5), font, font_scale, text_color, thickness, lineType=cv2.LINE_AA)
            continue

        crop = image[max(0, y1):min(image.shape[0], y2),
                     max(0, x1):min(image.shape[1], x2)]
        if crop.size == 0:
            continue

        stage2_results = stage2_model(crop, imgsz=416, conf=0.25)[0]

        label = 'alive'
        box_color = COLOR_ALIVE
        text_color = (0, 0, 0)
        conf2 = conf1

        if len(stage2_results.boxes) > 0:
            best = max(stage2_results.boxes, key=lambda b: float(b.conf[0]))
            health_cls = int(best.cls[0])
            conf2 = float(best.conf[0])
            if health_cls == 1:
                label = 'dead'
                box_color = COLOR_DEAD
                text_color = (255, 255, 255)
            else:
                label = 'alive'
                box_color = COLOR_ALIVE
                text_color = (0, 0, 0)

        counts[label] += 1
        label_text = f'{label} {conf2:.2f}'
        
        cv2.rectangle(annotated, (x1, y1), (x2, y2), box_color, 8)
        (tw, th), baseline = cv2.getTextSize(label_text, font, font_scale, thickness)
        
        tag_y1 = max(0, y1 - th - 15)
        tag_y2 = y1
        tag_x1 = x1
        tag_x2 = x1 + tw + 15
        
        cv2.rectangle(annotated, (tag_x1, tag_y1), (tag_x2, tag_y2), box_color, cv2.FILLED)
        cv2.putText(annotated, label_text, (tag_x1 + 8, tag_y2 - baseline - 5), font, font_scale, text_color, thickness, lineType=cv2.LINE_AA)

    return annotated, counts

@app.route('/')
def index():
    return render_template('index.html')

@app.route('/predict', methods=['POST'])
def predict():
    if 'image' not in request.files:
        return jsonify({'error': 'No image uploaded'}), 400

    file = request.files['image']
    if file.filename == '':
        return jsonify({'error': 'Empty filename'}), 400

    filename = f"{uuid.uuid4().hex}.jpg"
    upload_path = os.path.join(UPLOAD_FOLDER, filename)
    file.save(upload_path)

    result_img, counts = run_inference(upload_path)
    if result_img is None:
        return jsonify({'error': 'Could not process image'}), 500

    result_filename = f"result_{filename}"
    result_path = os.path.join(RESULT_FOLDER, result_filename)
    cv2.imwrite(result_path, result_img)

    result_url = url_for('static', filename=f'results/{result_filename}')
    return jsonify({
        'result_url': result_url,
        'counts': counts
    })

if __name__ == '__main__':
    load_models()
    port = int(os.environ.get('PORT', 8080))
    print(f"Starting server on port {port}")
    serve(app, host='0.0.0.0', port=port)
