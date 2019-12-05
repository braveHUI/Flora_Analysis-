import json
import os
import sys


class Config:
    SECRET_KEY = os.environ.get('SECRET_KEY') or 'PUYUAN2017'
    CELERY_TASK_SERIALIZER = 'json'
    CELERY_RESULT_SERIALIZER = 'json'
    CELERY_ACCEPT_CONTENT = ['json', 'pickle']


class DevelopmentConfig(Config):
    DEBUG = True
    base_path = os.path.dirname(os.path.realpath(__file__))
    # print(base_path)
    PYReport = "/home/instal/biosoft/pg/pysample_report"
    PYTemplate = os.path.join(base_path, 'application/template')
    PYSamplesheet = os.path.join(base_path, 'static', 'samplesheet')
    DBUser = 'root'
    DBPassword = 'hgh15070417641'
    DBName = 'PYsample'
    SQLALCHEMY_DATABASE_URI = "mysql+pymysql://{user}:{password}@127.0.0.1:3306/{dbname}".format(
        user=DBUser, password=DBPassword, dbname=DBName)
    # print(SQLALCHEMY_DATABASE_URI)
    SQLALCHEMY_TRACK_MODIFICATIONS = True
    CELERY_BROKER_URL = 'amqp://guest:guest@127.0.0.1:5672'
    CELERY_RESULT_BACKEND = 'redis://127.0.0.1:6379'
    JSON_AS_ASCII = False
    json2translate = os.path.join(base_path, 'application', 'Translate.json')
    json4PYSampleStatus = os.path.join(
        base_path, 'application', 'PYSampleStatus.json')
    json4PYQuestionnaireStatus = os.path.join(
        base_path, 'application', 'PYQuestionnaireStatus.json')
    json2releaseapply = os.path.join(
        base_path, 'application', 'PYReleaseApply.json')
    json2sampleback = os.path.join(
        base_path, 'application', 'PYSampleBack.json')
    cachedir = os.path.join(base_path, 'static', 'cache')
    cachelist = os.path.join(cachedir, 'cachelist.json')
    # SQLALCHEMY_POOL_SIZE = 50
    # SQLALCHEMY_POOL_TIMEOUT = 10
    FLASK_ADMIN = 'zhouyuanjie@promegene.com'
    if False == os.path.exists(PYSamplesheet):
        os.makedirs(PYSamplesheet, mode=0o751)
    if False == os.path.exists(cachedir):
        os.makedirs(cachedir, mode=0o751)
    synchead = {'content-type': 'application/json'}
    syncauth = {'username': 'develop', 'password': 'douhaoyu'}
    syncurl = "http://192.168.1.144:8080/uploadTubeInfo"
    CELERYBEAT_SCHEDULE = {
        'syncQuestStatus_every_10_minutes': {
            'task': 'app.schedule.scheduleTask.syncQuestionnaireStatus',
            'schedule': 600
        },
        "syncQuestSheet_every_30_minutes": {
            'task': 'app.schedule.scheduleTask.syncQuestionnaireSheet',
            'schedule': 1800
        }
    }


class ProductConfig(Config):
    DEBUG = True
    base_path = os.path.dirname(os.path.realpath(__file__))
    # print('pro', base_path)

    DEBUG = True
    DefaultGroup = "develop"
    DefaultUser = "develop"
    root2project = "/share/data2/PYProject"
    DBUser = 'root'
    DBPassword = 'hgh15070417641'
    DBName = 'pysample'
    SQLALCHEMY_DATABASE_URI = "mysql+pymysql://{user}:{password}@localhost:3306/{dbname}".format(user=DBUser,
                                                                                                 password=DBPassword,
                                                                                                 dbname=DBName)
    SQLALCHEMY_TRACK_MODIFICATIONS = True
    CELERY_BROKER_URL = 'amqp://guest:guest@localhost:5672'
    CELERY_RESULT_BACKEND = 'redis://localhost:6379'
    JSON_AS_ASCII = False
    CELERYBEAT_SCHEDULE = {
        'listen_task_folder': {
            'task': 'app.application.listen2project.listen_task_folder',
            'schedule': 3
        },
        "check_task_complete": {
            'task': 'app.application.listen2project.check_task_complete',
            'schedule': 10
        }
    }
    # SQLALCHEMY_POOL_SIZE = 50
    # SQLALCHEMY_POOL_TIMEOUT = 10
    mapping_dir = os.path.join(base_path, 'static', 'mapping')
    mapping_configuration = os.path.join(
        base_path, 'static/configuration', 'mapping_config.txt')


config = {'development': DevelopmentConfig,
          'ProductConfig': ProductConfig,
          'default': DevelopmentConfig
          }
