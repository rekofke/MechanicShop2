from functools import cache
from flask import Flask, request, jsonify
from sqlalchemy import select
from marshmallow import ValidationError
from .schemas import service_ticket_schema, service_tickets_schema
from . import service_tickets_bp
from app.models import Customer, db, Mechanic, PartDescription, SerializedPart, ServiceTicket
from app.blueprints.mechanics.schemas import mechanic_schema, mechanics_schema
from app.blueprints.serialized_parts.schemas import (
    serialized_part_schema,
    serialized_parts_schema,
)
from app.blueprints.serialized_parts.schemas import serialized_part_schema
from app.extensions import limiter, cache
from app.util.auth import token_required, admin_required


# ----- Service Ticket Routes -----
# Create a new service ticket
@service_tickets_bp.route("/", methods=["POST"])
@limiter.limit("25/hour")
@admin_required
def create_ServiceTicket():
    try:
        service_ticket_data = service_ticket_schema.load(request.json)
    except ValidationError as e:
        return jsonify(e.messages), 400

    customer = db.session.get(Customer, service_ticket_data["customer_id"])

    new_service_ticket = ServiceTicket(**service_ticket_data)
    db.session.add(new_service_ticket)
    db.session.commit()
    return service_ticket_schema.jsonify(
        new_service_ticket
    ), 201  # successfully created


# Get all service_tickets
@service_tickets_bp.route("/", methods=["GET"])
@limiter.exempt
def get_service_tickets():
    try:
        page = int(request.args.get("page"))
        per_page = int(request.args.get("per_page"))
        query = select(ServiceTicket)
        service_tickets = db.paginate(query, page=page, per_page=per_page)
        return service_tickets_schema.jsonify(service_tickets), 200
    except:
        query = select(ServiceTicket)
    service_tickets = db.session.execute(query).scalars().all()

    if service_tickets:
        return service_tickets_schema.jsonify(service_tickets), 200
    return jsonify({"error": "No service_tickets found"}), 404


# Get a service_ticket
@service_tickets_bp.route("/<int:service_ticket_id>", methods=["GET"])
@limiter.exempt
@cache.cached(timeout=30)
def get_service_ticket(service_ticket_id):
    service_ticket = db.session.get(ServiceTicket, service_ticket_id)

    if service_ticket:
        return service_ticket_schema.jsonify(service_ticket), 200

    return jsonify({"error": "Invalid service_ticket ID"}), 400


# Add a mechanic to a service_ticket
@service_tickets_bp.route("/<int:service_ticket_id>/add-mechanic/<int:mechanic_id>", methods=["PUT"])
@limiter.limit("25/hour")
@admin_required
def add_mechanic(service_ticket_id, mechanic_id):
    ticket = db.session.get(ServiceTicket, service_ticket_id)
    mechanic = db.session.get(Mechanic, mechanic_id)

    if ticket and mechanic:
        if mechanic not in ticket.mechanics:
            ticket.mechanics.append(mechanic)
            db.session.commit()
            return jsonify(
                {
                    "message": f"Successfully added mechanic {mechanic.name} to service ticket {service_ticket_id}",
                    "ticket": service_ticket_schema.dump(ticket),
                    "mechanic": mechanics_schema.dump(ticket.mechanics),
                }
            ), 200
        return jsonify(
            {"error": "Mechanic already assigned to this service ticket"}
        ), 400
    return jsonify({"error": "Invalid service ticket or mechanic ID"}), 400


# Remove a mechanic from a service_ticket
@service_tickets_bp.route(
    "/<int:service_ticket_id>/remove-mechanic/<int:mechanic_id>", methods=["DELETE"]
)
def remove_mechanic(service_ticket_id, mechanic_id):
    ticket = db.session.get(ServiceTicket, service_ticket_id)
    mechanic = db.session.get(Mechanic, mechanic_id)

    if ticket and mechanic:
        if mechanic in ticket.mechanics:
            ticket.mechanics.remove(mechanic)
            db.session.commit()
            return jsonify(
                {
                    "message": f"successfully removed {mechanic.name} from the ticket",
                    "ticket": service_ticket_schema.dump(ticket),
                    "mechanic": mechanics_schema.dump(ticket.mechanics),
                }
            ), 200
        return jsonify({"error": "Mechanic not assigned to this service ticket"}), 400
    return jsonify({"error": "Invalid service ticket or mechanic ID"}), 400


# Update a service_ticket
@service_tickets_bp.route("/<int:service_ticket_id>", methods=["PUT"])
@limiter.limit("5/hour")
@admin_required
def update_service_ticket(service_ticket_id):
    service_ticket = db.session.get(ServiceTicket, service_ticket_id)

    if not service_ticket:
        return jsonify({"error": "Invalid service_ticket ID"}), 400

    try:
        service_ticket_data = service_ticket_schema.load(request.json)
    except ValidationError as e:
        return jsonify(e.messages), 400

    query = select(ServiceTicket).where(
        (ServiceTicket.VIN == service_ticket_data["VIN"])
        & (ServiceTicket.service_date == service_ticket_data["service_date"])
        & (ServiceTicket.id != service_ticket_id)
    )
    existing_ticket = db.session.execute(query).scalars().first()

    if existing_ticket:
        return jsonify(
            {
                "error": "Service ticket already exists for this VIN on the specified date"
            }
        ), 400

    for fields, value in service_ticket_data.items():
        setattr(service_ticket, fields, value)

    db.session.commit()
    return service_ticket_schema.jsonify(service_ticket), 200


# Delete a service_ticket
@service_tickets_bp.route("/<int:service_ticket_id>", methods=["DELETE"])
@limiter.limit("5/hour")
@admin_required
def delete_service_ticket(service_ticket_id):
    service_ticket = db.session.get(ServiceTicket, service_ticket_id)

    if not service_ticket:
        return jsonify({"error": "Invalid service_ticket ID"}), 400

    db.session.delete(service_ticket)
    db.session.commit()

    return jsonify({"message": "service_ticket deleted successfully"}), 200


# Add a part to a service_ticket
@service_tickets_bp.route("/<int:ticket_id>/add-part/<int:part_id>", methods=["PUT"])
def add_part(ticket_id, part_id):
    ticket = db.session.get(ServiceTicket, ticket_id)
    part = db.session.get(SerializedPart, part_id)

    if ticket and part:
        if not part.ticket_id:
            ticket.serialized_parts.append(part)
            db.session.commit()
            return jsonify(
                {
                    "message": f"successfully added part to the ticket",
                    "ticket": service_ticket_schema.dump(ticket),
                    "parts": serialized_parts_schema.dump(ticket.serialized_parts),
                }
            ), 200
        return jsonify(
            {"error": "This part has already been used in another service ticket"}
        ), 400
    return jsonify({"error": "Invalid service ticket or part ID"}), 400


# Remove a serialized part from a service_ticket
@service_tickets_bp.route("/<int:ticket_id>/remove-part/<int:part_id>", methods=["DELETE"])
def remove_part(ticket_id, part_id):
    ticket = db.session.get(ServiceTicket, ticket_id)
    part = db.session.get(SerializedPart, part_id)

    if ticket and part:
        if not part.ticket_id:
            ticket.serialized_parts.remove(part)
            db.session.commit()
            return jsonify(
                {
                    "message": f"successfully removed part from the ticket",
                    "ticket": service_ticket_schema.dump(ticket),
                    "parts": serialized_parts_schema.dump(ticket.serialized_parts),
                }
            ), 200
        return jsonify({"error": "Part not assigned to this service ticket"}), 400
    return jsonify({"error": "Invalid service ticket or part ID"}), 400

@service_tickets_bp.route("/<int:ticket_id>/add-to-cart/<int:description_id>", methods=["PUT"])
def add_to_cart(ticket_id, description_id):
    ticket = db.session.get(ServiceTicket, ticket_id)
    description = db.session.get(PartDescription, description)

    parts = description.serialized_parts

    for part in parts:
        if not part.ticket_id:
            ticket.serializd_parts.append(part)
            return jsonify(
                {
                    "message": f"successfully added part to the ticket",
                    "ticket": service_ticket_schema.dump(ticket),
                    "parts": serialized_parts_schema.dump(ticket.serialized_parts),
                }
            ), 200
        

