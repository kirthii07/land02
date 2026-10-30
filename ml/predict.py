import joblib
import numpy as np
from pathlib import Path


BASE_DIR = Path(__file__).resolve().parent.parent
MODEL_PATH = BASE_DIR / "models" / "landslide_model.pkl"


_model = None


def load_model():
    global _model

    if _model is None:
        try:
            if MODEL_PATH.exists():
                _model = joblib.load(MODEL_PATH)
        except Exception:
            _model = None

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

    if model is not None:
        try:
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
        except Exception:
            pass

    # Heuristic fallback if model binary is unavailable
    risk_score = (
        (float(rain_24h or 0) > 80) or
        (float(soil_moisture or 0) > 75) or
        (float(tilt or 0) > 5)
    )
    return {
        "prediction": 1 if risk_score else 0,
        "probability": 0.85 if risk_score else 0.20,
        "label": "LANDSLIDE RISK" if risk_score else "NO LANDSLIDE RISK"
    }
