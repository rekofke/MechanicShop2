from flask import Flask, request, jsonify
from sqlalchemy import select
from marshmallow import ValidationError
from app.models import Customer, db
from .schemas import customer_schema, customers_schema  
from . import customers_bp



# ----- Customer Routes -----
# Create a new customer
@customers_bp.route("/", methods=["POST"])
def create_customer():
    try:
        customer_data = customer_schema.load(request.json)
    except ValidationError as e:
        return jsonify(e.messages), 400

    query = select(Customer).where(Customer.email == customer_data["email"])
    customer = db.session.execute(query).scalars().first()

    if customer:  # returns True and access if-block
        return jsonify({"error": "email already associated with another account"}), 400

    new_customer = Customer(**customer_data)

    db.session.add(new_customer)
    db.session.commit()

    return customer_schema.jsonify(new_customer), 201  # successfully created


# Get all customers
@customers_bp.route("/", methods=["GET"])
def get_customers():
    
    query = select(Customer)
    customers = db.session.execute(query).scalars().all()

    return customers_schema.jsonify(customers)

# Get a customer
@customers_bp.route('/<int:customer_id>', methods=['GET'])
def get_customer(customer_id):
    customer = db.session.get(Customer, customer_id)

    if customer:
        return customer_schema.jsonify(customer), 200
    
    return jsonify({"error": "Invalid customer ID"}), 400

# Update a customer
@customers_bp.route('/<int:customer_id>', methods=['PUT'])
def update_customer(customer_id):
    customer = db.session.get(Customer, customer_id)

    if not customer:
        return jsonify({"error": "Invalid customer ID"}), 400
    
    try:
        customer_data = customer_schema.load(request.json)
    except ValidationError as e:
        return jsonify(e.messages), 400
    
    # Check if the email already exists for another customer
    query = select(Customer).where(Customer.email == customer_data["email"])
    db.customer = db.session.execute(query).scalars().first()
    
    # If the customer exists and is not the one being updated, return an error
    if db.customer and db.customer != customer:
        return jsonify({"error": "Email already associated with another account"}), 400
    
    for fields, value in customer_data.items():
        setattr(customer, fields, value)

    db.session.commit()
    return customer_schema.jsonify(customer), 200

# Delete a customer
@customers_bp.route('/<int:customer_id>', methods=['DELETE'])
def delete_customer(customer_id):
    customer = db.session.get(Customer, customer_id)

    if not customer:
        return jsonify({"error": "Invalid customer ID"}), 400

    db.session.delete(customer)
    db.session.commit()

    return jsonify({"message": "Customer deleted successfully"}), 200