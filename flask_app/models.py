from flask_app import db, ma
from marshmallow import fields, ValidationError
from datetime import datetime
from sqlalchemy.orm import composite

"""
This file contains the SQL Alchemy models used to store User and Jogg data 
"""


class User(db.Model):
    """
    User Model to store username, encrypted password, and type
    """
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(50), unique=True, nullable=False)
    password = db.Column(db.String(50), unique=False, nullable=False)
    type = db.Column(db.String(5), unique=False, nullable=False)
    created_date = db.Column(db.DateTime, nullable=False, default=datetime.now)
    joggs = db.relationship('Jogg', backref='jogger', lazy=True)

    def __repr__(self):
        return f"User('{self.username}')"


class UserSchema(ma.Schema):
    """
    Marshmallow Schema to convert SqlAlchemy Model to Json
    """
    class Meta:
        fields = ("id", "username", "type")


user_schema = UserSchema()
users_schema = UserSchema(many=True)


class Location(fields.Field):
    """
    Location class that contains geographic co-ordinates (latitude and longitude) of any location
    Note: This is not a SQlAlchemy Model and does not have separate table in our DB
    """
    def __init__(self, lat, lon, **metadata):
        super().__init__(**metadata)
        self.lat = lat
        self.lon = lon

    def __composite_values__(self):
        return self.lat, self.lon

    def __repr__(self):
        return f"Location(lat={self.lat}, lon={self.lon})"

    def __eq__(self, other):
        return isinstance(other, Location) and \
            other.lat == self.lat and \
            other.lon == self.lon

    def __ne__(self, other):
        return not self.__eq__(other)

    def _serialize(self, value, attr, obj, **kwargs):
        if value is None:
            return ""
        return "".join(str(d) for d in value)

    def _deserialize(self, value, attr, data, **kwargs):
        try:
            return [int(c) for c in value]
        except ValueError as error:
            raise ValidationError("Pin codes must contain only digits.") from error


class LocationSchema(ma.Schema):
    """
    Marshmallow Schema to convert Location to Json
    """
    class Meta:
        fields = ("lat", "lon")


location_schema = LocationSchema()
locations_schema = LocationSchema(many=True)


class Jogg(db.Model):
    """
    Jogg Model to store user_id, start and end time as well as start and end locations of the jog
    """
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=False)
    start_time = db.Column(db.DateTime, nullable=False, default=datetime.now)
    end_time = db.Column(db.DateTime, nullable=False, default=datetime.now)
    start_lat = db.Column(db.Integer, nullable=False)
    start_lon = db.Column(db.Integer, nullable=False)
    start_location = composite(Location, start_lat, start_lon)
    start_weather = db.Column(db.String(5000), unique=False, nullable=False)
    end_lat = db.Column(db.Integer, nullable=False)
    end_lon = db.Column(db.Integer, nullable=False)
    end_location = composite(Location, end_lat, end_lon)
    end_weather = db.Column(db.String(5000), unique=False, nullable=False)
    created_date = db.Column(db.DateTime, nullable=False, default=datetime.now)

    def __repr__(self):
        return f"Jogg('id': '{self.id}', 'user': '{self.user_id}', start_location': '{self.start_location}'," \
               f" 'end_location': '{self.end_location}', 'start_weather': '{self.start_weather}', 'end_weather': '{self.end_weather}')"


class JoggSchema(ma.Schema):
    """
    Marshmallow Schema to convert Jogg Model to Json
    """
    start_location = fields.Nested(LocationSchema)
    end_location = fields.Nested(LocationSchema)

    class Meta:
        fields = ("id", "user_id", "start_time", "end_time", "start_location", "end_location",
                  'start_weather', 'end_weather', "created_date")


jogg_schema = JoggSchema()
joggs_schema = JoggSchema(many=True)


