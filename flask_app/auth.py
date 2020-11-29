from flask_jwt import current_identity
from functools import wraps

from flask_app import bcrypt
from flask_app.models import User

"""
Authentication helpers for flask-jwt auth 
"""

def authenticate(username, password):
    """
    Authentication function used by flask jwt to authorize validity of user credentials while login
    :param username:
    :param password:
    :return:
    """

    user = User.query.filter_by(username=username).first()
    if user and bcrypt.check_password_hash(user.password, password):
        return user


def identity(payload):
    """
    Identity function used by flask jwt to extract User object from jwt token
    This method is executed whenever someone calls any authenticated endpoint with valid jwt token
    The user object extracted here can be accessed in all function annotated with @jwt_required() using current_identity
    :param payload:
    :return:
    """
    user_id = payload['identity']
    return User.query.get(user_id)


def requires_auth(allowed_roles):
    """
    Custom function used for authorized access to any endpoint.
    Just annotate any route with @requires_auth() with a list of allowed roles.
    Only user types provided in allowed_roles parameter will be allowed to access the annotated endpoint.
    :param allowed_roles:
    :return:
    """
    def wrapper(fn):
        @wraps(fn)
        def decorator(*args, **kwargs):
            if allowed_roles and isinstance(allowed_roles, list):
                if not current_identity:
                    return {"error": "Unauthenticated Call"}
                if current_identity.type not in allowed_roles:
                    return {"error": "Unauthorized to perform this action"}
            return fn(*args, **kwargs)
        return decorator
    return wrapper
