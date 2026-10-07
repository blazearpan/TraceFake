from datetime import datetime, timezone
from sqlalchemy import String, Integer, Float, DateTime
from sqlalchemy.orm import Mapped, mapped_column
from backend.app.database.session import Base

class ModelEvaluation(Base):
    __tablename__ = "model_evaluations"
    id: Mapped[int] = mapped_column(Integer, primary_key=True)
    model_name: Mapped[str] = mapped_column(String(120), nullable=False)
    dataset_version: Mapped[str] = mapped_column(String(200), nullable=False)
    accuracy: Mapped[float] = mapped_column(Float)
    precision: Mapped[float] = mapped_column(Float)
    recall: Mapped[float] = mapped_column(Float)
    f1_score: Mapped[float] = mapped_column(Float)
    roc_auc: Mapped[float] = mapped_column(Float)
    evaluated_at: Mapped[datetime] = mapped_column(DateTime, default=lambda: datetime.now(timezone.utc))

class ModelFeature(Base):
    __tablename__ = "model_features"
    id: Mapped[int] = mapped_column(Integer, primary_key=True)
    model_name: Mapped[str] = mapped_column(String(120), nullable=False)
    feature_name: Mapped[str] = mapped_column(String(120), nullable=False)
    importance: Mapped[float] = mapped_column(Float, nullable=False)
