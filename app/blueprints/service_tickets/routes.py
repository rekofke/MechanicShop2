from flask import Flask, request, jsonify
from sqlalchemy import select
from marshmallow import ValidationError
from .schemas import service_ticket_schema, service_tickets_schema
from . import service_tickets_bp
from app.models import ServiceTicket, Customer, db, Mechanic
from app.blueprints.mechanics.schemas import mechanic_schema, mechanics_schema
from app.extensions import limiter
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

    customer = db.session.get(Customer, service_ticket_data['customer_id'])

    new_service_ticket = ServiceTicket(**service_ticket_data)
    db.session.add(new_service_ticket)
    db.session.commit()
    return service_ticket_schema.jsonify(new_service_ticket), 201  # successfully created

# Get all service_tickets
@service_tickets_bp.route("/", methods=["GET"])
@limiter.exempt
def get_service_tickets():
    
    query = select(ServiceTicket)
    service_tickets = db.session.execute(query).scalars().all()

    return service_tickets_schema.jsonify(service_tickets)

# Get a service_ticket
@service_tickets_bp.route('/<int:service_ticket_id>', methods=['GET'])
@limiter.exempt
def get_service_ticket(service_ticket_id):
    service_ticket = db.session.get(ServiceTicket, service_ticket_id)

    if service_ticket:
        return service_ticket_schema.jsonify(service_ticket), 200
    
    return jsonify({"error": "Invalid service_ticket ID"}), 400

# Add a mechanic to a service_ticket
@service_tickets_bp.route('/<int:service_ticket_id>/add-mechanic/<int:mechanic_id>', methods=['POST'])
@limiter.limit("25/hour")
def add_mechanic(service_ticket_id, mechanic_id):
    ticket = db.session.get(ServiceTicket, service_ticket_id)
    mechanic = db.session.get(Mechanic, mechanic_id)
    
    if ticket and mechanic:
        if mechanic not in ticket.mechanics:
            ticket.mechanics.append(mechanic)
            db.session.commit()
            return jsonify({
                'message': f'Successfully added mechanic {mechanic.name} to service ticket {service_ticket_id}',
                'ticket': service_ticket_schema.dump(ticket),
                'mechanic': mechanics_schema.dump(ticket.mechanics)}), 200
        return jsonify({'error': 'Mechanic already assigned to this service ticket'}), 400
    return jsonify({'error': 'Invalid service ticket or mechanic ID'}), 400

# Update a service_ticket
@service_tickets_bp.route('/<int:service_ticket_id>', methods=['PUT'])
@limiter.limit("5/hour")
def update_service_ticket(service_ticket_id):
    service_ticket = db.session.get(ServiceTicket, service_ticket_id)

    if not service_ticket:
        return jsonify({"error": "Invalid service_ticket ID"}), 400

    try:
        service_ticket_data = service_ticket_schema.load(request.json)
    except ValidationError as e:
        return jsonify(e.messages), 400

    query = select(ServiceTicket).where(
        (ServiceTicket.VIN == service_ticket_data["VIN"]) &
        (ServiceTicket.service_date == service_ticket_data["service_date"]) &
        (ServiceTicket.id != service_ticket_id)
    )
    existing_ticket = db.session.execute(query).scalars().first()

    if existing_ticket:
        return jsonify({"error": "Service ticket already exists for this VIN on the specified date"}), 400

    for fields, value in service_ticket_data.items():
        setattr(service_ticket, fields, value)

    db.session.commit()
    return service_ticket_schema.jsonify(service_ticket), 200

# Delete a service_ticket
@service_tickets_bp.route('/<int:service_ticket_id>', methods=['DELETE'])
@limiter.limit("5/hour")
def delete_service_ticket(service_ticket_id):
    service_ticket = db.session.get(ServiceTicket, service_ticket_id)

    if not service_ticket:
        return jsonify({"error": "Invalid service_ticket ID"}), 400

    db.session.delete(service_ticket)
    db.session.commit()

    return jsonify({"message": "service_ticket deleted successfully"}), 200
