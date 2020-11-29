from flask_app.models import Location
from flask_app.services import validation_util


def get_location_object(coordinates):
    """
    Utility function to check that given coordinates are in valid format and returns instance of Location class
    :param coordinates:
    :return: Location
    """

    if not isinstance(coordinates, dict):
        return validation_util.error_message(message="Invalid Location format, expected dict of lat and lon")
    err = validation_util.validate({"lat": coordinates.get("lat"), "lon": coordinates.get("lon")})
    if err:
        return err
    return Location(coordinates["lat"], coordinates["lon"])
