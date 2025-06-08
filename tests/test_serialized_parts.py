import unittest
from app import create_app
from app.models import db, PartDescription, SerializedPart, ServiceTicket, Customer
from app.util.auth import encode_token
from werkzeug.security import generate_password_hash
from datetime import date


class TestSerializedPart(unittest.TestCase):  # Fixed class name convention
    
    def setUp(self):
        self.app = create_app('TestingConfig')
        self.client = self.app.test_client()
        
        with self.app.app_context():
            db.drop_all()
            db.create_all()
            
            # Create customer 
            self.customer = Customer(
                name="Test Customer",
                email="customer@test.com",
                phone="123-456-7890"
            )
            db.session.add(self.customer)
            db.session.commit()

            self.customer_id = self.customer.id
            
            # Create part description
            self.part_description = PartDescription(
                part_name="test_part",
                brand="test_brand",
                price=99.99
            )
            db.session.add(self.part_description)
            db.session.commit()
            
            # Create service ticket
            self.service_ticket = ServiceTicket(
                service_date=date(2023, 10, 1),
                VIN='1HGCM82633A123456',
                service_desc='Test service',
                customer_id=self.customer.id  
            )
            db.session.add(self.service_ticket)
            db.session.commit()
            
            # Create serialized part using IDs
            self.serialized_part = SerializedPart(
                desc_id=self.part_description.id,
                ticket_id=self.service_ticket.id
            )
            db.session.add(self.serialized_part)
            db.session.commit()
            
        self.token = encode_token(1)

    # def test_create_serialized_part(self):
    #     with self.app.app_context():
    #         # Create new part description
    #         new_part_desc = PartDescription(
    #             part_name="new_part",
    #             brand="new_brand",
    #             price=49.99
    #         )
    #         db.session.add(new_part_desc)
            
    #         # Create new service ticket
    #         new_ticket = ServiceTicket(
    #             service_date=date(2021, 10, 1),
    #             VIN='2HGCM82633A654321',
    #             service_desc='New service',
    #             customer_id=self.customer_id 
    #         )
    #         db.session.add(new_ticket)
    #         db.session.commit()

    #         payload = {
    #             'desc_id': new_part_desc.id,
    #             'ticket_id': new_ticket.id
    #         }

    #         headers = {'Authorization': f'Bearer {self.token}'}
    #         response = self.client.post('/serialized-parts/', json=payload, headers=headers)
            
    #         if response.status_code != 200:
    #             print(f"Test failed with response: {response.json}")
                
    #         self.assertEqual(response.status_code, 201)
    #         self.assertEqual(response.json['desc_id'], new_part_desc.id)
    #         self.assertEqual(response.json['ticket_id'], new_ticket.id)

    def test_get_serialized_parts(self):
        response = self.client.get('/serialized-parts/')
        self.assertEqual(response.status_code, 200)
        self.assertGreater(len(response.json), 0)

    def test_serialized_part_update(self):
        update_payload = {
            'desc_id': 1,
            'ticket_id': 1
        }

        headers = {'Authorization': 'Bearer '+ self.token}
        response = self.client.put('/serialized-parts/1', json=update_payload, headers=headers)
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.json['desc_id'], 1)