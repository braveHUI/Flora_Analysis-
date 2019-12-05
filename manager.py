import os
from datetime import datetime

from app import create_app, db
from app.application.generateSampleJson import SampleJSON
from app.application import ReportJSON
from app.database import Questionnaire, RoleInfo, SampleInfo, UserInfo
from flask_migrate import Migrate, MigrateCommand
from flask_script import Manager, Server

app = create_app('development')
manager = Manager(app)
migrate = Migrate(app, db, compare_type=True)
manager.add_command('server', Server(host='localhost'), port=8080)
manager.add_command('db', MigrateCommand)


@manager.command
def insert_role():
    RoleInfo.insert_roles()
    print('insert_roles\tsuccess')


@manager.option('-u', '--username', dest='username', required=True, help='username')
@manager.option('-p', '--password', dest='password', required=True, help='password')
@manager.option('-n', '--realname', dest='realname', required=True, help='realname')
@manager.option('-r', '--role', dest='rolename', required=True, help='role name')
def adduser(username, password, realname, rolename):
    user = UserInfo.query.filter_by(username=username).first()
    role = RoleInfo.query.filter_by(name=rolename).first()
    if user:
        raise RuntimeError('The username has already existed ')
    if role is None:
        raise RuntimeError('The role name does not exist')
    user = UserInfo(username=username, realname=realname)
    user.password = password
    user.role_id = role.id
    db.session.add(user)
    token = user.generate_confirmation_token()
    user.confirm(token)

    new_user = UserInfo.query.filter_by(username=username).first()
    role = RoleInfo.query.filter_by(name=rolename).first()
    new_user.role_id = role.id
    db.session.commit()
    db.session.close()
    print('add user success:', username, realname, rolename)


# 通过命令行修改密码
@manager.option('-u', '--username', dest='username', required=True, help='username')
@manager.option('-p', '--password', dest='password', required=True, help='password')
@manager.option('-n', '--new_password', dest='new_password', required=True, help='new password')
def change_password(username, password, new_password):
    user = UserInfo.query.filter_by(username=username).first()
    if user is None:
        raise RuntimeError('Ivalid username')
    if user.verify_password(password):
        user.password = new_password
        db.session.commit()
        print('success')
    else:
        raise RuntimeError('Ivalid password')


@manager.shell
def make_context_shell():
    return dict(app=app,
                db=db,
                SampleInfo=SampleInfo,
                ReportJSON=ReportJSON,
                SampleJSON=SampleJSON)


if __name__ == "__main__":
    manager.run()
