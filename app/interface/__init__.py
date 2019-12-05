from flask import Blueprint

interface = Blueprint('interface', __name__)

from . import views
