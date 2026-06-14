"""Loads the trained Decision Tree and exposes classify_code()."""
import os
import sys #
import joblib
import numpy as np

#
ROOT_DIR = os.path.abspath(os.path.join(os.path.dirname(__file__), "..", ".."))
if ROOT_DIR not in sys.path:
    sys.path.insert(0, ROOT_DIR)
#

from ML.feature_extractor import extract_features, FEATURE_ORDER  # type: ignore

_MODEL_PATH = os.path.join(os.path.dirname(__file__), "..", "..", "ML", "logic_classifier.pkl")
_model = None
_labels = None


def _load():
    global _model, _labels
    if _model is None:
        bundle = joblib.load(_MODEL_PATH)
        _model = bundle["model"]
        _labels = bundle["labels"]
    return _model, _labels


def classify_code(code: str):
    model, labels = _load()
    feats = extract_features(code)
    x = np.array([[feats[k] for k in FEATURE_ORDER]])
    pred_idx = int(model.predict(x)[0])
    proba = model.predict_proba(x)[0]
    confidence = float(np.max(proba))
    return {
        "logic_type": labels[pred_idx],
        "confidence": round(confidence, 4),
        "features": feats,
    }
