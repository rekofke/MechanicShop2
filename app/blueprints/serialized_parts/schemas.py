from app.extensions import ma
from app.models import SerializedPart

# Customer Schema
class SerializedPartSchema(ma.SQLAlchemyAutoSchema):
    class Meta:
        model = SerializedPart
        include_fk = True


serialized_part_schema = SerializedPartSchema()
serialized_parts_schema = SerializedPartSchema(many=True)