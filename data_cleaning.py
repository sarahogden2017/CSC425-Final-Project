import os
from PIL import Image
import torch
import torchvision.transforms as transforms
from torchvision import models
from torchvision import models
from torchvision.models import ResNet18_Weights
import torch.nn.functional as F


model = models.resnet18(weights=ResNet18_Weights.DEFAULT)
model.eval()

weights = ResNet18_Weights.DEFAULT
transform = weights.transforms()

def classify_image(path):
    try:
        img = Image.open(path).convert('RGB')
        input_tensor = transform(img).unsqueeze(0)
        with torch.no_grad():
            output = model(input_tensor)
            _, predicted = torch.max(output, 1)
            label = categories[predicted.item()]
            return label
    except Exception as e:
        return f"Error: {e}"

# Scan folder and count likely photos
folder = "./data"
photo_keywords = [
    "flower", "plant", "daisy", "sunflower", "rose", "tulip", "orchid", "iris",
    "lily", "lavender", "poppy", "magnolia", "lotus", "coreopsis", "carnation",
    "bellflower", "astilbe", "calendula", "dandelion", "water lily"
]
summary = {}

for root, dirs, files in os.walk(folder):
    photo_count = 0
    not_photo_count = 0
    for file in files:
        if file.lower().endswith(('.jpg', '.jpeg', '.png')):
            path = os.path.join(root, file)
            label = classify_image(path)
            if any(keyword in label.lower() for keyword in photo_keywords):
                photo_count += 1
            else:
                not_photo_count += 1
    if photo_count + not_photo_count > 0:
        rel_path = os.path.relpath(root, folder)
        summary[rel_path] = (photo_count, not_photo_count)

# Print results
for folder, (photos, not_photos) in summary.items():
    print(f"{folder}: {photos} likely photos, {not_photos} not photos")