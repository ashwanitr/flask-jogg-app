from flask import jsonify
from flask import request
from flask_jwt import jwt_required, current_identity

from flask_app.auth import requires_auth
from flask_app.routes import admin_routes
from flask_app.services import user_service, jogg_service, validation_util
from flask_app.models import User

"""
This file contains Admin/Root user routes. Only users with type "Admin" and "Root" can access these routes.
Other users will get "Unauthorized to perform this action" error on executing these endpoints.

Each endpoint contains @requires_auth(allowed_roles) annotation. 
The list allowed_roles passed as parameter to this annotation decides if the endpoint can be executed by 
"Admin" user or "Root" user or both

These functions just delegate the incoming calls to user_service, jogg_service and weather_service. 
"""


@admin_routes.route("/users/<int:page>", methods=['GET'])
@admin_routes.route("/users", methods=['GET'])
@jwt_required()
@requires_auth(allowed_roles=["Admin", "Root"])
def get_all_users(page=1):
    user_types = ["User"] if current_identity.type == "Admin" else ["User", "Admin"]
    return jsonify(user_service.get_users_paginated(user_types=user_types, page=page))


@admin_routes.route("/users/<username>", methods=['GET'])
@jwt_required()
@requires_auth(allowed_roles=["Admin", "Root"])
def get_user_by_username(username):
    return jsonify(user_service.get_user(username))


@admin_routes.route("/users", methods=['POST', 'DELETE'])
@jwt_required()
@requires_auth(allowed_roles=["Admin", "Root"])
def modify_user():
    data = request.json
    if 'username' not in data:
        validation_util.error_message(message="Invalid Operation! Need a valid Username")
    username = data.get("username")
    user = User.query.filter_by(username=username).first()
    if user:
        if user.type == "Root":
            validation_util.error_message(message="Invalid Operation! Invalid permissions to modify a Root User")
        if user.type == "Admin" and current_identity.type != "Root":
            validation_util.error_message(message="Invalid Operation! Invalid permissions to modify a Admin User")

    if request.method == 'POST':
        password = data.get("password")
        user_type = data.get("type")
        if user_type == "Root":
            validation_util.error_message(message="Invalid Operation! Invalid permissions to modify a Root User")
        elif user_type == "Admin" and current_identity.type != "Root":
            validation_util.error_message(message="Invalid Operation! Invalid permissions to modify a Admin User")
        return jsonify(user_service.update_user(username, password, user_type, auto_create=True))
    elif request.method == 'DELETE':
        return jsonify(user_service.delete_user(username))


@admin_routes.route("/users/<username>/joggs/<int:page>")
@admin_routes.route("/users/<username>/joggs")
@admin_routes.route("/joggs/<int:page>")
@admin_routes.route("/joggs")
@jwt_required()
@requires_auth(allowed_roles=["Root"])
def get_joggs(username=None, page=1):
    if username:
        return jsonify(jogg_service.get_paginated_joggs_for_user(username, page=page))
    else:
        return jsonify(jogg_service.get_paginated_joggs(page=page))


@admin_routes.route("/joggs", methods=['POST', 'PUT', 'DELETE'])
@jwt_required()
@requires_auth(allowed_roles=["Root"])
def modify_jogg():
    if request.method == 'POST' or request.method == 'PUT':
        data = request.json
        return jsonify(jogg_service.update_jogg(jogg_id=data.get('jogg_id'),
                                                username=data.get('username'),
                                                start_time=data.get('start_time'),
                                                end_time=data.get('end_time'),
                                                start_location=data.get('start_location'),
                                                end_location=data.get('end_location'),
                                                auto_create=True))
    elif request.method == 'DELETE':
        data = request.json
        return jsonify(jogg_service.delete_jogg(jogg_id=data.get('jogg_id'), force=True))


@admin_routes.route("/users/<username>/speed")
@jwt_required()
@requires_auth(allowed_roles=["Admin", "Root"])
def get_average_user_speed(username):
    return jsonify(user_service.get_average_speed(username))


@admin_routes.route("/users/<username>/distance")
@jwt_required()
@requires_auth(allowed_roles=["Admin", "Root"])
def get_average_user_distance(username):
    return jsonify(user_service.get_average_distance(username))
