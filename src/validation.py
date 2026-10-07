from urllib.parse import urlparse
from pydantic import BaseModel, Field, field_validator

MAX_URL_LENGTH = 2048


class URLRequest(BaseModel):
    url: str = Field(..., min_length=1, max_length=MAX_URL_LENGTH)

    @field_validator("url")
    @classmethod
    def validate_url(cls, value: str) -> str:
        value = value.strip()
        parsed = urlparse(value)
        if parsed.scheme.lower() not in {"http", "https"}:
            raise ValueError("URL must begin with http:// or https://")
        if not parsed.hostname:
            raise ValueError("URL must contain a valid hostname")
        if any(control in value for control in ["\n", "\r", "\x00"]):
            raise ValueError("URL contains prohibited control characters")
        return value
