import ipaddress
import math
import re
from collections import Counter
from urllib.parse import urlsplit, parse_qsl, unquote

SUSPICIOUS_KEYWORDS = {
    "login", "signin", "verify", "verification", "secure", "account",
    "update", "password", "bank", "payment", "wallet", "confirm", "security"
}
SHORTENER_DOMAINS = {
    "bit.ly", "tinyurl.com", "t.co", "is.gd", "ow.ly", "buff.ly",
    "cutt.ly", "rebrand.ly", "shorturl.at", "tiny.one"
}

def shannon_entropy(value: str) -> float:
    if not value:
        return 0.0
    counts = Counter(value)
    n = len(value)
    return -sum((c/n) * math.log2(c/n) for c in counts.values())

def _safe_parts(url: str):
    parsed = urlsplit(url)
    host = (parsed.hostname or "").lower()
    domain_parts = host.split(".") if host else []
    subdomain_count = max(0, len(domain_parts) - 2) if host and not _is_ip(host) else 0
    return parsed, host, domain_parts, subdomain_count

def _is_ip(host: str) -> bool:
    try:
        ipaddress.ip_address(host)
        return True
    except ValueError:
        return False

def extract_features(url: str) -> dict:
    parsed, host, domain_parts, subdomain_count = _safe_parts(url)
    raw = url
    decoded = unquote(raw)
    path = parsed.path or ""
    query = parsed.query or ""
    query_params = parse_qsl(query, keep_blank_values=True)
    special_chars = sum(not ch.isalnum() for ch in raw)
    digit_count = sum(ch.isdigit() for ch in raw)
    hyphens = raw.count("-")
    underscores = raw.count("_")
    dots = raw.count(".")
    slash_count = raw.count("/")
    keyword_hits = sorted(k for k in SUSPICIOUS_KEYWORDS if re.search(rf"(?<![a-z]){re.escape(k)}(?![a-z])", decoded.lower()))
    encoded_count = len(re.findall(r"%[0-9a-fA-F]{2}", raw))
    repeated_separator = bool(re.search(r"([./_-])\1{2,}", raw))
    entropy = shannon_entropy(host)
    tld = domain_parts[-1] if len(domain_parts) >= 2 else ""
    return {
        "url_length": len(raw),
        "domain_length": len(host),
        "path_length": len(path),
        "query_length": len(query),
        "dot_count": dots,
        "hyphen_count": hyphens,
        "underscore_count": underscores,
        "digit_count": digit_count,
        "special_character_count": special_chars,
        "slash_count": slash_count,
        "subdirectory_count": max(0, len([p for p in path.split("/") if p])),
        "subdomain_count": subdomain_count,
        "query_parameter_count": len(query_params),
        "uses_https": int(parsed.scheme.lower() == "https"),
        "has_ip_hostname": int(_is_ip(host)),
        "has_at_symbol": int("@" in raw),
        "has_punycode": int("xn--" in host),
        "has_url_encoding": int(encoded_count > 0),
        "encoded_character_count": encoded_count,
        "has_shortener": int(host in SHORTENER_DOMAINS),
        "suspicious_keyword_count": len(keyword_hits),
        "has_suspicious_keyword": int(bool(keyword_hits)),
        "character_entropy": round(shannon_entropy(raw), 6),
        "domain_entropy": round(entropy, 6),
        "digit_ratio": round(digit_count / max(1, len(raw)), 6),
        "special_character_ratio": round(special_chars / max(1, len(raw)), 6),
        "has_repeated_separators": int(repeated_separator),
        "tld_length": len(tld),
    }

FEATURE_NAMES = list(extract_features("https://example.com/").keys())

def feature_rows(features: dict):
    return [{"name": k, "value": str(v)} for k, v in features.items()]
