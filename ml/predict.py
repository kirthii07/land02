import joblib
import numpy as np
from pathlib import Path


BASE_DIR = Path(__file__).resolve().parent.parent
MODEL_PATH = BASE_DIR / "models" / "landslide_model.pkl"


_model = None


def load_model():
    global _model

    if _model is None:
        _model = joblib.load(MODEL_PATH)

    return _model


def predict_landslide(
    rain_24h,
    rain_48h,
    rain_72h,
    rain_96h,
    soil_moisture,
    tilt
):

    model = load_model()

    features = np.array([[
        rain_24h,
        rain_48h,
        rain_72h,
        rain_96h,
        soil_moisture,
        tilt
    ]])

    prediction = int(model.predict(features)[0])

    probability = None

    if hasattr(model, "predict_proba"):
        probabilities = model.predict_proba(features)[0]
        probability = float(np.max(probabilities))

    return {
        "prediction": prediction,
        "probability": probability,
        "label": (
            "LANDSLIDE RISK"
            if prediction == 1
            else "NO LANDSLIDE RISK"
        )
    }