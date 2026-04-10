from marshmallow import Schema, ValidationError, fields, validate, validates_schema
from marshmallow_sqlalchemy import SQLAlchemyAutoSchema, auto_field

from models import Project, User, db


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
