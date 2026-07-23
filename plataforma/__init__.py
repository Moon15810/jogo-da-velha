from flask import Flask

from config import Config
from .extensoes import db, login_manager


def create_app(config_class=Config):
    app = Flask(__name__)
    app.config.from_object(config_class)

    db.init_app(app)
    login_manager.init_app(app)

    from . import modelos  # registra o modelo Usuario no SQLAlchemy

    with app.app_context():
        db.create_all()

    return app
