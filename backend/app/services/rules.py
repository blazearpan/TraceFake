from dataclasses import dataclass
from backend.app.services.url_features import SUSPICIOUS_KEYWORDS

@dataclass
class RuleResult:
    score: float
    reasons: list[dict]
    feature_risk: dict[str, str]

def evaluate_rules(features: dict) -> RuleResult:
    score = 0.0
    reasons = []
    risk = {name: "Low" for name in features}

    def add(code, description, points, severity, feature=None):
        nonlocal score
        score += points
        reasons.append({
            "code": code,
            "description": description,
            "severity": severity,
            "source": "Rule",
        })
        if feature:
            risk[feature] = severity

    if features["has_ip_hostname"]:
        add("IP_HOST", "An IP address is used as the hostname instead of a conventional domain.", 28, "High", "has_ip_hostname")
    if features["has_at_symbol"]:
        add("AT_SYMBOL", "The URL contains an @ symbol, which can obscure the apparent destination.", 18, "High", "has_at_symbol")
    if features["has_punycode"]:
        add("PUNYCODE", "The hostname contains Punycode/IDN notation.", 12, "Medium", "has_punycode")
    if features["has_shortener"]:
        add("SHORTENER", "A known URL-shortening hostname was detected.", 12, "Medium", "has_shortener")
    if features["url_length"] >= 120:
        add("LONG_URL", "The URL is unusually long.", 12, "Medium", "url_length")
    elif features["url_length"] >= 80:
        add("LONG_URL_MODERATE", "The URL is relatively long.", 6, "Low", "url_length")
    if features["subdomain_count"] >= 4:
        add("SUBDOMAIN_DEPTH", "The URL contains multiple subdomain levels.", 14, "Medium", "subdomain_count")
    elif features["subdomain_count"] >= 2:
        add("SUBDOMAIN_DEPTH_MODERATE", "The URL contains several subdomain levels.", 6, "Low", "subdomain_count")
    if features["suspicious_keyword_count"] >= 3:
        add("KEYWORDS_MANY", "Several security or account-related keywords occur in the URL.", 14, "Medium", "suspicious_keyword_count")
    elif features["suspicious_keyword_count"] >= 1:
        add("KEYWORD", "A security or account-related keyword occurs in the URL.", 4, "Low", "suspicious_keyword_count")
    if features["has_url_encoding"] and features["encoded_character_count"] >= 5:
        add("ENCODING", "The URL contains multiple percent-encoded characters.", 8, "Medium", "encoded_character_count")
    if features["has_repeated_separators"]:
        add("REPEATED_SEPARATORS", "The URL contains repeated separator characters.", 8, "Medium", "has_repeated_separators")
    if features["special_character_ratio"] > 0.25:
        add("SPECIAL_RATIO", "A relatively high proportion of the URL consists of special characters.", 8, "Medium", "special_character_ratio")
    if features["domain_entropy"] >= 3.5:
        add("DOMAIN_ENTROPY", "The hostname has relatively high character entropy.", 6, "Low", "domain_entropy")
    if features["uses_https"]:
        reasons.append({"code": "HTTPS", "description": "HTTPS is enabled for the submitted URL.", "severity": "Low", "source": "Rule"})
        risk["uses_https"] = "Low"
    else:
        add("NO_HTTPS", "HTTPS is not enabled.", 10, "Medium", "uses_https")

    return RuleResult(min(100.0, score), reasons, risk)
