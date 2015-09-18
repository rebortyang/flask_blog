__author__ = 'yangjiebin'
from flask import   Blueprint

auth = Blueprint('auth',__name__)

from . import views