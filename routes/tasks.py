from flask import Blueprint, jsonify, request
from flask_jwt_extended import get_jwt_identity, jwt_required
from marshmallow import ValidationError

from errors import api_error, validation_error_from_messages
from models import Project, Task, db
from routes.models import (
    MessageResponseSchema,
    TaskCreateRequestSchema,
    TaskListQuerySchema,
    TaskResponseSchema,
    TaskUpdateRequestSchema,
)
from validation import get_json_body

tasks_bp = Blueprint("tasks", __name__)
task_create_request_schema = TaskCreateRequestSchema()
task_update_request_schema = TaskUpdateRequestSchema()
task_list_query_schema = TaskListQuerySchema()
task_response_schema = TaskResponseSchema()
message_response_schema = MessageResponseSchema()


def _current_user_id() -> int | None:
    identity = get_jwt_identity()
    try:
        return int(identity)
    except (TypeError, ValueError):
        return None


def _owned_project_or_error(project_id: int, user_id: int):
    project = Project.query.filter_by(id=project_id).first()
    if not project:
        return None, api_error("NotFoundError", "project not found", 404)
    if project.owner_id != user_id:
        return None, api_error("ForbiddenError", "forbidden", 403)
    return project, None


def _owned_task_or_error(task_id: int, user_id: int):
    task = Task.query.filter_by(id=task_id).first()
    if not task:
        return None, api_error("NotFoundError", "task not found", 404)
    project, err = _owned_project_or_error(task.project_id, user_id)
    if err:
        return None, err
    return task, None


@tasks_bp.route("/projects/<int:project_id>/tasks", methods=["POST"])
@jwt_required()
def create_task(project_id: int):
    user_id = _current_user_id()
    if user_id is None:
        return api_error("UnauthorizedError", "invalid token identity", 401)

    _, err = _owned_project_or_error(project_id, user_id)
    if err:
        return err

    data, err = get_json_body(request)
    if err:
        return err

    try:
        payload = task_create_request_schema.load(data)
    except ValidationError as err:
        return validation_error_from_messages(err.messages)

    title = payload["title"].strip()
    description = payload.get("description")
    if isinstance(description, str):
        description = description.strip() or None

    task = Task(
        project_id=project_id,
        title=title,
        description=description,
        status=payload.get("status", "todo"),
        due_date=payload.get("due_date"),
    )
    db.session.add(task)
    db.session.commit()
    return jsonify(task_response_schema.dump(task)), 201


@tasks_bp.route("/projects/<int:project_id>/tasks", methods=["GET"])
@jwt_required()
def list_project_tasks(project_id: int):
    user_id = _current_user_id()
    if user_id is None:
        return api_error("UnauthorizedError", "invalid token identity", 401)

    _, err = _owned_project_or_error(project_id, user_id)
    if err:
        return err

    try:
        query_params = task_list_query_schema.load(request.args.to_dict())
    except ValidationError as err:
        return validation_error_from_messages(err.messages)

    query = Task.query.filter_by(project_id=project_id)
    if "status" in query_params:
        query = query.filter(Task.status == query_params["status"])
    if "due_before" in query_params:
        query = query.filter(Task.due_date <= query_params["due_before"])
    if "searchText" in query_params:
        query = query.filter(Task.title.ilike(f"%{query_params['searchText'].strip()}%"))

    total = query.count()
    limit = query_params["limit"]
    if "offset" in query_params:
        offset = query_params["offset"]
        page = (offset // limit) + 1
    else:
        page = query_params["page"]
        offset = (page - 1) * limit

    tasks = query.order_by(Task.created_time.desc()).offset(offset).limit(limit).all()
    return (
        jsonify(
            {
                "items": task_response_schema.dump(tasks, many=True),
                "pagination": {
                    "page": page,
                    "limit": limit,
                    "offset": offset,
                    "total": total,
                },
            }
        ),
        200,
    )


@tasks_bp.route("/tasks/<int:task_id>", methods=["GET"])
@jwt_required()
def get_task(task_id: int):
    user_id = _current_user_id()
    if user_id is None:
        return api_error("UnauthorizedError", "invalid token identity", 401)

    task, err = _owned_task_or_error(task_id, user_id)
    if err:
        return err
    return jsonify(task_response_schema.dump(task)), 200


@tasks_bp.route("/tasks/<int:task_id>", methods=["PUT"])
@jwt_required()
def update_task(task_id: int):
    user_id = _current_user_id()
    if user_id is None:
        return api_error("UnauthorizedError", "invalid token identity", 401)

    task, err = _owned_task_or_error(task_id, user_id)
    if err:
        return err

    data, err = get_json_body(request)
    if err:
        return err

    try:
        payload = task_update_request_schema.load(data)
    except ValidationError as err:
        return validation_error_from_messages(err.messages)

    if "title" in payload:
        task.title = payload["title"].strip()
    if "description" in payload:
        description = payload["description"]
        if isinstance(description, str):
            description = description.strip() or None
        task.description = description
    if "status" in payload:
        task.status = payload["status"]
    if "due_date" in payload:
        task.due_date = payload["due_date"]

    db.session.commit()
    return jsonify(task_response_schema.dump(task)), 200


@tasks_bp.route("/tasks/<int:task_id>", methods=["DELETE"])
@jwt_required()
def delete_task(task_id: int):
    user_id = _current_user_id()
    if user_id is None:
        return api_error("UnauthorizedError", "invalid token identity", 401)

    task, err = _owned_task_or_error(task_id, user_id)
    if err:
        return err

    db.session.delete(task)
    db.session.commit()
    return jsonify(message_response_schema.dump({"message": "task deleted"})), 200
