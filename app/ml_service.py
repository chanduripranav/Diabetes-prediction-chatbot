from pathlib import Path
import joblib

MODEL_PATH = Path("models/diabetes_knn.pkl")

_model = None
_feature_names = None

def load_model():
    global _model, _feature_names
    obj = joblib.load(MODEL_PATH)
    _model = obj["pipeline"]
    _feature_names = obj["feature_names"]
    print("Model loaded!")

def predict(features: dict):
    x = [[features[name] for name in _feature_names]]
    prob = float(_model.predict_proba(x)[0][1])
    label = int(prob >= 0.5)

    return {
        "prediction": label,
        "probability": prob
    }
