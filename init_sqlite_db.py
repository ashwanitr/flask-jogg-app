from flask_app import db, bcrypt
from flask_app.models import User, Jogg, Location

"""
Database initialization commands
run `python init_sqlite_db.py` from command line to setup local sqlite database
"""

db.create_all()
# Create a dummy user
user = User(username="user", password=bcrypt.generate_password_hash("password"), type="User")
db.session.add(user)
db.session.commit()

# Create a dummy admin
admin = User(username="admin", password=bcrypt.generate_password_hash("password"), type="Admin")
db.session.add(admin)
db.session.commit()

# Create a dummy root
root = User(username="root", password=bcrypt.generate_password_hash("password"), type="Root")
db.session.add(root)
db.session.commit()

location_a = Location(lat=25, lon=50)
location_b = Location(lat=155, lon=250)

# Create a dummy jogg
jogg_1 = Jogg(user_id=user.id, start_lat=location_a.lat, start_lon=location_a.lon, start_weather='Dummy',
              end_lat=location_b.lat, end_lon=location_b.lon, end_weather='dummy')
db.session.add(jogg_1)
db.session.commit()

print(User.query.all())
print(Jogg.query.all())