from fastapi import APIRouter, Depends, HTTPException
from fastapi.responses import FileResponse
from sqlalchemy.orm import Session
from sqlalchemy import desc
from backend.app.database.session import get_db
from backend.app.models.scan import Scan, ScanFeature, DetectionReason
from backend.app.schemas.scan import ScanRequest
from backend.app.services.detector import analyze_url
from backend.app.services.reports import generate_pdf

router = APIRouter(prefix="/api/scans", tags=["scans"])

def serialize(scan: Scan):
    return {
        "id": scan.id,
        "url": scan.url,
        "timestamp": scan.timestamp,
        "classification": scan.classification,
        "risk_score": scan.risk_score,
        "ml_score": scan.ml_score,
        "rule_score": scan.rule_score,
        "reputation_status": scan.reputation_status,
        "model_name": scan.model_name,
        "model_version": scan.model_version,
        "features": [{"name": f.feature_name, "value": f.feature_value, "risk": f.risk_level} for f in scan.features],
        "reasons": [{"code": r.reason_code, "description": r.description, "severity": r.severity, "source": r.source} for r in scan.reasons],
        "recommendations": [],
        "model_ready": scan.model_name != "Not available",
    }

@router.post("/analyze")
def analyze(request: ScanRequest, db: Session = Depends(get_db)):
    try:
        result = analyze_url(request.url)
    except ValueError as exc:
        raise HTTPException(status_code=422, detail=str(exc))
    scan = Scan(
        url=result["url"], classification=result["classification"],
        risk_score=result["risk_score"], ml_score=result["ml_score"],
        rule_score=result["rule_score"], reputation_status=result["reputation_status"],
        model_name=result["model_name"], model_version=result["model_version"]
    )
    db.add(scan)
    db.flush()
    for f in result["features"]:
        db.add(ScanFeature(scan_id=scan.id, feature_name=f["name"], feature_value=f["value"], risk_level=f["risk"]))
    for r in result["reasons"]:
        db.add(DetectionReason(scan_id=scan.id, reason_code=r["code"], description=r["description"], severity=r["severity"], source=r["source"]))
    db.commit()
    result["id"] = scan.id
    result["timestamp"] = scan.timestamp
    return result

@router.get("")
def history(limit: int = 100, db: Session = Depends(get_db)):
    rows = db.query(Scan).order_by(desc(Scan.timestamp)).limit(min(max(limit, 1), 500)).all()
    return [serialize(s) for s in rows]

@router.get("/{scan_id}")
def get_scan(scan_id: int, db: Session = Depends(get_db)):
    scan = db.get(Scan, scan_id)
    if not scan:
        raise HTTPException(status_code=404, detail="Scan not found.")
    return serialize(scan)

@router.delete("/{scan_id}")
def delete_scan(scan_id: int, db: Session = Depends(get_db)):
    scan = db.get(Scan, scan_id)
    if not scan:
        raise HTTPException(status_code=404, detail="Scan not found.")
    db.delete(scan)
    db.commit()
    return {"status": "deleted"}

@router.post("/{scan_id}/report")
def report(scan_id: int, db: Session = Depends(get_db)):
    scan = db.get(Scan, scan_id)
    if not scan:
        raise HTTPException(status_code=404, detail="Scan not found.")
    result = serialize(scan)
    path = generate_pdf(result)
    return FileResponse(path, media_type="application/pdf", filename=path.name)
