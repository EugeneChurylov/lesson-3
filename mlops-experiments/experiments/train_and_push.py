#!/usr/bin/env python3
# -*- coding: utf-8 -*-

import os
import shutil
import time
from pathlib import Path

import joblib
import mlflow
from mlflow.tracking import MlflowClient

import numpy as np
from sklearn.datasets import load_iris
from sklearn.linear_model import SGDClassifier
from sklearn.model_selection import train_test_split

from prometheus_client import CollectorRegistry, Gauge, push_to_gateway


# ----------------------------
# Config via ENV (safe defaults)
# ----------------------------
MLFLOW_TRACKING_URI = os.getenv("MLFLOW_TRACKING_URI", "http://localhost:5000")

# Якщо вкажеш MLFLOW_ARTIFACT_URI=s3://mlflow-artifacts — артефакти підуть у MinIO/S3.
# Інакше підуть локально в ./mlruns
DEFAULT_LOCAL_ARTIFACT_ROOT = f"file://{Path.cwd().joinpath('mlruns').resolve()}"
MLFLOW_ARTIFACT_URI = os.getenv("MLFLOW_ARTIFACT_URI", DEFAULT_LOCAL_ARTIFACT_ROOT)

# Ім’я експерименту можна змінити через ENV, інакше — дефолтне
EXPERIMENT_NAME = os.getenv("MLFLOW_EXPERIMENT_NAME", "Iris_Experiments")

# Pushgateway
PUSHGATEWAY_URL = os.getenv("PUSHGATEWAY_URL", "http://localhost:9091")


# ----------------------------
# Helpers
# ----------------------------
def get_or_create_experiment(name: str, desired_artifact_root: str) -> str:
    """
    Повертає experiment_id. Якщо існуючий експеримент має інший artifact_location,
    створює новий з суфіксом `-v2` (щоб обійти read-only /mlruns тощо).
    """
    client = MlflowClient()
    exp = client.get_experiment_by_name(name)
    if exp is None:
        return client.create_experiment(name, artifact_location=desired_artifact_root)

    # MLflow не дозволяє змінити artifact_location у вже створеного експерименту.
    # Якщо він «чужий» — створимо новий з суфіксом.
    current_loc = (exp.artifact_location or "").strip()
    if not current_loc.startswith(desired_artifact_root):
        alt_name = f"{name}-v2"
        exp2 = client.get_experiment_by_name(alt_name)
        if exp2 is None:
            return client.create_experiment(alt_name, artifact_location=desired_artifact_root)
        return exp2.experiment_id

    return exp.experiment_id


def push_metrics_to_pushgateway(run_id: str, accuracy: float, loss: float) -> None:
    registry = CollectorRegistry()
    g_acc = Gauge("mlflow_accuracy", "Model accuracy", ["run_id"], registry=registry)
    g_loss = Gauge("mlflow_loss", "Model loss", ["run_id"], registry=registry)
    g_acc.labels(run_id=run_id).set(accuracy)
    g_loss.labels(run_id=run_id).set(loss)

    # якщо pushgateway недоступний — просто попереджаємо, але не валимо скрипт
    try:
        push_to_gateway(PUSHGATEWAY_URL, job="mlflow-job", registry=registry)
    except Exception as e:
        print(f"[WARN] Pushgateway push failed: {e}")


def ensure_dir(p: Path) -> None:
    p.mkdir(parents=True, exist_ok=True)


# ----------------------------
# Main
# ----------------------------
def main():
    # 1) MLflow tracking
    mlflow.set_tracking_uri(MLFLOW_TRACKING_URI)

    # 2) Визначаємо/створюємо експеримент з коректним artifact root
    exp_id = get_or_create_experiment(EXPERIMENT_NAME, MLFLOW_ARTIFACT_URI)
    exp = MlflowClient().get_experiment(exp_id)
    mlflow.set_experiment(exp.name)
    print(f"[INFO] Using experiment: {exp.name} (id={exp_id})")
    print(f"[INFO] artifact_location: {exp.artifact_location}")

    # 3) Дані
    X, y = load_iris(return_X_y=True)
    X_train, X_test, y_train, y_test = train_test_split(
        X, y, test_size=0.2, random_state=42
    )

    # 4) Параметри перебору
    learning_rates = [0.01, 0.05, 0.1]
    epochs = [100, 300]

    best_accuracy = -1.0
    best_model_obj = None

    # 5) Запуски
    for lr in learning_rates:
        for ep in epochs:
            with mlflow.start_run() as run:
                run_id = run.info.run_id

                clf = SGDClassifier(
                    loss="log_loss",
                    learning_rate="constant",
                    eta0=lr,
                    max_iter=ep,
                    random_state=42,
                )
                clf.fit(X_train, y_train)

                acc = float(clf.score(X_test, y_test))
                loss = float(1.0 - acc)

                # Логуємо
                mlflow.log_param("learning_rate", lr)
                mlflow.log_param("epochs", ep)
                mlflow.log_metric("accuracy", acc)
                mlflow.log_metric("loss", loss)

                # Зберігаємо модель як артефакт
                model_path = Path(f"model_lr{lr}_ep{ep}.pkl")
                joblib.dump(clf, model_path)
                mlflow.log_artifact(str(model_path))

                print(f"[RUN {run_id}] acc={acc:.4f}, loss={loss:.4f}")

                # Метрики в Pushgateway
                push_metrics_to_pushgateway(run_id, acc, loss)

                # Трек кращої моделі
                if acc > best_accuracy:
                    best_accuracy = acc
                    best_model_obj = clf

    # 6) Копія найкращої моделі в best_model/
    if best_model_obj is not None:
        best_dir = Path("best_model")
        ensure_dir(best_dir)
        best_file = best_dir / "best_model.pkl"
        joblib.dump(best_model_obj, best_file)
        print(f"[INFO] Best model saved to: {best_file.resolve()}")
    else:
        print("[WARN] No model was trained — nothing to save.")

    print(f"[INFO] Best accuracy: {best_accuracy:.4f}")


if __name__ == "__main__":
    main()
