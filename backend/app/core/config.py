from pathlib import Path
from pydantic_settings import BaseSettings, SettingsConfigDict

BASE_DIR = Path(__file__).resolve().parents[3]

class Settings(BaseSettings):
    app_name: str = "TraceFake"
    database_url: str = f"sqlite:///{BASE_DIR / 'tracefake.db'}"
    model_path: str = str(BASE_DIR / "ml" / "trained_models" / "tracefake_model.joblib")
    metadata_path: str = str(BASE_DIR / "ml" / "trained_models" / "metadata.json")
    reports_dir: str = str(BASE_DIR / "reports")
    ml_weight: float = 0.65
    rule_weight: float = 0.35
    safe_threshold: int = 30
    phishing_threshold: int = 70
    max_url_length: int = 4096
    cors_origins: str = "http://localhost:5173,http://127.0.0.1:5173"

    model_config = SettingsConfigDict(env_file=".env", extra="ignore")

settings = Settings()
Path(settings.reports_dir).mkdir(parents=True, exist_ok=True)
