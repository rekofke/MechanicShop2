import unittest
from app import create_app
from app.models import db, PartDescription, SerializedPart, ServiceTicket
from app.util.auth import encode_token
from werkzeug.security import generate_password_hash
from app.blueprints.serialized_parts.schemas import serialized_part_schema, serialized_parts_schema
# from app.blueprints.part_descriptions.schemas import part, part_description_schema, part_descriptions_schpart_descriptions_schema
# from app.blueprints.customers.schemas import customer_schema, customers_schema
# from app.blueprints.mechanics.schemas import mechanic_schema, mechanics_schema
from app.models import Customer, Mechanic

class TestServiceTickets(unittest.TestCase):
    def setUp(self):
        self.app = create_app('TestingConfig')
        self.client = self.app.test_client()
        
        with self.app.app_context():
            db.drop_all()
            db.create_all()        

            self.customer = Customer(
                name='test',
                email='test_customer@testme.com',
                phone='123-456-7890'
            )
            db.session.add(self.customer)
            db.session.commit()

            self.mechanic=Mechanic(
                name='test mechanic',
                email='test_mechanic@testme.com',
                salary=50000,
                password=generate_password_hash('123')

            )
            db.session.add(self.mechanic)
            db.session.commit()

            self.serialized_parts=SerializedPart(
                desc_id=1,
                ticket_id=1
            )
            db.session.add(self.serialized_parts)
            db.session.commit()

            self.service_ticket = ServiceTicket(
                service_date='2020-01-01',
                VIN='1HGCM82633A123456',
                service_desc='Test service',
                customer_id=1,
                mechanic_id=1
            )
            db.session.add(self.service_ticket)
            db.session.commit()

        def test_create_service_ticket(self):
            payload = {
                'service_date': '2020-01-01',
                'vin': '1HGCM82633A123456',
                'service_desc': 'Test service',
                'customer_id': 1
            }

            response = self.client.post('/service-tickets/', json=payload)
            self.assertEqual(response.status_code, 201)
            self.assertEqual(response.json['service_desc'], 'Test service')

        def test_get_service_tickets(self):
            response = self.client.get('/mechanics/')
            self.assertEqual(response.status_code, 200)
            self.assertGreater(len(response.json), 0)

        def test_service_ticket_update(self):
            update_payload = {
                'service_date': '2020-01-01',
                'vin': '1HGCM82633A123456',
                'service_desc': 'Test service',
                'customer_id': 1
            }

            headers = {'Authorization': 'Bearer '+ self.token}
            response = self.client.put('/service-tickets/1', json=update_payload, headers=headers)
            self.assertEqual(response.status_code, 200)
            self.assertEqual(response.json['name'], 'new name')