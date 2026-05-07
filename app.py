import json
from pathlib import Path

import joblib
import pandas as pd
from fastapi import FastAPI, HTTPException
from pydantic import BaseModel

APP_DIR = Path(__file__).parent
MODELS_DIR = APP_DIR / "models"
MODEL_PATH = MODELS_DIR / "personality_model.joblib"
META_PATH = MODELS_DIR / "metadata.json"

app = FastAPI(title="Personality Classifier", version="1.0")


class PredictionRequest(BaseModel):
    Time_spent_Alone: float
    Stage_fear: str
    Social_event_attendance: float
    Going_outside: float
    Drained_after_socializing: str
    Friends_circle_size: float
    Post_frequency: float


@app.on_event("startup")
def load_artifacts():
    if not MODEL_PATH.exists() or not META_PATH.exists():
        raise RuntimeError("Model artifacts not found. Ensure models are copied into the image.")
    app.state.model = joblib.load(MODEL_PATH)
    with META_PATH.open("r", encoding="utf-8") as f:
        app.state.meta = json.load(f)


@app.get("/")
def health():
    return {"status": "ok"}


@app.post("/predict")
def predict(payload: PredictionRequest):
    model = app.state.model
    meta = app.state.meta

    record = payload.dict()
    try:
        df = pd.DataFrame([{k: record[k] for k in meta["features"]}])
    except KeyError as exc:
        raise HTTPException(status_code=400, detail=f"Missing field: {exc}")

    proba = model.predict_proba(df)
    pred = model.classes_[proba.argmax(axis=1)][0]

    return {
        "prediction": pred,
        "probability": float(proba.max())
    }
