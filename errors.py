from flask import jsonify
from typing import Any


def validation_error(message: str, status_code: int = 400):
    return jsonify({"error": "ValidationError", "message": message}), status_code


def api_error(error: str, message: str, status_code: int):
    return jsonify({"error": error, "message": message}), status_code


def validation_error_from_messages(messages: Any):
    return validation_error(_extract_first_message(messages))


def _extract_first_message(value: Any) -> str:
    if isinstance(value, dict):
        for nested in value.values():
            result = _extract_first_message(nested)
            if result:
                return result
    elif isinstance(value, list):
        for nested in value:
            result = _extract_first_message(nested)
            if result:
                return result
    elif isinstance(value, str):
        return value
    return "invalid input"
