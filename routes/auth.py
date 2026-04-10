from flask import Blueprint, jsonify, request
from flask_jwt_extended import create_access_token, create_refresh_token
from marshmallow import ValidationError

from errors import api_error, validation_error_from_messages
from models import User, bcrypt, db
from routes.models import (
    AuthTokensResponseSchema,
    LoginRequestSchema,
    RegisterRequestSchema,
    UserResponseSchema,
)
from validation import get_json_body

auth_bp = Blueprint("auth", __name__)
register_request_schema = RegisterRequestSchema()
login_request_schema = LoginRequestSchema()
user_response_schema = UserResponseSchema()
auth_tokens_response_schema = AuthTokensResponseSchema()


@auth_bp.route("/register", methods=["POST"])
def register():
    data, err = get_json_body(request)
    if err:
        return err

    try:
        payload = register_request_schema.load(data)
    except ValidationError as err:
        return validation_error_from_messages(err.messages)

    email_norm = payload["email"].strip().lower()

    if User.query.filter_by(email=email_norm).first():
        return api_error("ConflictError", "email is already registered", 409)

    user = User(
        name=payload["name"].strip(),
        email=email_norm,
        password_hash=bcrypt.generate_password_hash(payload["password"]).decode("utf-8"),
    )
    db.session.add(user)
    db.session.commit()

    return jsonify(user_response_schema.dump(user)), 201


@auth_bp.route("/login", methods=["POST"])
def login():
    data, err = get_json_body(request)
    if err:
        return err

    try:
        payload = login_request_schema.load(data)
    except ValidationError as err:
        return validation_error_from_messages(err.messages)

    email_norm = payload["email"].strip().lower()

    user = User.query.filter_by(email=email_norm).first()
    if not user or not bcrypt.check_password_hash(user.password_hash, payload["password"]):
        return api_error(
            "UnauthorizedError", "invalid email or password", 401
        )

    access = create_access_token(identity=str(user.id))
    refresh = create_refresh_token(identity=str(user.id))
    response = {
        "access_token": access,
        "refresh_token": refresh,
        "user": user,
    }
    return jsonify(auth_tokens_response_schema.dump(response)), 200
