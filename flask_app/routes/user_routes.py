from datetime import datetime

from flask import jsonify
from flask import request
from flask_jwt import jwt_required, current_identity

from flask_app.auth import requires_auth
from flask_app.services import user_service, jogg_service, validation_util
from . import user_routes

"""
This file contains user routes. Only users with type "User" can access these routes.
Admin and Root users will get "Unauthorized to perform this action" error on executing these endpoints   
"""

@user_routes.route("/users/<username>")
@user_routes.route("/users")
@jwt_required()
@requires_auth(allowed_roles=["User"])
def get_user(username=None):
    if username:
        if current_identity.username == username:
            return jsonify(user_service.get_user(current_identity.username))
        else:
            return jsonify(validation_util.error_message(message="Invalid Request"))
    else:
        return jsonify(user_service.get_user(current_identity.username))


@user_routes.route("/users/<username>/joggs/<page>", methods=['GET'])
@user_routes.route("/users/<username>/joggs", methods=['GET'])
@jwt_required()
@requires_auth(allowed_roles=["User"])
def get_joggs(username, page=1):
    if current_identity.username == username:
        return jsonify(jogg_service.get_paginated_joggs_for_user(current_identity.username, page=page))
    else:
        return jsonify(validation_util.error_message(message="Invalid Request"))


@user_routes.route("/users/<username>/joggs", methods=['POST', 'PUT', 'DELETE'])
@jwt_required()
@requires_auth(allowed_roles=["User"])
def modify_jogg(username):
    if current_identity.username == username:
        if request.method == 'POST' or request.method == 'PUT':
            data = request.json
            if data.get('jogg_id') and jogg_service.get_jogg_by_id(data.get('jogg_id')):
                existing_jogg = jogg_service.get_jogg_by_id(data.get('jogg_id'))
                if existing_jogg.get('user_id') == current_identity.id:
                    return jsonify(jogg_service
                                   .update_jogg(jogg_id=data.get('jogg_id'), username=data.get('username'),
                                                start_time=data.get('start_time'), end_time=data.get('end_time'),
                                                start_location=data.get('start_location'),
                                                end_location=data.get('end_location'), auto_create=True))
                else:
                    return jsonify(validation_util.error_message(message="Invalid Request"))
            else:
                return jsonify(jogg_service
                               .update_jogg(jogg_id=data.get('jogg_id'), username=current_identity.username,
                                            start_time=data.get('start_time'), end_time=data.get('end_time'),
                                            start_location=data.get('start_location'),
                                            end_location=data.get('end_location'), auto_create=True))
        elif request.method == 'DELETE':
            data = request.json
            if data and 'jogg_id' in data:
                existing_jogg = jogg_service.get_jogg_by_id(data.get('jogg_id')).get('data')
                if existing_jogg and existing_jogg.get('user_id') == current_identity.id:
                    return jsonify(jogg_service.delete_jogg(data.get('jogg_id'), deleted_by=current_identity.id))
                else:
                    return jsonify(validation_util.error_message(message="Invalid Request"))
            else:
                return validation_util.error_message(message="Could not delete jogg. Invalid jogg id detected")
    else:
        return jsonify(validation_util.error_message(message="Invalid Request"))


@user_routes.route("/users/<username>/speed")
@jwt_required()
@requires_auth(allowed_roles=["User"])
def get_average_user_speed(username):
    if current_identity.username == username:
        return jsonify(user_service.get_average_speed(current_identity.username))
    else:
        return jsonify(validation_util.error_message(message="Invalid Request"))


@user_routes.route("/users/<username>/distance")
@jwt_required()
@requires_auth(allowed_roles=["User"])
def get_average_user_distance(username):
    if current_identity.username == username:
        return jsonify(user_service.get_average_distance(current_identity.username))
    else:
        return jsonify(validation_util.error_message(message="Invalid Request"))
