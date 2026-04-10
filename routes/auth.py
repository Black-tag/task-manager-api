from flask import Blueprint, jsonify, request
from flask_jwt_extended import create_access_token, create_refresh_token

from errors import api_error, validation_error
from models import User, bcrypt, db
from validation import get_json_body, require_str, valid_email

auth_bp = Blueprint("auth", __name__)


@auth_bp.route("/register", methods=["POST"])
def register():
    data, err = get_json_body(request)
    if err:
        return err

    name, msg = require_str(data, "name", max_len=100)
    if msg:
        return validation_error(msg)

    email_raw, msg = require_str(data, "email", max_len=100)
    if msg:
        return validation_error(msg)
    email_norm = email_raw.lower()
    if not valid_email(email_norm):
        return validation_error("email is invalid")

    password, msg = require_str(data, "password", max_len=72)
    if msg:
        return validation_error(msg)

    if User.query.filter_by(email=email_norm).first():
        return api_error("ConflictError", "email is already registered", 409)

    user = User(
        name=name,
        email=email_norm,
        password_hash=bcrypt.generate_password_hash(password).decode("utf-8"),
    )
    db.session.add(user)
    db.session.commit()

    return jsonify({"id": user.id, "name": user.name, "email": user.email}), 201


@auth_bp.route("/login", methods=["POST"])
def login():
    data, err = get_json_body(request)
    if err:
        return err

    email_raw, msg = require_str(data, "email", max_len=100)
    if msg:
        return validation_error(msg)
    email_norm = email_raw.lower()
    if not valid_email(email_norm):
        return validation_error("email is invalid")

    password, msg = require_str(data, "password", max_len=72)
    if msg:
        return validation_error(msg)

    user = User.query.filter_by(email=email_norm).first()
    if not user or not bcrypt.check_password_hash(user.password_hash, password):
        return api_error(
            "UnauthorizedError", "invalid email or password", 401
        )

    access = create_access_token(identity=str(user.id))
    refresh = create_refresh_token(identity=str(user.id))
    return jsonify(access_token=access, refresh_token=refresh), 200
