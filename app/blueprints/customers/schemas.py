from app.extensions import ma
from app.models import Customer

# Customer Schema
class CustomerSchema(ma.SQLAlchemyAutoSchema):
    class Meta:
        model = Customer
        include_relationships = True


customer_schema = CustomerSchema()
customers_schema = CustomerSchema(many=True)