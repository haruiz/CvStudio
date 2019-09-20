from marshmallow import Schema, fields
from .image_scheme import ImageSchema

class DatasetSchema(Schema):
    name = fields.Str()
    regions = fields.Nested(ImageSchema)