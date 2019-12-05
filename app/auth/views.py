from app import db
from app.database import RoleInfo, UserInfo
from app.decorators import Admin_required
from flask import flash, redirect, render_template, request, url_for
from flask_login import (current_user, fresh_login_required, login_required,
                         login_user, logout_user)

from . import auth
from .forms import LoginForm, RegisterForm


@auth.route('/login', methods=['GET', 'POST'])
def login():
    form = LoginForm()
    if form.validate_on_submit():
        user = UserInfo.query.filter_by(username=form.username.data).first()
        if user is not None and user.verify_password(form.password.data):
            login_user(user, form.remember_me.data)
            db.session.close()
            return redirect(url_for('interface.index'))
        flash('Invalid username or password')
    db.session.close()
    return render_template('auth/login.html', form=form)


@auth.route('/logout')
@login_required
def logout():
    logout_user()
    flash('You have been logged out.')
    return redirect(url_for('auth.login'))


@auth.route('/register', methods=['GET', 'POST'])
def register():
    form = RegisterForm()
    if form.validate_on_submit():
        roleinfo = RoleInfo.query.filter_by(default=True).first()
        rolename = roleinfo.name
        userinfo = UserInfo.query.filter_by(
            username=form.username.data).first()
        role = RoleInfo.query.filter_by(name=rolename).first()
        if None == userinfo:
            user = UserInfo(username=form.username.data,
                            realname=form.realname.data)
            user.password = form.password.data
            user.role_id = role.id
            user.email = form.email.data

            token = user.generate_confirmation_token()
            user.confirm(token)
            db.session.add(user)
            db.session.commit()
            db.session.close()
            flash('注册成功！')
        else:
            db.session.close()
            flash('用户已注册！')

    return render_template('auth/register.html', form=form)


@auth.route('/UserAdmin', methods=['GET', 'POST'])
@login_required
@Admin_required
def useradmin():
    items = UserInfo.query.all()
    sampleList = {}
    line = 1
    for sample in items:
        sampleList[line] = sample.UserInfor2dict()
        line += 1
    # print(sampleList)
    return render_template('auth/useradmin.html')


@auth.route('/ChangeInfor', methods=['GET', 'POST'])
@login_required
@fresh_login_required
def changeinfor():
    select = request.json
    if None == select:
        return render_template('auth/change_infor.html')
    # print(select)
    try:
        User = UserInfo.query.filter_by(username=select['username']).first()
        User.update(select)
        db.session.close()
    except:
        db.session.rollback()
        db.session.close()
        print("sth wrong about change userinfor")
    return render_template('auth/change_infor.html')


# ==============================================================================
# 404.html
# 403.html
# ==============================================================================
@auth.errorhandler(404)
def page_not_found(e):
    return render_template('404.html'), 404


@auth.errorhandler(403)
def permisson_denied(e):
    return render_template('403.html'), 403
