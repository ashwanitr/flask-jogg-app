import unittest
from flask_testing import TestCase

from flask_app import app, db, bcrypt
from flask_app.models import User, Jogg, Location

"""
Unit Tests using Flask-Testing
run `python tests.py` from command line to execute the tests
"""


class AuthTests(TestCase):
    test_username = "test"
    test_password = "test"
    test_type = "User"

    def create_app(self):
        return app

    def test_register_success(self):
        username = "new_user"
        data = {
            "username": username,
            "password": self.test_password,
            "type": self.test_type
        }
        json_response = self.client.post("/auth/register", json=data).json
        response_data = json_response.get('data')
        user = User.query.filter_by(username=username).first()
        self.assertEqual(response_data.get('username'), username)
        self.assertEqual(user.username, username)

    def test_register_failure_user_exists(self):
        data = {
            "username": self.test_username,
            "password": self.test_password,
            "type": self.test_type
        }
        json_response = self.client.post("/auth/register", json=data).json
        user = User.query.filter_by(username=self.test_username).first()
        self.assertEqual(json_response.get('message'), "User Already Registered")
        self.assertTrue(json_response.get('error'))
        self.assertEqual(user.username, self.test_username)

    def test_login_success(self):
        data = {
            "username": self.test_username,
            "password": self.test_password
        }
        json_response = self.client.post("/login", json=data).json
        self.assertIsNotNone(json_response.get('access_token'))

    def test_login_failure_invalid_credentials(self):
        data = {
            "username": self.test_username,
            "password": "Invalid Password"
        }
        json_response = self.client.post("/login", json=data).json
        self.assertEqual(json_response.get('status_code'), 401)

    def test_unauthenticated_call_without_jwt(self):
        json_response = self.client.get("/users").json
        self.assertEqual(json_response.get('status_code'), 401)

    def test_authenticated_call_with_jwt(self):
        data = {
            "username": self.test_username,
            "password": self.test_password
        }
        json_response = self.client.post("/login", json=data).json

        json_response = self.client.get("/users",
                                        headers={"Authorization": f"JWT {json_response.get('access_token')}"}).json
        self.assertFalse(json_response.get('error'))
        self.assertIsNotNone(json_response.get('data'))

    def setUp(self):
        db.create_all()
        test_user = User(username=self.test_username,
                         password=bcrypt.generate_password_hash(self.test_password),
                         type=self.test_type)
        db.session.add(test_user)
        db.session.commit()

    def tearDown(self):
        db.session.remove()
        db.drop_all()


class UserTests(TestCase):
    test_username = "test"
    test_password = "test"
    user_type = "User"

    def create_app(self):
        return app

    def _get_auth_headers(self):
        data = {
            "username": self.test_username,
            "password": self.test_password
        }
        json_response = self.client.post("/login", json=data).json
        return {"Authorization": f"JWT {json_response.get('access_token')}"}

    def test_login_success(self):
        data = {
            "username": self.test_username,
            "password": self.test_password
        }
        json_response = self.client.post("/login", json=data).json
        self.assertIsNotNone(json_response.get('access_token'))

    def test_login_failure_invalid_credentials(self):
        data = {
            "username": self.test_username,
            "password": "Invalid Password"
        }
        json_response = self.client.post("/login", json=data).json
        self.assertEqual(json_response.get('status_code'), 401)

    def test_unauthenticated_call_without_jwt(self):
        json_response = self.client.get("/users").json
        self.assertEqual(json_response.get('status_code'), 401)

    def test_get_joggs(self):
        json_response = self.client.get(f"/users/{self.test_username}/joggs",
                                        headers=self._get_auth_headers()).json
        response_data = json_response.get('data')
        self.assertFalse(json_response.get('error'))
        self.assertIsNotNone(response_data)
        u = User.query.filter_by(username=self.test_username).first()
        self.assertEqual(len(response_data), 1)
        self.assertEqual(response_data[0].get('user_id'), u.id)

    def test_delete_jogg(self):
        user_id = User.query.filter_by(username=self.test_username).first().id
        r = Jogg.query.filter_by(user_id=user_id).first()
        json_response = self.client.delete(f"/users/{self.test_username}/joggs",
                                           json={'jogg_id': r.id},
                                           headers=self._get_auth_headers()).json
        response_data = json_response.get('data')
        self.assertFalse(json_response.get('error'))
        self.assertIsNotNone(response_data)
        r = Jogg.query.filter_by(user_id=user_id).first()
        self.assertIsNone(r)

    def setUp(self):
        db.create_all()
        test_user = User(username=self.test_username,
                         password=bcrypt.generate_password_hash(self.test_password),
                         type=self.user_type)
        db.session.add(test_user)
        db.session.commit()

        location_a = Location(lat=25, lon=50)
        location_b = Location(lat=15, lon=20)

        jogg_1 = Jogg(user_id=test_user.id, start_lat=location_a.lat, start_lon=location_a.lon, end_lat=location_b.lat,
                      end_lon=location_b.lon, start_weather='dummy', end_weather='dummy')
        db.session.add(jogg_1)
        db.session.commit()

    def tearDown(self):
        db.session.remove()
        db.drop_all()


class AdminTests(TestCase):
    admin_username = "test"
    admin_password = "test"
    user_type = "Admin"

    def create_app(self):
        return app

    def _get_auth_headers(self):
        data = {
            "username": self.admin_username,
            "password": self.admin_password
        }
        json_response = self.client.post("/login", json=data).json
        return {"Authorization": f"JWT {json_response.get('access_token')}"}


    def test_create_user(self):
        json_response = self.client.post(f"/admin/users",
                                         json={"username": "random", "password": "random", "type": "User"},
                                         headers=self._get_auth_headers()).json
        response_data = json_response.get('data')
        self.assertFalse(json_response.get('error'))
        self.assertIsNotNone(response_data)
        u = User.query.filter_by(username='random').first()
        self.assertEqual(response_data.get('id'), u.id)

    def test_delete_user(self):
        user_id = User.query.filter_by(username=self.admin_username).first().id
        r = Jogg.query.filter_by(user_id=user_id).first()
        db.session.delete(r)
        db.session.commit()
        json_response = self.client.delete(f"/admin/users",
                                           json={'username': self.admin_username},
                                           headers=self._get_auth_headers()).json
        response_data = json_response.get('data')
        self.assertFalse(json_response.get('error'))
        u = User.query.filter_by(username=self.admin_username).first()
        self.assertIsNone(u)

    def setUp(self):
        db.create_all()
        test_user = User(username=self.admin_username,
                         password=bcrypt.generate_password_hash(self.admin_password),
                         type=self.user_type)
        db.session.add(test_user)
        db.session.commit()

        location_a = Location(lat=25, lon=50)
        location_b = Location(lat=15, lon=20)

        jogg_1 = Jogg(user_id=test_user.id, start_lat=location_a.lat, start_lon=location_a.lon, end_lat=location_b.lat,
                      end_lon=location_b.lon, start_weather='dummy', end_weather='dummy')
        db.session.add(jogg_1)
        db.session.commit()

    def tearDown(self):
        db.session.remove()
        db.drop_all()


class RootTests(TestCase):
    root_username = "test"
    root_password = "test"
    user_type = "Root"

    def create_app(self):
        return app

    def _get_auth_headers(self):
        data = {
            "username": self.root_username,
            "password": self.root_password
        }
        json_response = self.client.post("/login", json=data).json
        return {"Authorization": f"JWT {json_response.get('access_token')}"}

    def test_get_joggs(self):
        json_response = self.client.get(f"/admin/joggs",
                                        headers=self._get_auth_headers()).json
        response_data = json_response.get('data')
        self.assertFalse(json_response.get('error'))
        self.assertIsNotNone(response_data)
        u = User.query.filter_by(username=self.root_username).first()
        self.assertEqual(len(response_data), 1)
        self.assertEqual(response_data[0].get('user_id'), u.id)

    def test_delete_jogg(self):
        user_id = User.query.filter_by(username=self.root_username).first().id
        r = Jogg.query.filter_by(user_id=user_id).first()
        json_response = self.client.delete(f"/admin/joggs",
                                           json={'jogg_id': r.id},
                                           headers=self._get_auth_headers()).json
        response_data = json_response.get('data')
        self.assertFalse(json_response.get('error'))
        self.assertIsNotNone(response_data)
        r = Jogg.query.filter_by(user_id=user_id).first()
        self.assertIsNone(r)

    def setUp(self):
        db.create_all()
        test_user = User(username=self.root_username,
                         password=bcrypt.generate_password_hash(self.root_password),
                         type=self.user_type)
        db.session.add(test_user)
        db.session.commit()

        location_a = Location(lat=25, lon=50)
        location_b = Location(lat=15, lon=20)

        jogg_1 = Jogg(user_id=test_user.id, start_lat=location_a.lat, start_lon=location_a.lon, end_lat=location_b.lat,
                      end_lon=location_b.lon, start_weather='dummy', end_weather='dummy')
        db.session.add(jogg_1)
        db.session.commit()

    def tearDown(self):
        db.session.remove()
        db.drop_all()


if __name__ == '__main__':
    unittest.main()

