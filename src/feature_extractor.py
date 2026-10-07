"""Static URL feature extraction. URLs are never opened or requested."""
import ipaddress
import re
from urllib.parse import urlparse

SUSPICIOUS_WORDS = {
    "login", "signin", "verify", "verification", "secure", "account",
    "update", "confirm", "password", "bank", "payment", "wallet",
    "bonus", "prize", "urgent", "unlock", "recovery", "authenticate",
}

FEATURE_NAMES = [
    "url_length", "hostname_length", "path_length", "has_https",
    "has_ip_address", "num_dots", "num_hyphens", "num_special_chars",
    "num_subdomains", "has_at_symbol", "has_double_slash_path",
    "suspicious_word_count", "has_punycode", "query_length",
]


def _is_ip(hostname: str) -> int:
    try:
        ipaddress.ip_address(hostname)
        return 1
    except ValueError:
        return 0


def extract_features(url: str) -> dict[str, float]:
    parsed = urlparse(url)
    hostname = parsed.hostname or ""
    path = parsed.path or ""
    lowered = url.lower()
    words = set(re.findall(r"[a-z0-9]+", lowered))
    special_chars = sum(1 for char in url if char in "@#$%^&*_=+~|;,")
    dot_count = hostname.count(".")
    subdomains = max(0, dot_count - 1) if not _is_ip(hostname) else 0
    return {
        "url_length": len(url),
        "hostname_length": len(hostname),
        "path_length": len(path),
        "has_https": int(parsed.scheme.lower() == "https"),
        "has_ip_address": _is_ip(hostname),
        "num_dots": dot_count,
        "num_hyphens": url.count("-"),
        "num_special_chars": special_chars,
        "num_subdomains": subdomains,
        "has_at_symbol": int("@" in url),
        "has_double_slash_path": int("//" in path),
        "suspicious_word_count": len(words.intersection(SUSPICIOUS_WORDS)),
        "has_punycode": int("xn--" in hostname.lower()),
        "query_length": len(parsed.query),
    }


def feature_vector(url: str):
    features = extract_features(url)
    return [features[name] for name in FEATURE_NAMES]
