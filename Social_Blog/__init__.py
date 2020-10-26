from config import Config
from flask import Flask
from flask_bcrypt import Bcrypt
from flask_cors import CORS
from flask_login import LoginManager
from flask_mail import Mail
from flask_migrate import Migrate
from flask_sqlalchemy import SQLAlchemy

db = SQLAlchemy()
cors = CORS()
bcrypt = Bcrypt()
migrate = Migrate()
login_manager = LoginManager()
mail = Mail()
login_manager.login_view = "login"
login_manager.login_message_category = "danger-alert"


def create_app(config_class=Config):
    app = Flask(__name__)
    app.config.from_object(Config)

    db.init_app(app)
    cors.init_app(app)
    bcrypt.init_app(app)
    login_manager.init_app(app)
    migrate.init_app(app, db)
    mail.init_app(app)

    with app.app_context():
        from . import models, routes

        return app
