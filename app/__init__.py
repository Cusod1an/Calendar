# app/__init__.py
from flask import Flask
from flask_sqlalchemy import SQLAlchemy
from flask_socketio import SocketIO

db = SQLAlchemy()
socketio = SocketIO()  # Глобальний об'єкт SocketIO


def create_app():
    app = Flask(__name__)
    app.config.from_object("config.Config")

    db.init_app(app)
    socketio.init_app(app)  # Ініціалізація SocketIO з додатком

    # Реєстрація контролерів
    from app.controllers.maintenance_controller import bp as maintenance_bp
    app.register_blueprint(maintenance_bp, url_prefix="/maintenance")

    from app.controllers.equipment_controller import bp as equipment_bp
    app.register_blueprint(equipment_bp, url_prefix="/equipment")

    from app.controllers.auth_controller import bp as auth_bp
    app.register_blueprint(auth_bp, url_prefix="/auth")

    return app
