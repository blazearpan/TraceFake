from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from backend.app.core.config import settings
from backend.app.database.session import init_db
from backend.app.api.scans import router as scans_router
from backend.app.api.analytics import router as analytics_router
from backend.app.api.models import router as models_router

app = FastAPI(title="TraceFake API", version="1.0.0", description="Static phishing URL detection and risk analysis API.")

origins = [x.strip() for x in settings.cors_origins.split(",") if x.strip()]
app.add_middleware(
    CORSMiddleware,
    allow_origins=origins,
    allow_credentials=False,
    allow_methods=["GET", "POST", "DELETE", "OPTIONS"],
    allow_headers=["*"],
)

@app.on_event("startup")
def startup():
    init_db()

@app.get("/")
def root():
    return {"name": "TraceFake", "status": "online", "message": "Trace the Link. Detect the Threat."}

@app.get("/api/health")
def health():
    return {"status": "ok", "service": "TraceFake Detection API"}

app.include_router(scans_router)
app.include_router(analytics_router)
app.include_router(models_router)
