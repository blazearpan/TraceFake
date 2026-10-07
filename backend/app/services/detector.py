from urllib.parse import urlsplit
from backend.app.core.config import settings
from backend.app.services.url_features import extract_features
from backend.app.services.rules import evaluate_rules
from backend.app.services.model_manager import MODEL_MANAGER

def validate_url(raw: str):
    value = raw.strip()

    if not value:
        raise ValueError("Please enter a URL.")

    if len(value) > settings.max_url_length:
        raise ValueError("The URL is too long for safe analysis.")

    candidate = value if "://" in value else "https://" + value
    parsed = urlsplit(candidate)

    if parsed.scheme.lower() not in {"http", "https"} or not parsed.hostname:
        raise ValueError("Please enter a valid HTTP or HTTPS URL.")

    hostname = parsed.hostname

    if any(char.isspace() for char in hostname):
        raise ValueError("Please enter a valid HTTP or HTTPS URL.")

    if "." not in hostname and hostname.lower() != "localhost":
        raise ValueError("Please enter a valid HTTP or HTTPS URL.")

    return candidate

def classify(score: float) -> str:
    if score < settings.safe_threshold:
        return "SAFE"
    if score < settings.phishing_threshold:
        return "SUSPICIOUS"
    return "PHISHING"

def recommendations(classification: str, reasons: list[dict]):
    if classification == "PHISHING":
        return [
            "Do not enter passwords, payment information, or authentication codes.",
            "Do not download files from the destination unless independently verified.",
            "Verify the domain through a trusted source before interacting with it.",
        ]
    if classification == "SUSPICIOUS":
        return [
            "Treat the URL with caution and verify the domain independently.",
            "Avoid entering sensitive information until the destination is verified.",
        ]
    return [
        "No strong phishing indicators were detected by the current model and rules.",
        "A SAFE result is not a guarantee that the destination is harmless.",
    ]

def analyze_url(raw_url: str):
    url = validate_url(raw_url)
    features = extract_features(url)
    rule_result = evaluate_rules(features)
    ml_result = MODEL_MANAGER.predict(features)

    if ml_result is None:
        ml_score = 0.0
        risk_score = rule_result.score
        model_name = "Not available"
        model_version = "Not trained"
    else:
        ml_score = ml_result["phishing_score"]
        risk_score = (settings.ml_weight * ml_score) + (settings.rule_weight * rule_result.score)
        model_name = ml_result["model_name"]
        model_version = ml_result["model_version"]

    risk_score = round(max(0.0, min(100.0, risk_score)), 2)
    classification = classify(risk_score)

    # ML-only prediction is an additional factual signal; it is not used to invent reasons.
    reasons = list(rule_result.reasons)
    if ml_result is not None:
        ml_label = "phishing-oriented" if ml_result["prediction"] == 1 else "legitimate-oriented"
        reasons.append({
            "code": "ML_SIGNAL",
            "description": f"The trained {model_name} model produced a {ml_label} prediction for the extracted URL features.",
            "severity": "Medium" if ml_result["prediction"] == 1 else "Low",
            "source": "ML",
        })

    feature_output = []
    for name, value in features.items():
        feature_output.append({
            "name": name,
            "value": str(value),
            "risk": rule_result.feature_risk.get(name, "Low"),
        })

    return {
        "url": url,
        "classification": classification,
        "risk_score": risk_score,
        "ml_score": round(ml_score, 2),
        "rule_score": round(rule_result.score, 2),
        "reputation_status": "Not configured",
        "model_name": model_name,
        "model_version": model_version,
        "features": feature_output,
        "reasons": reasons,
        "recommendations": recommendations(classification, reasons),
        "model_ready": MODEL_MANAGER.ready,
    }
