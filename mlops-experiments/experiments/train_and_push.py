import os
import time
import joblib
import mlflow
import mlflow.sklearn
import numpy as np
from sklearn.datasets import load_iris
from sklearn.linear_model import SGDClassifier
from sklearn.model_selection import train_test_split
from prometheus_client import CollectorRegistry, Gauge, push_to_gateway

MLFLOW_TRACKING_URI = os.getenv("MLFLOW_TRACKING_URI", "http://localhost:5000")
PUSHGATEWAY_URL = os.getenv("PUSHGATEWAY_URL", "http://localhost:9091")

mlflow.set_tracking_uri(MLFLOW_TRACKING_URI)
mlflow.set_experiment("Iris_Experiments")

X, y = load_iris(return_X_y=True)
X_train, X_test, y_train, y_test = train_test_split(X, y, test_size=0.2, random_state=42)

learning_rates = [0.01, 0.05, 0.1]
epochs = [100, 300]

best_accuracy = -1.0
best_run_id = None

for lr in learning_rates:
    for ep in epochs:
        with mlflow.start_run() as run:
            clf = SGDClassifier(
                loss="log_loss",
                learning_rate="constant",
                eta0=lr,
                max_iter=ep,
                random_state=42,
            )
            clf.fit(X_train, y_train)
            acc = clf.score(X_test, y_test)
            loss = 1 - acc

            mlflow.log_param("learning_rate", lr)
            mlflow.log_param("epochs", ep)
            mlflow.log_metric("accuracy", acc)
            mlflow.log_metric("loss", loss)

            # збереження моделі як артефакт
            model_path = f"model_{lr}_{ep}.pkl"
            joblib.dump(clf, model_path)
            mlflow.log_artifact(model_path)

            print(f"Run {run.info.run_id}: acc={acc:.4f}, loss={loss:.4f}")

            # пуш у pushgateway
            registry = CollectorRegistry()
            g_acc = Gauge("mlflow_accuracy", "Model accuracy", ["run_id"], registry=registry)
            g_loss = Gauge("mlflow_loss", "Model loss", ["run_id"], registry=registry)
            g_acc.labels(run_id=run.info.run_id).set(acc)
            g_loss.labels(run_id=run.info.run_id).set(loss)

            push_to_gateway(PUSHGATEWAY_URL, job="mlflow-job", registry=registry)

            if acc > best_accuracy:
                best_accuracy = acc
                best_run_id = run.info.run_id
                best_model_path = "best_model.pkl"
                joblib.dump(clf, best_model_path)
                mlflow.log_artifact(best_model_path, artifact_path="best_model")

print(f"Best run: {best_run_id} with accuracy={best_accuracy:.4f}")
