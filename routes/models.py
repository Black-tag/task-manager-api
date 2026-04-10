from marshmallow import Schema, ValidationError, fields, validate, validates_schema
from marshmallow_sqlalchemy import SQLAlchemyAutoSchema, auto_field

from models import Project, Task, User, db


class RegisterRequestSchema(Schema):
    name = fields.Str(required=True, validate=validate.Length(min=1, max=100))
    email = fields.Email(required=True, validate=validate.Length(max=100))
    password = fields.Str(required=True, validate=validate.Length(min=1, max=72))


class LoginRequestSchema(Schema):
    email = fields.Email(required=True, validate=validate.Length(max=100))
    password = fields.Str(required=True, validate=validate.Length(min=1, max=72))


class ProjectCreateRequestSchema(Schema):
    title = fields.Str(required=True, validate=validate.Length(min=1, max=100))
    description = fields.Str(required=False, allow_none=True, validate=validate.Length(max=200))


class ProjectUpdateRequestSchema(Schema):
    title = fields.Str(required=False, validate=validate.Length(min=1, max=100))
    description = fields.Str(required=False, allow_none=True, validate=validate.Length(max=200))

    @validates_schema
    def validate_non_empty_update(self, data, **kwargs):
        if "title" not in data and "description" not in data:
            raise ValidationError("at least one of title or description is required")


class TaskCreateRequestSchema(Schema):
    title = fields.Str(required=True, validate=validate.Length(min=1, max=100))
    description = fields.Str(
        required=False, allow_none=True, validate=validate.Length(max=200)
    )
    status = fields.Str(
        required=False,
        validate=validate.OneOf(["todo", "in_progress", "done"]),
    )
    due_date = fields.Date(required=False, allow_none=True)


class TaskUpdateRequestSchema(Schema):
    title = fields.Str(required=False, validate=validate.Length(min=1, max=100))
    description = fields.Str(
        required=False, allow_none=True, validate=validate.Length(max=200)
    )
    status = fields.Str(
        required=False,
        validate=validate.OneOf(["todo", "in_progress", "done"]),
    )
    due_date = fields.Date(required=False, allow_none=True)

    @validates_schema
    def validate_non_empty_update(self, data, **kwargs):
        if (
            "title" not in data
            and "description" not in data
            and "status" not in data
            and "due_date" not in data
        ):
            raise ValidationError(
                "at least one of title, description, status, or due_date is required"
            )


class TaskListQuerySchema(Schema):
    page = fields.Int(required=False, load_default=1, validate=validate.Range(min=1))
    limit = fields.Int(
        required=False, load_default=20, validate=validate.Range(min=1, max=100)
    )
    offset = fields.Int(required=False, validate=validate.Range(min=0))
    status = fields.Str(
        required=False,
        validate=validate.OneOf(["todo", "in_progress", "done"]),
    )
    due_before = fields.Date(required=False)
    searchText = fields.Str(required=False, validate=validate.Length(min=1, max=100))

    @validates_schema
    def validate_pagination_mode(self, data, **kwargs):
        if "offset" in data and "page" in data and data["page"] != 1:
            raise ValidationError("use either page+limit or offset+limit")


class UserResponseSchema(SQLAlchemyAutoSchema):
    class Meta:
        model = User
        sqla_session = db.session
        load_instance = False
        fields = ("id", "name", "email", "created_time")

    created_time = auto_field(dump_only=True)


class ProjectResponseSchema(SQLAlchemyAutoSchema):
    class Meta:
        model = Project
        sqla_session = db.session
        load_instance = False
        include_fk = True
        fields = ("id", "owner_id", "title", "description", "created_time")

    created_time = auto_field(dump_only=True)


class AuthTokensResponseSchema(Schema):
    access_token = fields.Str(required=True)
    refresh_token = fields.Str(required=True)
    user = fields.Nested(UserResponseSchema, required=True)


class MessageResponseSchema(Schema):
    message = fields.Str(required=True)


class TaskResponseSchema(SQLAlchemyAutoSchema):
    class Meta:
        model = Task
        sqla_session = db.session
        load_instance = False
        include_fk = True
        fields = (
            "id",
            "project_id",
            "title",
            "description",
            "status",
            "due_date",
            "created_time",
            "last_modified_time",
        )

    due_date = auto_field(dump_only=True)
    created_time = auto_field(dump_only=True)
    last_modified_time = auto_field(dump_only=True)
