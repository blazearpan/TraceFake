from backend.app.services.detector import classify, validate_url

def test_thresholds():
    assert classify(0) == "SAFE"
    assert classify(29.99) == "SAFE"
    assert classify(30) == "SUSPICIOUS"
    assert classify(69.99) == "SUSPICIOUS"
    assert classify(70) == "PHISHING"

def test_url_validation_adds_scheme():
    assert validate_url("example.com").startswith("https://")

def test_invalid_url():
    try:
        validate_url("not a valid url")
    except ValueError:
        assert True
    else:
        assert False
