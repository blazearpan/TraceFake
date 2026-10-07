from backend.app.services.url_features import extract_features

def test_feature_extraction_is_deterministic():
    url = "https://example.com/login?verify=true"
    a = extract_features(url)
    b = extract_features(url)
    assert a == b
    assert a["uses_https"] == 1
    assert a["has_suspicious_keyword"] == 1

def test_ip_detection():
    f = extract_features("http://192.168.1.10/login")
    assert f["has_ip_hostname"] == 1

def test_punycode_detection():
    f = extract_features("https://xn--example-dk9c.com/")
    assert f["has_punycode"] == 1
