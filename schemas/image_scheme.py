from marshmallow import Schema, fields
from .annot_scheme import AnnotScheme

class ImageSchema(Schema):
    path = fields.Str()
    regions = fields.Nested(AnnotScheme)