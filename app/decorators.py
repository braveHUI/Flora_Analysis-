from functools import wraps

from app.database.UserRoles import Permission
from flask import abort
from flask_login import current_user


def permission_required(permission):
    def decorator(f):
        @wraps(f)
        def decorated_function(*args, **kwargs):
            if not current_user.can(permission):
                abort(403)
            return f(*args, **kwargs)
        return decorated_function
    return decorator


def Manager_required(f):
    return permission_required(Permission.READ | Permission.WRITE | Permission.UPLOAD | Permission.MANAGER)(f)


def Warehouse_required(f):
    return permission_required(Permission.READ | Permission.WRITE | Permission.UPLOAD | Permission.WAREHOUSE)(f)


def Samplecenter_required(f):
    return permission_required(Permission.READ | Permission.WRITE | Permission.UPLOAD | Permission.SAMPLECENTER)(f)


def Production_required(f):
    return permission_required(Permission.READ | Permission.WRITE | Permission.UPLOAD | Permission.PRODUCTION)(f)


def Consultant_required(f):
    return permission_required(Permission.READ | Permission.WRITE | Permission.UPLOAD | Permission.CONSULTANT)(f)


def Reporter_required(f):
    return permission_required(Permission.READ | Permission.WRITE | Permission.UPLOAD | Permission.REPORT)(f)


def Admin_required(f):
    return permission_required(Permission.ADMINISTER)(f)
