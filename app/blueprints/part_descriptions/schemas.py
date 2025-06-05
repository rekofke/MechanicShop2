from app.extensions import ma
from app.models import PartDescription

# Customer Schema
class PartDescriptionSchema(ma.SQLAlchemyAutoSchema):
    class Meta:
        model = PartDescription
        include_relationships = True


part_description_schema = PartDescriptionSchema()
part_descriptions_schema = PartDescriptionSchema(many=True)