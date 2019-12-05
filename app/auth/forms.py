from app.database.UserRoles import UserInfo
from flask_wtf import FlaskForm
from wtforms import (BooleanField, PasswordField, StringField, SubmitField,
                     ValidationError)
from wtforms.validators import DataRequired, Email, EqualTo, Length, Regexp


class LoginForm(FlaskForm):
    username = StringField(
        '用户名',
        validators=[DataRequired(),
                    Length(1, 64),
                    Regexp('^[A-Za-z][A-Za-z0-9_.]*$',
                           0,
                           'Usernames must have only letters, '
                           'numbers, dots or underscores')])
    password = PasswordField('密码', validators=[DataRequired()])
    remember_me = BooleanField('Keep me logged in')
    submit = SubmitField('Log In')


class RegisterForm(FlaskForm):
    username = StringField(
        '用户名',
        validators=[DataRequired(),
                    Length(1, 64),
                    Regexp('^[A-Za-z][A-Za-z0-9_.]*$',
                           0,
                           'Usernames must have only letters, '
                           'numbers, dots or underscores')])
    realname = StringField('真实姓名',
        validators=[DataRequired(),
                    Length(1, 64)])
    password = PasswordField('密码', validators=[DataRequired()])

    pwd_confirm = PasswordField(
        label='重复密码',
        validators=[
            DataRequired(message='重复密码不能为空.'),
            EqualTo('password', message="两次密码输入不一致")
        ],
    )

    email = StringField('邮箱', validators=[DataRequired(), Email()])

    submit = SubmitField('注册')



