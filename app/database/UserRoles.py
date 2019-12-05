from datetime import datetime

from app import db, login_manager
from flask import current_app
from flask_login import AnonymousUserMixin, UserMixin
from itsdangerous import TimedJSONWebSignatureSerializer as Serializer
from sqlalchemy import (Boolean, Column, DateTime, ForeignKey, Integer, String,
                        Table)
from werkzeug.security import check_password_hash, generate_password_hash


class Permission:
    READ = 0x01
    WRITE = 0x02
    UPLOAD = 0x04
    REPORT = 0x08
    MANAGER = 0x10
    WAREHOUSE = 0x20
    SAMPLECENTER = 0x40
    PRODUCTION = 0x80
    CONSULTANT = 0x100
    ADMINISTER = 0x200


class RoleInfo(db.Model):
    __tablename__ = 'Roles'
    id = Column(Integer, primary_key=True)
    name = Column(String(64), unique=True)
    default = Column(Boolean, default=False, index=True)
    permissions = Column(Integer)
    users = db.relationship('UserInfo', backref='role', lazy='dynamic')

    @staticmethod
    def insert_roles():
        roles = {
            "Guest": (Permission.READ, True),
            "Manager": (Permission.READ | Permission.WRITE | Permission.UPLOAD | Permission.REPORT | Permission.MANAGER, False),
            "Manager": (Permission.READ | Permission.WRITE | Permission.UPLOAD | Permission.REPORT | Permission.MANAGER, False),
            "Warehouse": (Permission.READ | Permission.WRITE | Permission.UPLOAD | Permission.WAREHOUSE, False),
            "Samplecenter": (Permission.READ | Permission.WRITE | Permission.UPLOAD | Permission.SAMPLECENTER, False),
            "Production": (Permission.READ | Permission.WRITE | Permission.UPLOAD | Permission.PRODUCTION, False),
            "Consultant": (Permission.READ | Permission.WRITE | Permission.UPLOAD | Permission.REPORT | Permission.CONSULTANT, False),
            "Administrator": (0xfff, False)
        }
        for r in roles:
            role = RoleInfo.query.filter_by(name=r).first()
            if role is None:
                role = RoleInfo(name=r)
                role.permissions = roles[r][0]
                role.default = roles[r][1]
                db.session.add(role)
        db.session.commit()

    def __repr__(self):
        return '<RoleInfo %r>' % self.name


class UserInfo(UserMixin, db.Model):
    __tablename__ = "Users"
    id = Column(Integer, primary_key=True)
    email = Column(String(64), unique=True, index=True)
    username = Column(String(64), unique=True, index=True)
    realname = Column(String(64), unique=True, index=True)
    role_id = Column(Integer, ForeignKey('Roles.id'))
    password_hash = Column(String(128))
    datetime = Column(DateTime, default=datetime.now())
    num = Column(Integer)
    confirmed = Column(Boolean, default=False)

    def __init__(self, **kwargs):
        super(UserInfo, self).__init__(**kwargs)
        if self.role is None:
            if self.email == current_app.config['FLASK_ADMIN']:
                self.role = RoleInfo.query.filter_by(permission=0xff).first()
            if self.role is None:
                self.role = RoleInfo.query.filter_by(default=True).first()

    @property
    def password(self):
        raise AttributeError('password is not a readable attribute')

    @password.setter
    def password(self, password):
        self.password_hash = generate_password_hash(password)

    def verify_password(self, password):
        return check_password_hash(self.password_hash, password)

    def generate_confirmation_token(self, expiration=3600):
        s = Serializer(current_app.config['SECRET_KEY'], expiration)
        return s.dumps({'confirm': self.id})

    def confirm(self, token):
        s = Serializer(current_app.config['SECRET_KEY'])
        try:
            data = s.loads(token)
            print(data)
        except:
            return False
        if data.get('confirm') != self.id:
            return False
        self.confirmed = True
        db.session.commit()
        db.session.close()
        return True

    def generate_reset_token(self, expiration=3600):
        s = Serializer(current_app.config['SECRET_KEY'], expiration=expiration)
        return s.dumps({'reset': self.id})

    def reset_password(self, token, new_password):
        s = Serializer(current_app.config['SECRET_KEY'])
        try:
            data = s.loads(token)
        except:
            return False
        if data.get('reset') != self.id:
            return False
        self.password = new_password
        db.session.add(self)
        db.session.commit()
        return True

    def generate_email_change_token(self, new_email, expiration=3600):
        s = Serializer(current_app.config['SECRET_KEY'], expiration)
        return s.dumps({'change_email': self.id, 'new_email': new_email})

    def change_email(self, token):
        s = Serializer(current_app.config['SECRET_KEY'])
        try:
            data = s.loads(token)
        except:
            return False
        if data.get('change_email') != self.id:
            return False
        new_email = data.get('new_mail')
        if new_email is None:
            return False
        if self.query.filter_by(email=new_email) is not None:
            return None
        self.email = new_email
        db.session.add(self)
        return True

    def can(self, permissions):
        return self.role is not None and (self.role.permissions & permissions) == permissions

    def is_administrator(self):
        return self.can(Permission.ADMINISTER)

    def __repr__(self):
        return '<UserInfo %r>' % self.username

    def UserInfor2dict(self):
        data = {
            'id': self.id,
            'email': self.email,
            'username': self.username,
            'realname': self.realname,
            'roleid':  {"1":"Guest","2":"Manager","3":"Warehouse","4":"Samplecenter","5":"Production","6":"Consultant","7":"Administrator","None":"未确定"}[str(self.role_id)],
            # 'roleid': self.role_id,
            'datetime': self.datetime,

        }
        if None != data['datetime']:
            data['datetime'] = data['datetime'].strftime(
                "%Y-%m-%d %H:%M:%S")
        return data

    def change_authority(self,role):
        if role == 'None':
            role = None
        else:
            role = int(role)
        self.role_id = role
        db.session.commit()
        return True

    def update(self,data):
        token = self.generate_confirmation_token()
        if data['username']!= '':
            self.username = data['username']
        if data["realname"] != '':
            self.realname = data["realname"]
        if data["password"] != '':
            self.password = data["password"]
        if data["email"] != '':
            self.email = data["email"]
        db.session.commit()


class AnonymousUser(AnonymousUserMixin):
    def can(self, permissions):
        return False

    def is_administrator(self):
        return False


login_manager.anonymous_user = AnonymousUser


@login_manager.user_loader
def load_user(user_id):
    return UserInfo.query.get(int(user_id))
