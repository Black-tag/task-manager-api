import re
from typing import Any

from errors import validation_error

EMAIL_RE = re.compile(r"^[^@\s]+@[^@\s]+\.[^@\s]+$")


def get_json_body(request):
    data = request.get_json(silent=True)
    if data is None:
        return None, validation_error("JSON body is required")
    if not isinstance(data, dict):
        return None, validation_error("JSON body must be an object")
    return data, None


def require_str(data: dict, key: str, *, max_len: int | None = None):
    val = data.get(key)
    if val is None:
        return None, f"{key} is required"
    if not isinstance(val, str):
        return None, f"{key} must be a string"
    s = val.strip()
    if not s:
        return None, f"{key} is required"
    if max_len is not None and len(s) > max_len:
        return None, f"{key} must be at most {max_len} characters"
    return s, None


def valid_email(email: str) -> bool:
    return bool(EMAIL_RE.match(email))


def require_enum(data: dict, key: str, allowed: set[str]):
    val: Any = data.get(key)
    if val is None:
        return None, f"{key} is required"
    if not isinstance(val, str):
        return None, f"{key} must be a string"
    if val not in allowed:
        allowed_str = ", ".join(sorted(allowed))
        return None, f"{key} must be one of: {allowed_str}"
    return val, None
