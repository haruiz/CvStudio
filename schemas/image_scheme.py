from marshmallow import Schema, fields
from .annotation_scheme import AnnotationScheme


class ImageSchema(Schema):
    path = fields.Str()
    regions = fields.Nested(AnnotationScheme)
