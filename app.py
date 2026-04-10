import os

from flask import Flask
from flask_jwt_extended import JWTManager

from models import bcrypt, db
from routes.auth import auth_bp
from routes.projects import projects_bp

app = Flask(__name__)
app.config["SQLALCHEMY_DATABASE_URI"] = (
    "postgresql://postgres:postgres@localhost:5432/postgres"
)
app.config["JWT_SECRET_KEY"] = os.environ.get(
    "JWT_SECRET_KEY", "dev-secret-change-me"
)

db.init_app(app)
bcrypt.init_app(app)
jwt = JWTManager(app)
app.register_blueprint(auth_bp, url_prefix="/auth")
app.register_blueprint(projects_bp, url_prefix="/projects")


@jwt.unauthorized_loader
def handle_missing_or_invalid_token(_reason: str):
    return {"error": "AuthError", "message": "Missing or invalid token"}, 401


if __name__ == "__main__":
    with app.app_context():
        db.create_all()
    app.run(debug=True)

