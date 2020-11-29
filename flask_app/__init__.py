from os import environ

from flask import Flask
from flask_bcrypt import Bcrypt
from flask_jwt import JWT
from flask_marshmallow import Marshmallow
from flask_sqlalchemy import SQLAlchemy

app = Flask(__name__)

app.config.from_object(environ.get('APP_SETTINGS', 'flask_app.config.LocalConfig'))

db = SQLAlchemy(app)
bcrypt = Bcrypt(app)
ma = Marshmallow(app)
from flask_app.auth import authenticate, identity

jwt = JWT(app, authenticate, identity)


from flask_app.routes.user_routes import user_routes
from flask_app.routes.admin_routes import admin_routes
from flask_app.routes.auth_routes import auth_routes

app.register_blueprint(user_routes)
app.register_blueprint(admin_routes, url_prefix="/admin")
app.register_blueprint(auth_routes, url_prefix="/auth")

