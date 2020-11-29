from flask_app import app

"""
Weather Service:
    Fetch Weather Forecast from Open Weather Map API
"""

def get_weather_forecast_from_server(lat, lon, time):
    import requests

    api_key = app.config['OWM_API_KEY']
    url = f"https://api.openweathermap.org/data/2.5/onecall?lat={lat}&lon={lon}&appid={api_key}&" \
          f"units=metric&exclude=current,minutely,daily,alerts"
    response = requests.get(url)
    json_response = response.json()
    hourly_data = json_response.get('hourly')
    forecasted_time_list = [x.get('dt') for x in hourly_data]
    closest_index = min(range(len(forecasted_time_list)), key=lambda i: abs(forecasted_time_list[i] - time))
    return hourly_data[closest_index]



