import datetime
from geopy.distance import geodesic

from flask_app.models import User, users_schema, user_schema, Jogg, joggs_schema
from flask_app import db, bcrypt
from flask_app.services import validation_util

"""
User Service:
    Provides CRUD functionality for User objects.
"""

def get_user(username):
    return validation_util.success_message(data=user_schema.dump(User.query.filter_by(username=username).first()))


def get_users_paginated(user_types=None, page=1, per_page=10):
    if user_types is None:
        user_types = ["User"]
    return validation_util.success_message(data=users_schema
                                           .dump(User.query.order_by(User.created_date.desc()).filter(User.type.in_(user_types))
                                                 .paginate(page, per_page).items))


def create_user(username, password, type):
    user = User.query.filter_by(username=username).first()
    if user:
        return validation_util.error_message(message="User Already Registered")
    else:
        err = validation_util.validate({"username": username, "password": password, "type": type})
        if err:
            return err
        user = User(username=username, password=bcrypt.generate_password_hash(password), type=type)
        db.session.add(user)
        db.session.commit()
        return validation_util.success_message(data=user_schema.dump(user))


def update_user(username, password, type, auto_create=False):
    user = User.query.filter_by(username=username).first()
    if not user:
        if auto_create:
            return create_user(username, password, type)
        else:
            return validation_util.error_message(message="Cannot update user! Invalid User Details")
    else:
        user.username = username
        if password:
            user.password = bcrypt.generate_password_hash(password)
        if type:
            user.type = type
        db.session.commit()
        return validation_util.success_message(data=user_schema.dump(user))


def delete_user(username):
    user = User.query.filter_by(username=username).first()
    if user:
        jogg = Jogg.query.filter_by(user_id=user.id).first()
        if jogg:
            return validation_util.error_message(
                message="Cannot delete user. User has associated jogg objects created. Delete all user's joggs first")
        db.session.delete(user)
        db.session.commit()
        return validation_util.success_message("Deleted Successfully!")
    return validation_util.error_message("User does not exist")


def get_average_speed(username):
    time_cutoff = datetime.datetime.now() - datetime.timedelta(7)
    user = User.query.filter_by(username=username).first()
    joggs = Jogg.query.filter_by(user_id=user.id).filter(Jogg.created_date >= time_cutoff).all()
    speeds = [safe_division(extract_jogg_distance(jogg), extract_jogg_time(jogg)) for jogg in joggs]
    return validation_util.success_message(data={'average_speed(kph)': safe_division(sum(speeds), len(speeds))})


def get_average_distance(username):
    time_cutoff = datetime.datetime.now() - datetime.timedelta(7)
    user = User.query.filter_by(username=username).first()
    joggs = Jogg.query.filter_by(user_id=user.id).filter(Jogg.created_date >= time_cutoff).all()
    distances = [extract_jogg_distance(jogg) for jogg in joggs]
    return validation_util.success_message(data={'average_distance(km)': safe_division(sum(distances), len(distances))})


def extract_jogg_time(jogg):
    return (jogg.end_time - jogg.start_time).total_seconds() / 3600


def extract_jogg_distance(jogg):
    return geodesic((jogg.start_lat, jogg.start_lon), (jogg.end_lat, jogg.end_lon)).kilometers


def safe_division(n, d):
    return n / d if d else 0
