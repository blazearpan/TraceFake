from pathlib import Path
import json
from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session
from backend.app.database.session import get_db
from backend.app.models.evaluation import ModelEvaluation, ModelFeature
from backend.app.services.model_manager import MODEL_MANAGER
from backend.app.core.config import settings

router = APIRouter(prefix="/api/models", tags=["models"])

@router.get("/status")
def model_status():
    return {
        "ready": MODEL_MANAGER.ready,
        "model_name": MODEL_MANAGER.metadata.get("model_name"),
        "model_version": MODEL_MANAGER.metadata.get("model_version"),
        "metrics": MODEL_MANAGER.metadata.get("test_metrics", {}),
        "comparison": MODEL_MANAGER.metadata.get("model_comparison", []),
        "confusion_matrix": MODEL_MANAGER.metadata.get("confusion_matrix", []),
        "feature_importance": MODEL_MANAGER.metadata.get("feature_importance", []),
        "dataset": MODEL_MANAGER.metadata.get("dataset", {}),
        "methodology": MODEL_MANAGER.metadata.get("selection_method", "No trained model available."),
    }

@router.get("/evaluations")
def evaluations(db: Session = Depends(get_db)):
    return [e.__dict__ | {"_sa_instance_state": None} for e in db.query(ModelEvaluation).all()]
