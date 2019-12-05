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
    # PYReport = "/share/data7/opt/pysample_report"
    PYReport = os.environ.get('PYReport')
    PYTemplate = os.path.join(base_path, 'application/template')
    PYSamplesheet = os.path.join(base_path, 'static', 'samplesheet')
    # DBUser = os.environ.get('USERNAME')
    # DBPassword = os.environ.get('PASSWORD')
    # DBName = 'PYsample'
    # SQLALCHEMY_DATABASE_URI = "mysql+pymysql://{user}:{password}@192.168.1.21:3306/{dbname}".format(
    #  user=DBUser, password=DBPassword, dbname=DBName)
    DBUser = os.environ.get('dbuser')
    DBPassword = os.environ.get('dbpassword')
    DBName = os.environ.get("sample_dbname")
    SQLALCHEMY_DATABASE_URI = "mysql+pymysql://{user}:{password}@127.0.0.1:3306/{dbname}".format(
        user=DBUser, password=DBPassword, dbname=DBName)
    SQLALCHEMY_TRACK_MODIFICATIONS = True
    CELERY_BROKER_URL = 'amqp://guest:guest@127.0.0.1:5672'
    CELERY_RESULT_BACKEND = 'redis://127.0.0.1:6379'
    JSON_AS_ASCII = False
    json4PYSampleStatus = os.path.join(
        base_path, 'application', 'PYSampleStatus.json')
    json4PYQuestionnaireStatus = os.path.join(
        base_path, 'application', 'PYQuestionnaireStatus.json')
    json4PYSampleInfo = os.path.join(
        base_path, 'application', 'PYSampleInfo.json')
    json4PYFormulaType = os.path.join(
        base_path, 'application', 'PYFormulaType.json')
    json2releaseapply = os.path.join(
        base_path, 'application', 'PYReleaseApply.json')
    json2releaseupdate = os.path.join(
        base_path, 'application', 'PYReleaseUpdate.json')
    json2sampleback = os.path.join(
        base_path, 'application', 'PYSampleBack.json')
    PYFormulaVersion = '2018.Jun26'
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
    syncurl = os.environ.get('syncurl')
    CELERYBEAT_SCHEDULE = {
        'syncQuestStatus_every_10_minutes': {
            'task': 'app.schedule.scheduleTask.syncQuestionnaireStatus',
            'schedule': 600  #600 # 0
        },
        "syncQuestSheet_every_30_minutes": {
            'task': 'app.schedule.scheduleTask.syncQuestionnaireSheet',
            'schedule': 1800  #1800  # 0
        },
        "autoJSONReport_every_20_minutes": {
            'task': 'app.schedule.scheduleTask.autoJSONReport',
            'schedule': 1200  #1200 # 0
        },
        "autoJSONStatus_every_20_minutes": {
            'task': 'app.schedule.scheduleTask.autoJSONStatus',
            'schedule': 1200  #1200  # 0
        },
        "autoSampleReport_every_10_minutes": {
            'task': 'app.schedule.scheduleTask.autoSampleReport',
            'schedule': 600  #600 # 0
        },
        "autoSampleStatus_every_10_minutes": {
            'task': 'app.schedule.scheduleTask.autoSampleStatus',
            'schedule': 60  #600 # 0
        },

    }


class ProductConfig(Config):
    DEBUG = True
    base_path = os.path.dirname(os.path.realpath(__file__))
    # print('pro', base_path)

    DEBUG = True
    DefaultGroup = "develop"
    DefaultUser = "develop"
    # root2project = "/share/data2/PYProject"
    root2project = os.environ.get("root2project")
    DBUser = 'develop'
    DBPassword = 'develop2018'
    DBName = 'VAS2PRO'
    # DBUser = os.environ.get("dbuser")
    # DBPassword = os.environ.get("dbpassword")
    # DBName = os.environ.get("sample_dbname")
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
