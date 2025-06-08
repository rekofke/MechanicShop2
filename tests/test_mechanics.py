import unittest
from app import create_app
from app.models import db, Mechanic
from app.util.auth import encode_token
from werkzeug.security import generate_password_hash

class TestMechanic(unittest.TestCase):
    
    def setUp(self):
        self.app = create_app('TestingConfig')
        self.mechanic = Mechanic(
            name='test',
            email='test@test.com',
            salary=50000,
            password=generate_password_hash('123')
        )
        with self.app.app_context():
            db.drop_all()
            db.create_all()
            db.session.add(self.mechanic)
            db.session.commit()
        self.token = encode_token(1)
        self.client = self.app.test_client()

    def test_create_mechanic(self):
        payload = {
            'name': 'Test Mechanic',
            'email': 'unique_test@test.com',
            'salary': 50000,
            'password': '123'
        }

        response = self.client.post('/mechanics/', json=payload)
        self.assertEqual(response.status_code, 201)
        self.assertEqual(response.json['name'], 'Test Mechanic')


    def test_login_mechanic(self):
        payload = {
            'email': 'test@test.com',
            'password': '123'
        }

        response = self.client.post('/mechanics/login', json=payload)
        self.assertEqual(response.status_code, 200)
        self.assertIn('token', response.json)

    def test_get_mechanics(self):
        response = self.client.get('/mechanics/')
        self.assertEqual(response.status_code, 200)
        self.assertGreater(len(response.json), 0)

    def test_mechanic_update(self):
        update_payload = {
            'name': 'new name',
            'email': 'new@test.com',
            'salary': 60000,
            'password': '123'
        }

        headers = {'Authorization': 'Bearer '+ self.token}
        response = self.client.put('/mechanics/1', json=update_payload, headers=headers)
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.json['name'], 'new name')