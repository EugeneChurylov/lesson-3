# Lesson 3 — TorchScript Inference in Docker

## 📌 Опис
У цьому проєкті ми:
- Експортували модель **MobileNetV2** у формат TorchScript (`model.pt`)
- Написали скрипт `inference.py`, який приймає зображення і виводить топ-3 класи
- Створили два Docker-образи:
  - **Fat** (великий, >1GB, з усіма інструментами)
  - **Slim** (оптимізований multi-stage, менший за розміром)

---

## 🚀 Як запустити

### 1. Побудувати образи
```bash
docker build -f Dockerfile.fat -t ml-fat .
docker build -f Dockerfile.slim -t ml-slim .
```
### 2. Запустити inference
```bash
# Fat контейнер
docker run --rm -v "$PWD":/app ml-fat python inference.py /app/example.jpg

# Slim контейнер
docker run --rm -v "$PWD":/app ml-slim python inference.py /app/example.jpg
```
### 3. Перевірка розмірів і шарів
```bash
docker images | grep -E 'ml-(fat|slim)'
docker history ml-fat
docker history ml-slim
```