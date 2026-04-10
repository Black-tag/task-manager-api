from datetime import datetime
from flask_sqlalchemy import SQLAlchemy
from flask_bcrypt import Bcrypt

db = SQLAlchemy()
bcrypt = Bcrypt()


class User(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(100), nullable=False)
    email = db.Column(db.String(100), unique=True, index=True, nullable=False)
    password_hash = db.Column(db.String(100), nullable=False)
    created_time = db.Column(db.DateTime, default=lambda: datetime.utcnow())

class Project(db.Model):
    id = db.Column(db.Integer, primary_key=True, index=True)
    owner_id = db.Column(db.Integer, db.ForeignKey("user.id"), nullable=False, index=True)
    title = db.Column(db.String(100), nullable=False)
    description = db.Column(db.String(200), nullable=True)
    created_time = db.Column(db.DateTime, default=lambda: datetime.utcnow())
    owner = db.relationship("User", backref=db.backref("projects", lazy=True))


class Task(db.Model):
    id = db.Column(db.Integer, primary_key=True, index=True)
    project_id = db.Column(
        db.Integer, db.ForeignKey("project.id"), nullable=False, index=True
    )
    title = db.Column(db.String(100), nullable=False)
    description = db.Column(db.String(200), nullable=True)
    status = db.Column(db.String(20), nullable=False, default="todo", index=True)
    due_date = db.Column(db.Date, nullable=True)
    created_time = db.Column(db.DateTime, default=lambda: datetime.utcnow())
    last_modified_time = db.Column(
        db.DateTime,
        default=lambda: datetime.utcnow(),
        onupdate=lambda: datetime.utcnow(),
    )
    project = db.relationship("Project", backref=db.backref("tasks", lazy=True))