from flask import Flask
from flask_sqlalchemy import SQLAlchemy
from flask_migrate import Migrate

from app.config import Config

db = SQLAlchemy()
migrate = Migrate()


def create_app(config_class=Config):
    from app.routes.auth import auth
    from app.routes.menu import menu
    from app.routes.order import order
    from app.routes.category import category

    app = Flask(__name__)
    app.config.from_object(config_class)

    db.init_app(app)
    migrate.init_app(app, db)

    app.register_blueprint(auth, url_prefix="/auth")
    app.register_blueprint(menu, url_prefix="/menu")
    app.register_blueprint(order, url_prefix="/order")
    app.register_blueprint(category, url_prefix="/categories")

    return app
