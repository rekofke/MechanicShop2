import unittest
from app import create_app
from app.models import db, PartDescription
from app.util.auth import encode_token
from werkzeug.security import generate_password_hash

class Test_part_description(unittest.TestCase):
    
    def setUp(self):
        self.app = create_app('TestingConfig')
        self.part_description = PartDescription(
            part_name="test_part",
            brand="test_brand",
            price=99.99

        )
        with self.app.app_context():
            db.drop_all()
            db.create_all()
            db.session.add(self.part_description)
            db.session.commit()
        self.token = encode_token(1)
        self.client = self.app.test_client()

    def test_create_part_description(self):
        payload = {
            'part_name': 'Test part2',
            'brand': 'Test brand',
            'price': 49.99,
        }

        response = self.client.post('/part-descriptions/', json=payload)
        self.assertEqual(response.status_code, 201)
        self.assertEqual(response.json['part_name'], 'Test part2')

    def test_get_part_descriptions(self):
        response = self.client.get('/part-descriptions/')
        self.assertEqual(response.status_code, 200)
        self.assertGreater(len(response.json), 0)

    def test_part_description_update(self):
        update_payload = {
            'part_name': 'new name',
            'brand': 'new brand',
            'price': 49.99
        }

        headers = {'Authorization': 'Bearer '+ self.token}
        response = self.client.put('/part-descriptions/1', json=update_payload, headers=headers)
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.json['part_name'], 'new name')