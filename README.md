# Title and Description

An AI-based Web Application to Detect and Assess the Health of Hard Corals Using YOLO, developed as part of a STEM Research III study at the Philippine Science High School – Central Visayas Campus in Cebu.

## Overview

This application uses a two-stage YOLO-based deep learning pipeline:
- *Stage 1 (SCoralDet approach):* Detects hard coral vs. non-hard coral regions using YOLOv8
- *Stage 2 (MAFFN approach):* Classifies detected hard corals as alive or dead using YOLOv8

## Features

- Single-image upload via drag-and-drop or file browser
- Automated coral detection with annotated bounding boxes
- Color-coded health classification (green = alive, red = dead, white = non-hard coral)
- Detection summary showing count of each class

## Tech Stack

- *Backend:* Python, Flask, Waitress
- *Frontend:* HTML, CSS, JavaScript
- *Models:* YOLOv8n (Ultralytics)
- *Image Processing:* OpenCV

## Researchers

- Euan Margret A. Cantalejo
- Alyssa Coritico
- Yuumie G. Dizon

## Research Adviser

- Felix S. Calvo

Philippine Science High School – Central Visayas Campus in Cebu, 2024-2026