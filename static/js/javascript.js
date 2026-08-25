const dropArea = document.getElementById("drop-area");
const fileInput = document.getElementById("fileInput");
const browseBtn = document.getElementById("browseBtn");
const previewImage = document.getElementById("previewImage");
const previewText = document.getElementById("previewText");
const resultImage = document.getElementById("resultImage");
const resultText = document.getElementById("resultText");
const loadingSpinner = document.getElementById("loadingSpinner");
const step2 = document.getElementById("step2");
const step3 = document.getElementById("step3");
const resetBtn = document.getElementById("resetBtn");

browseBtn.addEventListener("click", () => {
    fileInput.click();
});

fileInput.addEventListener("change", function () {
    if (this.files[0]) {
        handleFile(this.files[0]);
    }
});

dropArea.addEventListener("dragover", (e) => {
    e.preventDefault();
    dropArea.classList.add("dragover");
});

dropArea.addEventListener("dragleave", () => {
    dropArea.classList.remove("dragover");
});

dropArea.addEventListener("drop", (e) => {
    e.preventDefault();
    dropArea.classList.remove("dragover");
    const file = e.dataTransfer.files[0];
    if (file) handleFile(file);
});

function handleFile(file) {
    if (!file.type.startsWith("image/")) {
        alert("Please upload an image file.");
        return;
    }

    const reader = new FileReader();
    reader.onload = function (e) {
        previewImage.src = e.target.result;
        previewImage.style.display = "block";
        previewText.style.display = "none";
        step2.classList.add("active");
    };
    reader.readAsDataURL(file);

    const formData = new FormData();
    formData.append("image", file);

    step3.classList.add("active");
    resultImage.style.display = "none";
    resultText.style.display = "none";
    document.getElementById("summaryBox").style.display = "none";
    loadingSpinner.style.display = "block";
    document.getElementById("loadingText").style.display = "block";
    resetBtn.disabled = true;

    fetch("/predict", {
        method: "POST",
        body: formData,
    })
        .then((response) => response.json())
        .then((data) => {
            loadingSpinner.style.display = "none";
            document.getElementById("loadingText").style.display = "none";
            if (data.result_url) {
                resultImage.src = data.result_url + "?t=" + new Date().getTime();
                resultImage.style.display = "block";
                resultText.style.display = "none";

                const c = data.counts;
                const total = c.alive + c.dead + c.non_hard;
                document.getElementById("detectionSummary").textContent =
                    `Detected ${total} region(s): ${c.alive} alive hard coral, ${c.dead} dead hard coral, ${c.non_hard} non-hard coral`;
                document.getElementById("summaryBox").style.display = "block";
            } else {
                resultText.textContent = "Detection failed. Please try another image.";
                resultText.style.display = "block";
            }
            resetBtn.disabled = false;
        })
        .catch(() => {
            loadingSpinner.style.display = "none";
            resultText.textContent = "An error occurred. Please try again.";
            resultText.style.display = "block";
            resetBtn.disabled = false;
        });
}

resetBtn.addEventListener("click", () => {
    previewImage.src = "";
    previewImage.style.display = "none";
    previewText.style.display = "block";
    fileInput.value = "";
    step2.classList.remove("active");

    resultImage.src = "";
    resultImage.style.display = "none";
    resultText.textContent = "Results will appear here after upload.";
    resultText.style.display = "block";
    loadingSpinner.style.display = "none";
    document.getElementById("loadingText").style.display = "none";
    document.getElementById("summaryBox").style.display = "none";
    step3.classList.remove("active");
    resetBtn.disabled = true;
});