from datetime import datetime
import json
from flask_app import db
from flask_app.models import User, Jogg, jogg_schema, joggs_schema, Location
from flask_app.services import validation_util, location_util, weather_service

"""
Jogg Service:
    Provides CRUD functionality for Jogg objects.
"""

def get_jogg_by_id(jogg_id):
    return validation_util.success_message(data=jogg_schema.dump(Jogg.query.get(jogg_id)))


def get_paginated_joggs(page=1, per_page=10):
    return validation_util.success_message(data=joggs_schema
                                           .dump(Jogg.query.order_by(Jogg.created_date.desc())
                                                 .paginate(page, per_page).items))


def get_paginated_joggs_for_user(username, page=1, per_page=10):
    user = User.query.filter_by(username=username).first()
    return validation_util.success_message(data=joggs_schema
                                           .dump(Jogg.query.filter_by(user_id=user.id)
                                                 .order_by(Jogg.created_date.desc())
                                                 .paginate(page, per_page).items))


def create_jogg(username, start_time, end_time, start_location, end_location):
    user = User.query.filter_by(username=username).first()
    if user:
        user_id = user.id
    else:
        return validation_util.error_message(message="Cannot create Jogg without a Valid User")

    err = validation_util.validate({"start_time": start_time, "end_time": end_time, "start_location": start_location,
                                    "end_location": end_location})
    if err:
        return err

    if not isinstance(start_time, int) or not isinstance(end_time, int):
        validation_util.error_message(f"Invalid start_time and end_time timestamps. Expecting integers")

    start_location = location_util.get_location_object(start_location)
    end_location = location_util.get_location_object(end_location)

    start_weather = json.dumps(weather_service.get_weather_forecast_from_server(start_location.lat,
                                                                                start_location.lon,
                                                                                start_time))
    end_weather = json.dumps(weather_service.get_weather_forecast_from_server(end_location.lat,
                                                                              end_location.lon,
                                                                              end_time))

    new_jogg = Jogg(user_id=user_id, start_time=datetime.fromtimestamp(start_time),
                    end_time=datetime.fromtimestamp(end_time),
                    start_lat=start_location.lat, start_lon=start_location.lon, end_lat=end_location.lat,
                    end_lon=end_location.lon, start_weather=start_weather, end_weather=end_weather)
    db.session.add(new_jogg)
    db.session.commit()
    return validation_util.success_message(data=jogg_schema.dump(new_jogg))


def update_jogg(jogg_id, username, start_time, end_time, start_location, end_location, auto_create=False):
    existing_jogg = Jogg.query.get(jogg_id)
    if existing_jogg:
        if username:
            user = User.query.filter_by(username=username).first()
            existing_jogg.user_id = user.id

        start_weather_update = check_start_weather_data(existing_jogg, start_location, start_time)
        end_weather_update = check_end_weather_data(existing_jogg, end_location, end_time)
        start_time = start_time if start_time else existing_jogg.start_time
        end_time = end_time if end_time else existing_jogg.end_time
        start_location = location_util.get_location_object(start_location) if start_location else Location(
            existing_jogg.start_lat, existing_jogg.lon)
        end_location = location_util.get_location_object(end_location) if end_location else Location(
            existing_jogg.end_lat, existing_jogg.end_lon)

        existing_jogg.start_time = datetime.fromtimestamp(start_time)
        existing_jogg.end_time = datetime.fromtimestamp(end_time)
        existing_jogg.start_lat = start_location.lat
        existing_jogg.start_lon = start_location.lon
        existing_jogg.end_lat = end_location.lat
        existing_jogg.end_lon = end_location.lon

        if start_weather_update:
            existing_jogg.start_weather = json.dumps(weather_service.get_weather_forecast_from_server(start_location.lat,
                                                                                                      start_location.lon,
                                                                                                      start_time))
        if end_weather_update:
            existing_jogg.end_weather = json.dumps(weather_service.get_weather_forecast_from_server(end_location.lat,
                                                                                                    end_location.lon,
                                                                                                    end_time))

        db.session.commit()
        return validation_util.success_message(data=jogg_schema.dump(existing_jogg))
    else:
        if auto_create:
            return create_jogg(username, start_time, end_time, start_location, end_location)
        return validation_util.error_message(message="No Jogg found with given ID.")


def delete_jogg(jogg_id, deleted_by=None, force=False):
    jogg = Jogg.query.filter_by(id=jogg_id).first()
    if jogg:
        if force or jogg.user_id == deleted_by:
            db.session.delete(jogg)
            db.session.commit()
            return validation_util.success_message(data=f"Successfully deleted jogg with id {jogg.id}")
    return validation_util.error_message(message=f"Unable to delete jogg with id {jogg.id}")


def check_start_weather_data(jogg, location, time):
    if location and 'lat' in location and 'lon' in location:
        if jogg.start_lat != location.get('lat') or jogg.start_lon != location.get('lon'):
            return True
    if time and jogg.start_time != time:
        return True
    return False


def check_end_weather_data(jogg, location, time):
    if location and 'lat' in location and 'lon' in location:
        if jogg.end_lat != location.get('lat') or jogg.end_lon != location.get('lon'):
            return True
    if time and jogg.end_time != time:
        return True
    return False
