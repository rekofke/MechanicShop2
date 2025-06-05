from flask import Flask, request, jsonify
from sqlalchemy import select
from marshmallow import ValidationError
from app.models import db, PartDescription
from .schemas import part_description_schema, part_descriptions_schema  
from . import part_descriptions_bp
from app.extensions import limiter, cache


# ----- part_description Routes -----
# Create a new part_description
@part_descriptions_bp.route("/", methods=["POST"])
@limiter.limit("25/hour")
def create_part_description():
    try:
        part_description_data = part_description_schema.load(request.json)
    except ValidationError as e:
        return jsonify(e.messages), 400

    new_part_description = PartDescription(**part_description_data)

    db.session.add(new_part_description)
    db.session.commit()

    return part_description_schema.jsonify(new_part_description), 201  # successfully created


# Get all part_descriptions
@part_descriptions_bp.route("/", methods=["GET"])
@limiter.exempt
def get_part_descriptions():
    try:
        page = int(request.args.get('page'))
        per_page = int(request.args.get('per_page'))
        query = select(PartDescription)
        part_descriptions = db.paginate(query, page=page, per_page=per_page)
        return part_descriptions_schema.jsonify(part_descriptions), 200
    except:
        query = select(PartDescription)
    part_descriptions = db.session.execute(query).scalars().all()

    if part_descriptions:
        return part_descriptions_schema.jsonify(part_descriptions), 200
    return jsonify({"error": "No part_descriptions found"}), 404

# Get a part_description
@part_descriptions_bp.route('/<int:part_description_id>', methods=['GET'])
@limiter.exempt
@cache.cached(timeout=30)
def get_part_description(part_description_id):
    part_description = db.session.get(PartDescription, part_description_id)

    if part_description:
        return part_description_schema.jsonify(part_description), 200
    
    return jsonify({"error": "Invalid part_description ID"}), 400

# Update a part_description
@part_descriptions_bp.route('/<int:part_description_id>', methods=['PUT'])
@limiter.limit("5/hour")
def update_part_description(part_description_id):
    part_description = db.session.get(PartDescription, part_description_id)

    if not part_description:
        return jsonify({"error": "Invalid part_description ID"}), 400
    
    try:
        part_description_data = part_description_schema.load(request.json)
    except ValidationError as e:
        return jsonify(e.messages), 400
    
    for fields, value in part_description_data.items():
        setattr(part_description, fields, value)

    db.session.commit()
    return part_description_schema.jsonify(part_description), 200

# Delete a part_description
@part_descriptions_bp.route('/<int:part_description_id>', methods=['DELETE'])
@limiter.limit("5/hour")
def delete_part_description(part_description_id):
    part_description = db.session.get(PartDescription, part_description_id)

    if not part_description:
        return jsonify({"error": "Invalid part_description ID"}), 400

    db.session.delete(part_description)
    db.session.commit()

    return jsonify({"message": "part_description deleted successfully"}), 200

# Path query to find most valuable part_description
@part_descriptions_bp.route('/most-valuable', methods=['GET'])
def get_most_valuable():
    # return list of part_descriptions with the most service tickets

    query = select(PartDescription)
    part_descriptions = db.session.execute(query).scalars().all()

    part_descriptions.sort(key=lambda part_description: len(part_description.tickets),reverse=True)

    return part_descriptions_schema.jsonify(part_descriptions), 200  

# Query parameter to search part_description by email
@part_descriptions_bp.route('/search', methods=['GET'])
def search_by_part_name():
    name = request.args.get('name')

    #* search for exact email
    # query = select(part_description).where(part_description.email == email)
    #* search for part of email
    query = select(part_description).where(part_description.part_name.like(f"%{name}%"))
    part_description = db.session.execute(query).scalars().first()

    return part_description_schema.jsonify(part_description), 200 



