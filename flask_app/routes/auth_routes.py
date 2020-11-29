from flask import jsonify
from flask import request

from flask_app.services import user_service, validation_util
from flask_app.routes import auth_routes

"""
This file contains just one route for users to register. 
The endpoint is unauthenticated and can be accessed by anyone to register as a "User", "Admin" or "Root" 
"""

@auth_routes.route('/register', methods=['POST'])
def register():
    data = request.json
    username = data.get("username")
    password = data.get("password")
    user_type = data.get("type")
    return jsonify(user_service.create_user(username, password, user_type))
