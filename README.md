# 🚀 MLOps Homework – ArgoCD + MLflow

## 1. Запуск Terraform

Перейти у директорію з Terraform:

```bash
cd mlops-argocd-demo/argocd
```

Ініціалізувати Terraform:

```bash
terraform init
```

Запустити деплой ArgoCD:

```bash
terraform apply -auto-approve
```

---

## 2. Перевірка роботи ArgoCD

Список подів у namespace **infra-tools**:

```bash
kubectl -n infra-tools get pods
```

Очікувано – поди ArgoCD у статусі `Running`.

---

## 3. Відкриття UI ArgoCD

Зробити port-forward:

```bash
kubectl -n infra-tools port-forward svc/argocd-server 8080:443
```

Отримати пароль:

```bash
kubectl -n infra-tools get secret argocd-initial-admin-secret -o jsonpath='{.data.password}' | base64 --decode; echo
```

Увійти в UI:

- URL: [http://localhost:8080](http://localhost:8080)
- Логін: `admin`
- Пароль: з команди вище

---

## 4. Деплой MLflow через ArgoCD Application

Файл **application.yaml** знаходиться в окремому репозиторії.

Застосувати його:

```bash
kubectl -n infra-tools apply -f https://raw.githubusercontent.com/EugeneChurylov/mlops-mlflow-helm/main/mlflow-helm/application.yaml
```

---

## 5. Перевірка деплою MLflow

```bash
# Перевірка namespace mlflow
kubectl get ns

# Перевірка подів і сервісів
kubectl -n mlflow get pods,svc
```

Очікувано:

- Pod **mlflow-mlflow** у статусі `Running`
- Service **mlflow-mlflow** з портом `5000/TCP`

---

## 6. Доступ до MLflow UI

```bash
kubectl -n mlflow port-forward svc/mlflow-mlflow 5000:5000
```

Відкрити у браузері:  
👉 [http://localhost:5000](http://localhost:5000)

---

## 7. Посилання на репозиторії

- Основний (Terraform + ArgoCD): https://github.com/EugeneChurylov/lesson-3/tree/lesson-7/mlops-argocd-demo/argocd
- Helm-чарт + Application: https://github.com/EugeneChurylov/mlops-mlflow-helm
