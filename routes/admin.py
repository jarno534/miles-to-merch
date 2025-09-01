from flask import Blueprint
from extensions import db
from models import Product
from .api import login_required
import requests
import json

admin_bp = Blueprint('admin', __name__, url_prefix='/admin')