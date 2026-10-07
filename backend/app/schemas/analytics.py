from pydantic import BaseModel

class AnalyticsOut(BaseModel):
    total_scans: int
    safe: int
    suspicious: int
    phishing: int
    average_risk: float
    risk_buckets: list[dict]
    timeline: list[dict]
