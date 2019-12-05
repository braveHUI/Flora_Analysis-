from datetime import datetime

from celery import Celery
from flask import Flask
from flask_bootstrap import Bootstrap
from flask_login import LoginManager
from flask_mail import Mail
from flask_moment import Moment
from flask_sqlalchemy import SQLAlchemy

from .config import DevelopmentConfig, ProductConfig, config

bootstrap = Bootstrap()
mail = Mail()
moment = Moment()
db = SQLAlchemy()
login_manager = LoginManager()
login_manager.session_protection = 'strong'
login_manager.login_view = 'auth.login'
celery = Celery(__name__, backend=DevelopmentConfig.CELERY_RESULT_BACKEND,
                broker=DevelopmentConfig.CELERY_BROKER_URL)

from .database import Questionnaire, RoleInfo, SampleInfo, UserInfo
from .schedule import (autoJSONReport, autoJSONStatus, autoSampleReport,
                       autoSampleStatus, syncQuestionnaireSheet,
                       syncQuestionnaireStatus)


def create_app(config_name):
    app = Flask(__name__)
    app.config.from_object(config[config_name])
    bootstrap.init_app(app)
    mail.init_app(app)
    moment.init_app(app)
    db.init_app(app)
    login_manager.init_app(app)
    celery.conf.update(app.config)

    from app.auth import auth
    app.register_blueprint(auth)

    from app.interface import interface
    app.register_blueprint(interface)
    return app
