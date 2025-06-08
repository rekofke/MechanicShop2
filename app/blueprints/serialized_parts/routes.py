from flask import Flask, request, jsonify
from sqlalchemy import select
from marshmallow import ValidationError
from app.models import PartDescription, db, SerializedPart
from app.blueprints.part_descriptions import part_descriptions_bp
from .schemas import serialized_part_schema, serialized_parts_schema  
from . import serialized_parts_bp
from app.extensions import limiter, cache


# ----- serialized_part Routes -----
# Create a new serialized_part
@serialized_parts_bp.route("/", methods=["POST"])
@limiter.limit("25/hour")
def create_serialized_part():
    try:
        serialized_part_data = serialized_part_schema.load(request.json)
    except ValidationError as e:
        return jsonify(e.messages), 400

    new_serialized_part = SerializedPart(**serialized_part_data)

    db.session.add(new_serialized_part)
    db.session.commit()

    return jsonify({
        "message": f"Added new {new_serialized_part.description.brand} {new_serialized_part.description.part_name} to database",
        "part": serialized_part_schema.dump(new_serialized_part)
    }), 201


# Get all serialized_parts
@serialized_parts_bp.route("/", methods=["GET"])
@limiter.exempt
def get_serialized_parts():
    try:
        page = int(request.args.get('page'))
        per_page = int(request.args.get('per_page'))
        query = select(SerializedPart)
        serialized_parts = db.paginate(query, page=page, per_page=per_page)
        return serialized_parts_schema.jsonify(serialized_parts), 200
    except:
        query = select(SerializedPart)
    serialized_parts = db.session.execute(query).scalars().all()

    if serialized_parts:
        return serialized_parts_schema.jsonify(serialized_parts), 200
    return jsonify({"error": "No serialized_parts found"}), 404

# Get a serialized_part
@serialized_parts_bp.route('/<int:serialized_part_id>', methods=['GET'])
@limiter.exempt
@cache.cached(timeout=30)
def get_serialized_part(serialized_part_id):
    serialized_part = db.session.get(SerializedPart, serialized_part_id)

    if serialized_part:
        return serialized_part_schema.jsonify(serialized_part), 200
    
    return jsonify({"error": "Invalid serialized_part ID"}), 400

# Update a serialized_part
@serialized_parts_bp.route('/<int:serialized_part_id>', methods=['PUT'])
@limiter.limit("5/hour")
def update_serialized_part(serialized_part_id):
    serialized_part = db.session.get(SerializedPart, serialized_part_id)

    if not serialized_part:
        return jsonify({"error": "Invalid serialized_part ID"}), 400
    
    try:
        serialized_part_data = serialized_part_schema.load(request.json)
    except ValidationError as e:
        return jsonify(e.messages), 400
    
    for fields, value in serialized_part_data.items():
        setattr(serialized_part, fields, value)

    db.session.commit()
    return serialized_part_schema.jsonify(serialized_part), 200

# Delete a serialized_part
@serialized_parts_bp.route('/<int:serialized_part_id>', methods=['DELETE'])
@limiter.limit("5/hour")
def delete_serialized_part(serialized_part_id):
    serialized_part = db.session.get(SerializedPart, serialized_part_id)

    if not serialized_part:
        return jsonify({"error": "Invalid serialized_part ID"}), 400

    db.session.delete(serialized_part)
    db.session.commit()

    return jsonify({"message": "serialized_part deleted successfully"}), 200

# Path query to find most valuable serialized_part
@serialized_parts_bp.route('/most-valuable', methods=['GET'])
def get_most_valuable():
    # return list of serialized_parts with the most service tickets

    query = select(SerializedPart)
    serialized_parts = db.session.execute(query).scalars().all()

    serialized_parts.sort(key=lambda serialized_part: len(serialized_part.tickets),reverse=True)

    return serialized_parts_schema.jsonify(serialized_parts), 200  

# Find on hand amount of part by description ID
@serialized_parts_bp.route("/stock/<int:description_id>", methods=["GET"])
def get_individual_stock(description_id):
    part_description = db.session.get(PartDescription, description_id)

    parts = part_description.serialized_parts

    count = 0
    for part in parts:
        if not part.ticket_id:
            count += 1

    return jsonify(
        {"item": part_description.part_name,
        "quantity": count

    }
    )





