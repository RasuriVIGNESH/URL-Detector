from src.feature_extractor import extract_features


def test_https_is_detected():
    assert extract_features("https://www.example.com")["has_https"] == 1


def test_ip_address_is_detected():
    assert extract_features("http://192.0.2.10/login")["has_ip_address"] == 1


def test_suspicious_words_are_counted():
    features = extract_features("http://secure-login-verify.example.com")
    assert features["suspicious_word_count"] >= 3
