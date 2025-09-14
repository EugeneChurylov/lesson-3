import os, time, json, joblib

os.makedirs("model", exist_ok=True)

artifact = {
    "trained_at": time.time(),
    "algo": "mock-sum",
    "note": "this is a placeholder model artifact"
}
joblib.dump(artifact, "model/model.pkl")
print(json.dumps({"status": "trained", "path": "model/model.pkl"}))
