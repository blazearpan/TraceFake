import json
from pathlib import Path
import joblib
import pandas as pd
from backend.app.core.config import settings
from backend.app.services.url_features import FEATURE_NAMES

class ModelManager:
    def __init__(self):
        self.model = None
        self.metadata = {}
        self.load()

    def load(self):
        model_path = Path(settings.model_path)
        metadata_path = Path(settings.metadata_path)
        if model_path.exists():
            self.model = joblib.load(model_path)
        if metadata_path.exists():
            try:
                self.metadata = json.loads(metadata_path.read_text(encoding="utf-8"))
            except Exception:
                self.metadata = {}

    @property
    def ready(self):
        return self.model is not None

    def predict(self, features: dict):
        if not self.ready:
            return None
        frame = pd.DataFrame([[features.get(name, 0) for name in FEATURE_NAMES]], columns=FEATURE_NAMES)
        prediction = int(self.model.predict(frame)[0])
        if hasattr(self.model, "predict_proba"):
            probabilities = self.model.predict_proba(frame)[0]
            classes = list(self.model.classes_)
            phishing_index = classes.index(1) if 1 in classes else 0
            phishing_score = float(probabilities[phishing_index] * 100)
        else:
            phishing_score = 100.0 if prediction == 1 else 0.0
        return {
            "prediction": prediction,
            "phishing_score": phishing_score,
            "model_name": self.metadata.get("model_name", type(self.model).__name__),
            "model_version": self.metadata.get("model_version", "trained-local"),
        }

MODEL_MANAGER = ModelManager()
