from flask import Blueprint
"""
Exposes user, admin and auth routes as Flask Blueprints
"""
user_routes = Blueprint('user_routes', __name__)
admin_routes = Blueprint('admin_routes', __name__)
auth_routes = Blueprint('auth_routes', __name__)

from . import admin_routes, auth_routes, user_routes