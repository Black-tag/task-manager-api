from flask import Blueprint, jsonify, request
from flask_jwt_extended import get_jwt_identity, jwt_required
from marshmallow import ValidationError

from errors import api_error, validation_error_from_messages
from models import Project, db
from routes.models import (
    MessageResponseSchema,
    ProjectCreateRequestSchema,
    ProjectResponseSchema,
    ProjectUpdateRequestSchema,
)
from validation import get_json_body

projects_bp = Blueprint("projects", __name__)
project_create_request_schema = ProjectCreateRequestSchema()
project_update_request_schema = ProjectUpdateRequestSchema()
project_response_schema = ProjectResponseSchema()
message_response_schema = MessageResponseSchema()


def _current_user_id() -> int | None:
    identity = get_jwt_identity()
    try:
        return int(identity)
    except (TypeError, ValueError):
        return None


@projects_bp.route("", methods=["POST"])
@jwt_required()
def create_project():
    user_id = _current_user_id()
    if user_id is None:
        return api_error("UnauthorizedError", "invalid token identity", 401)

    data, err = get_json_body(request)
    if err:
        return err

    try:
        payload = project_create_request_schema.load(data)
    except ValidationError as err:
        return validation_error_from_messages(err.messages)

    title = payload["title"].strip()
    description = payload.get("description")
    if isinstance(description, str):
        description = description.strip() or None

    project = Project(owner_id=user_id, title=title, description=description)
    db.session.add(project)
    db.session.commit()

    return jsonify(project_response_schema.dump(project)), 201


@projects_bp.route("", methods=["GET"])
@jwt_required()
def list_projects():
    user_id = _current_user_id()
    if user_id is None:
        return api_error("UnauthorizedError", "invalid token identity", 401)

    projects = (
        Project.query.filter_by(owner_id=user_id)
        .order_by(Project.created_time.desc())
        .all()
    )
    return jsonify(project_response_schema.dump(projects, many=True)), 200


@projects_bp.route("/<int:project_id>", methods=["GET"])
@jwt_required()
def get_project(project_id: int):
    user_id = _current_user_id()
    if user_id is None:
        return api_error("UnauthorizedError", "invalid token identity", 401)

    project = Project.query.filter_by(id=project_id).first()
    if not project:
        return api_error("NotFoundError", "project not found", 404)
    if project.owner_id != user_id:
        return api_error("ForbiddenError", "forbidden", 403)

    return jsonify(project_response_schema.dump(project)), 200


@projects_bp.route("/<int:project_id>", methods=["PUT"])
@jwt_required()
def update_project(project_id: int):
    user_id = _current_user_id()
    if user_id is None:
        return api_error("UnauthorizedError", "invalid token identity", 401)

    project = Project.query.filter_by(id=project_id).first()
    if not project:
        return api_error("NotFoundError", "project not found", 404)
    if project.owner_id != user_id:
        return api_error("ForbiddenError", "forbidden", 403)

    data, err = get_json_body(request)
    if err:
        return err

    try:
        payload = project_update_request_schema.load(data)
    except ValidationError as err:
        return validation_error_from_messages(err.messages)

    if "title" in payload:
        project.title = payload["title"].strip()

    if "description" in payload:
        description = payload["description"]
        if isinstance(description, str):
            description = description.strip() or None
        project.description = description

    db.session.commit()
    return jsonify(project_response_schema.dump(project)), 200


@projects_bp.route("/<int:project_id>", methods=["DELETE"])
@jwt_required()
def delete_project(project_id: int):
    user_id = _current_user_id()
    if user_id is None:
        return api_error("UnauthorizedError", "invalid token identity", 401)

    project = Project.query.filter_by(id=project_id).first()
    if not project:
        return api_error("NotFoundError", "project not found", 404)
    if project.owner_id != user_id:
        return api_error("ForbiddenError", "forbidden", 403)

    db.session.delete(project)
    db.session.commit()
    return jsonify(message_response_schema.dump({"message": "project deleted"})), 200
