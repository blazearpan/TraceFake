from datetime import datetime
from pydantic import BaseModel, Field

class ScanRequest(BaseModel):
    url: str = Field(min_length=1, max_length=4096)

class FeatureOut(BaseModel):
    name: str
    value: str
    risk: str

class ReasonOut(BaseModel):
    code: str
    description: str
    severity: str
    source: str

class ScanOut(BaseModel):
    id: int | None = None
    url: str
    timestamp: datetime | None = None
    classification: str
    risk_score: float
    ml_score: float
    rule_score: float
    reputation_status: str
    model_name: str
    model_version: str
    features: list[FeatureOut]
    reasons: list[ReasonOut]
    recommendations: list[str]
    model_ready: bool
