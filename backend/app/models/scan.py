from datetime import datetime, timezone
from sqlalchemy import String, Integer, Float, DateTime, ForeignKey, Text
from sqlalchemy.orm import Mapped, mapped_column, relationship
from backend.app.database.session import Base

class Scan(Base):
    __tablename__ = "scans"
    id: Mapped[int] = mapped_column(Integer, primary_key=True, index=True)
    url: Mapped[str] = mapped_column(Text, nullable=False)
    timestamp: Mapped[datetime] = mapped_column(DateTime, default=lambda: datetime.now(timezone.utc), index=True)
    classification: Mapped[str] = mapped_column(String(20), nullable=False)
    risk_score: Mapped[float] = mapped_column(Float, nullable=False)
    ml_score: Mapped[float] = mapped_column(Float, nullable=False)
    rule_score: Mapped[float] = mapped_column(Float, nullable=False)
    reputation_status: Mapped[str] = mapped_column(String(80), default="Not configured")
    model_name: Mapped[str] = mapped_column(String(120), default="Not available")
    model_version: Mapped[str] = mapped_column(String(80), default="Not available")
    features = relationship("ScanFeature", cascade="all, delete-orphan", back_populates="scan")
    reasons = relationship("DetectionReason", cascade="all, delete-orphan", back_populates="scan")

class ScanFeature(Base):
    __tablename__ = "scan_features"
    id: Mapped[int] = mapped_column(Integer, primary_key=True)
    scan_id: Mapped[int] = mapped_column(ForeignKey("scans.id", ondelete="CASCADE"), index=True)
    feature_name: Mapped[str] = mapped_column(String(120), nullable=False)
    feature_value: Mapped[str] = mapped_column(String(500), nullable=False)
    risk_level: Mapped[str] = mapped_column(String(20), nullable=False)
    scan = relationship("Scan", back_populates="features")

class DetectionReason(Base):
    __tablename__ = "detection_reasons"
    id: Mapped[int] = mapped_column(Integer, primary_key=True)
    scan_id: Mapped[int] = mapped_column(ForeignKey("scans.id", ondelete="CASCADE"), index=True)
    reason_code: Mapped[str] = mapped_column(String(100), nullable=False)
    description: Mapped[str] = mapped_column(Text, nullable=False)
    severity: Mapped[str] = mapped_column(String(20), nullable=False)
    source: Mapped[str] = mapped_column(String(30), nullable=False)
    scan = relationship("Scan", back_populates="reasons")
