from flask import Flask

from app.database import db
from config import Config


def create_app():
    app = Flask(__name__)
    app.config.from_object(Config)

    db.init_app(app)

    from app.routes import main_bp

    app.register_blueprint(main_bp)

    return app