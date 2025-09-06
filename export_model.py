import torch
import torchvision.models as models

# 1. Завантажуємо готову модель MobileNet V2
model = models.mobilenet_v2(pretrained=True)
model.eval()  # важливо перевести в режим inference

# 2. Конвертуємо в TorchScript
example_input = torch.rand(1, 3, 224, 224)  # приклад випадкового зображення
traced_model = torch.jit.trace(model, example_input)

# 3. Зберігаємо модель на диск
traced_model.save("model.pt")

print("TorchScript-модель збережена як model.pt")