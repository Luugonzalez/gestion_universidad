from marshmallow import fields, Schema, post_load, validate
from app.models.area import Area
from markupsafe import escape

class AreaMapping(Schema):
    hashids = fields.String(attribute="hashid", dump_only=True)
    nombre = fields.String(required=True, validate=validate.Length(min=1, max=100))
    
    @post_load
    def nuevo_area(self, data, **kwargs):
        for key in ['nombre']:
            if key in data:
                data[key] = escape(data[key])
        return Area(**data)
