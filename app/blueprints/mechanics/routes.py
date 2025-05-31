from flask import Flask, request, jsonify
from sqlalchemy import select
from marshmallow import ValidationError
from .schemas import mechanic_schema, mechanics_schema  
from . import mechanics_bp
from app.models import Mechanic, db


# ----- Mechanic Routes -----
# Create a new mechanic
@mechanics_bp.route("/", methods=["POST"])
def create_mechanic():
    try:
        mechanic_data = mechanic_schema.load(request.json)
    except ValidationError as e:
        return jsonify(e.messages), 400

    query = select(Mechanic).where(Mechanic.email == mechanic_data["email"])
    mechanic = db.session.execute(query).scalars().first()

    if mechanic:
        return jsonify({"error": "Email already taken"}), 400
    

    new_mechanic = Mechanic(**mechanic_data)
    db.session.add(new_mechanic)
    db.session.commit()

    return mechanic_schema.jsonify(new_mechanic), 201  # successfully created

# Get all mechanics
@mechanics_bp.route("/", methods=["GET"])
def get_mechanics():
    
    query = select(Mechanic)
    mechanics = db.session.execute(query).scalars().all()

    return mechanics_schema.jsonify(mechanics), 200

# Get a mechanic
@mechanics_bp.route('/<int:mechanic_id>', methods=['GET'])
def get_mechanic(mechanic_id):
    mechanic = db.session.get(Mechanic, mechanic_id)

    if mechanic:
        return mechanic_schema.jsonify(mechanic), 200
    
    return jsonify({"error": "Invalid mechanic ID"}), 400

# Update a mechanic
@mechanics_bp.route('/<int:mechanic_id>', methods=['PUT'])
def update_mechanic(mechanic_id):
    mechanic = db.session.get(Mechanic, mechanic_id)

    if not mechanic:
        return jsonify({"error": "Invalid mechanic ID"}), 400
    
    try:
        mechanic_data = mechanic_schema.load(request.json)
    except ValidationError as e:
        return jsonify(e.messages), 400
    
    # Check if the email already exists for another mechanic
    query = select(Mechanic).where(Mechanic.email == mechanic_data["email"])
    db.mechanic = db.session.execute(query).scalars().first()
    
    # If the mechanic exists and is not the one being updated, return an error
    if db.mechanic and db.mechanic != mechanic:
        return jsonify({"error": "Email already associated with another account"}), 400
    
    for fields, value in mechanic_data.items():
        setattr(mechanic, fields, value)

    db.session.commit()
    return mechanic_schema.jsonify(mechanic), 200

# Delete a mechanic
# Delete a mechanic
@mechanics_bp.route('/<int:mechanic_id>', methods=['DELETE'])
def delete_mechanic(mechanic_id):
    mechanic = db.session.get(Mechanic, mechanic_id)

    if not mechanic:
        return jsonify({"error": "Invalid mechanic ID"}), 400

    db.session.delete(mechanic)
    db.session.commit()

    return jsonify({"message": "mechanic deleted successfully"}), 200