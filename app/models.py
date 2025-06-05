from flask_sqlalchemy import SQLAlchemy
from sqlalchemy.orm import DeclarativeBase, Mapped, mapped_column
from datetime import date
from typing import List


class Base(DeclarativeBase):
    pass

db = SQLAlchemy(model_class=Base)

service_mechanic = db.Table(
    "service_mechanic",
    Base.metadata,
    db.Column("ticket_id", db.ForeignKey("service_tickets.id")),
    db.Column("mechanic_id", db.ForeignKey("mechanics.id")),
)

# * ---------- Models ----------
class Customer(Base):
    __tablename__ = "customers"
 
    id: Mapped[int] = mapped_column(primary_key=True)
    name: Mapped[str] = mapped_column(db.String(255), nullable=False)
    email: Mapped[str] = mapped_column(db.String(320), nullable=False, unique=True)
    phone: Mapped[str] = mapped_column(db.String(16), nullable=False)

    tickets: Mapped[List["ServiceTicket"]] = db.relationship(back_populates="customer", cascade="all, delete-orphan", passive_deletes=True)

class Mechanic(Base):
    __tablename__ = "mechanics"

    id: Mapped[int] = mapped_column(primary_key=True)
    name: Mapped[str] = mapped_column(db.String(255), nullable=False)
    email: Mapped[str] = mapped_column(db.String(320), nullable=False, unique=True)
    salary: Mapped[float] = mapped_column(db.Float(), nullable=False)
    password: Mapped[str] = mapped_column(db.String(255), nullable=False)

    tickets: Mapped[List["ServiceTicket"]] = db.relationship(secondary=service_mechanic, back_populates="mechanics")

class ServiceTicket(Base):
    __tablename__ = "service_tickets"

    id: Mapped[int] = mapped_column(primary_key=True)
    service_date: Mapped[date]
    VIN: Mapped[str] = mapped_column(db.String(17), nullable=False)
    service_desc: Mapped[str] = mapped_column(db.String(500), nullable=False)
    customer_id: Mapped[int] = mapped_column(db.ForeignKey("customers.id"), nullable=False)

    customer: Mapped["Customer"] = db.relationship(back_populates="tickets")
    mechanics: Mapped[List["Mechanic"]] = db.relationship(secondary=service_mechanic, back_populates="tickets")
    serialized_parts: Mapped[List["SerializedPart"]] = db.relationship(back_populates="ticket")

class PartDescription(Base):
    __tablename__ = "part_descriptions"

    id: Mapped[int] = mapped_column(primary_key=True)
    part_name: Mapped[str] = mapped_column(db.String(255), nullable=False)
    brand: Mapped[str] = mapped_column(db.String(255), nullable=False)
    price: Mapped[float] = mapped_column(db.Float(), nullable=False)

    serialized_parts: Mapped[List["SerializedPart"]] = db.relationship(back_populates="description")

class SerializedPart(Base):
    __tablename__ = "serialized_parts"

    id: Mapped[int] = mapped_column(primary_key=True)
    desc_id: Mapped[int] = mapped_column(db.ForeignKey("part_descriptions.id"), nullable=False)
    ticket_id: Mapped[int] = mapped_column(db.ForeignKey("service_tickets.id"), nullable=True)

    description: Mapped["PartDescription"] = db.relationship(back_populates="serialized_parts")
    ticket: Mapped["ServiceTicket"] = db.relationship(back_populates="serialized_parts")