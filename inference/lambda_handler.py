import json
import os

import joblib
import pandas as pd

BASE_DIR = os.path.dirname(__file__)
MODEL_PATH = os.path.join(BASE_DIR, "personality_model.joblib")
META_PATH = os.path.join(BASE_DIR, "metadata.json")

_model = None
_metadata = None


def _load_artifacts():
    global _model, _metadata
    if _model is None:
        _model = joblib.load(MODEL_PATH)
    if _metadata is None:
        with open(META_PATH, "r", encoding="utf-8") as f:
            _metadata = json.load(f)
    return _model, _metadata


def _normalize_record(record, features):
    missing = [f for f in features if f not in record]
    if missing:
        raise ValueError(f"Missing fields: {', '.join(missing)}")
    return {f: record.get(f) for f in features}


def handler(event, context):
    try:
        model, metadata = _load_artifacts()
        features = metadata["features"]

        body = event.get("body", event)
        if isinstance(body, str):
            body = json.loads(body)

        if isinstance(body, dict) and "records" in body:
            records = body["records"]
        else:
            records = [body]

        rows = [_normalize_record(record, features) for record in records]
        df = pd.DataFrame(rows)

        proba = model.predict_proba(df)
        classes = model.classes_.tolist() if hasattr(model, "classes_") else metadata["classes"]
        preds = [classes[int(i)] for i in proba.argmax(axis=1)]

        results = [
            {"prediction": pred, "probability": float(proba[idx].max())}
            for idx, pred in enumerate(preds)
        ]

        return {
            "statusCode": 200,
            "headers": {"Content-Type": "application/json"},
            "body": json.dumps({"results": results if len(results) > 1 else results[0]})
        }
    except Exception as exc:
        return {
            "statusCode": 400,
            "headers": {"Content-Type": "application/json"},
            "body": json.dumps({"error": str(exc)})
        }
