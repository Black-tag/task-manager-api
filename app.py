from flask import Flask
from flask_jwt_extended import JWTManager

from config import Config
from models import bcrypt, db
from routes.auth import auth_bp
from routes.projects import projects_bp
from routes.tasks import tasks_bp

app = Flask(__name__)
app.config.from_object(Config)

db.init_app(app)
bcrypt.init_app(app)
jwt = JWTManager(app)
app.register_blueprint(auth_bp, url_prefix="/auth")
app.register_blueprint(projects_bp, url_prefix="/projects")
app.register_blueprint(tasks_bp)


@jwt.unauthorized_loader
def handle_missing_or_invalid_token(_reason: str):
    return {"error": "AuthError", "message": "Missing or invalid token"}, 401


if __name__ == "__main__":
    with app.app_context():
        db.create_all()
    app.run(
        host=app.config["HOST"],
        port=app.config["PORT"],
        debug=app.config["DEBUG"],
    )

