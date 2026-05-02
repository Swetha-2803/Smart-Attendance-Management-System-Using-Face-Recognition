import cv2
import os

dataset_path = os.path.join("media", "dataset")
print(f"📂 Checking dataset in: {dataset_path}")

for file in os.listdir(dataset_path):
    if file.lower().endswith((".jpg", ".png", ".jpeg")):
        filepath = os.path.join(dataset_path, file)
        img = cv2.imread(filepath)
        if img is None:
            print(f"❌ Cannot read: {file}")
        else:
            print(f"✅ {file} loaded successfully with shape {img.shape}")
