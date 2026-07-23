from flask import Flask

from config import Config
from .extensoes import db, login_manager, csrf


def create_app(config_class=Config):
    app = Flask(__name__)
    app.config.from_object(config_class)

    db.init_app(app)
    login_manager.init_app(app)
    csrf.init_app(app)

    from . import modelos  # registra o modelo Usuario no SQLAlchemy

    from .principal.rotas import bp as principal_bp
    app.register_blueprint(principal_bp)

    from .jogos.rotas import bp as jogos_bp
    app.register_blueprint(jogos_bp)

    from .auth.rotas import bp as auth_bp
    app.register_blueprint(auth_bp)

    with app.app_context():
        db.create_all()

    return app
