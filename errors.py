from flask import jsonify


def validation_error(message: str, status_code: int = 400):
    return jsonify({"error": "ValidationError", "message": message}), status_code


def api_error(error: str, message: str, status_code: int):
    return jsonify({"error": error, "message": message}), status_code
