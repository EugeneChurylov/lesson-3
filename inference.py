import torch
from PIL import Image
from torchvision import transforms
import json
import sys
import os

if len(sys.argv) < 2:
    print("Використання: python inference.py path/to/image.jpg")
    sys.exit(1)

image_path = sys.argv[1]
if not os.path.exists(image_path):
    print(f"Файл не знайдено: {image_path}")
    sys.exit(1)

# 1) Модель
model = torch.jit.load("model.pt")
model.eval()

# 2) Класи ImageNet (підтримує і dict {"0": "..."} і list ["..."])
with open("imagenet_classes.json") as f:
    classes = json.load(f)
if isinstance(classes, dict):
    # зробити список у правильному порядку
    classes = [classes[str(i)] for i in range(len(classes))]

# 3) Препроцес
preprocess = transforms.Compose([
    transforms.Resize(256),
    transforms.CenterCrop(224),
    transforms.ToTensor(),
    transforms.Normalize([0.485, 0.456, 0.406],
                         [0.229, 0.224, 0.225]),
])

img = Image.open(image_path).convert("RGB")
input_tensor = preprocess(img).unsqueeze(0)

# 4) Інференс
with torch.no_grad():
    outputs = model(input_tensor)
probs = torch.nn.functional.softmax(outputs[0], dim=0)
top3_prob, top3_idx = torch.topk(probs, 3)

print(f"\nРезультати інференсу для {image_path}:\n")
for i in range(3):
    idx = int(top3_idx[i])
    label = classes[idx]
    print(f"{label}: {top3_prob[i].item():.4f}")
