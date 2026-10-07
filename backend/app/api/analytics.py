from collections import Counter
from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session
from backend.app.database.session import get_db
from backend.app.models.scan import Scan
from backend.app.schemas.analytics import AnalyticsOut

router = APIRouter(prefix="/api/analytics", tags=["analytics"])

@router.get("", response_model=AnalyticsOut)
def analytics(db: Session = Depends(get_db)):
    rows = db.query(Scan).all()
    counts = Counter(r.classification for r in rows)
    total = len(rows)
    avg = round(sum(r.risk_score for r in rows) / total, 2) if total else 0.0
    buckets = [{"range": label, "count": sum(1 for r in rows if lo <= r.risk_score <= hi)}
               for label, lo, hi in [("0-29",0,29),("30-69",30,69),("70-100",70,100)]]
    timeline_counter = Counter(r.timestamp.date().isoformat() for r in rows if r.timestamp)
    timeline = [{"date": k, "count": timeline_counter[k]} for k in sorted(timeline_counter)]
    return {
        "total_scans": total,
        "safe": counts.get("SAFE", 0),
        "suspicious": counts.get("SUSPICIOUS", 0),
        "phishing": counts.get("PHISHING", 0),
        "average_risk": avg,
        "risk_buckets": buckets,
        "timeline": timeline,
    }
