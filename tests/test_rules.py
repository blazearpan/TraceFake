from backend.app.services.rules import evaluate_rules
from backend.app.services.url_features import extract_features

def test_keyword_alone_is_not_high_risk():
    result = evaluate_rules(extract_features("https://example.com/login"))
    assert result.score < 30

def test_ip_and_at_symbol_raise_score():
    result = evaluate_rules(extract_features("http://192.168.1.10@evil.example/login"))
    assert result.score >= 30
