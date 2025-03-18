from ultralytics import YOLO
import matplotlib.pyplot as plt
from pathlib import Path

# Initialize a new YOLO model for classification
model = YOLO('yolov8n-cls.pt')  # use the nano classification model

data_path = Path('data')
# Train the model
results = model.train(
    data=data_path,     # Path to data config file
    epochs=100,           # Number of epochs
    imgsz=224,           # Image size
    batch=32,            # Batch size
    name='yolo_classify', # Name of the experiment
    project='runs',       # Project name
    patience=20,         # Early stopping patience
    device='cpu'         # Use CPU for training
)

# Evaluate the model
metrics = model.val()

# Export the model
model.export(format='onnx')  # Exports to ONNX format

# Convert the model to TFlite
model.export(format='tflite')  # Exports to TFlite format

