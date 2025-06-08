import unittest
from app import create_app
from app.models import db, Customer
from marshmallow import ValidationError
from app.util.auth import encode_token


class TestCustomer(unittest.TestCase):

    def setUp(self):
        self.app = create_app('TestingConfig')
        self.customer = Customer(
            name='test',
            email='test@testing.com',
            phone='123-456-7890'
        )
        # self.customer = Customer(name='test', email='test@test.com', phone='123-456-7890')
        with self.app.app_context():
            db.drop_all()
            db.create_all()
            db.session.add(self.customer)
            db.session.commit()

        self.client = self.app.test_client()
        self.token = encode_token(1)
        self.client = self.app.test_client()

    def test_create_customer(self):
       payload = {
           "name": "Test Testly",
           "email": "unique_test@test.com",
           "phone": "123-456-7890"
       }

       response = self.client.post('/customers/', json=payload) # trailing backslash is required 
       self.assertEqual(response.status_code, 201)
       self.assertEqual(response.json['name'], "Test Testly")

    def test_create_invalid_customer(self):
        payload = {
            "name": "Test Testly",
            "phone": "123-456-7890"
        }

        response = self.client.post('/customers/', json=payload)
        self.assertRaises(ValidationError)
        self.assertEqual(response.status_code, 400)
        self.assertIn('email', response.json)
        

    def test_get_customers(self):
        response = self.client.get('/customers/')
        self.assertEqual(response.status_code, 200)
        self.assertGreater(len(response.json), 0)

    def test_customer_update(self):
        update_payload = {
            'name': 'new name',
            'email': 'new@test.com',
            'phone': '987-654-3210'
        }

        headers = {'Authorization': 'Bearer '+ self.token}
        response = self.client.put('/customers/1', json=update_payload, headers=headers)
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.json['name'], 'new name')

    # def test_delete_customer(self):
        
    #     headers = {'Authorization': 'Bearer '+ self.token}
    #     response = self.client.delete('/customers/1', headers=headers)
    #     self.assertEqual(response.status_code, 200)
    #     self.assertEqual(response.json['message'], "Customer deleted successfully")



    
