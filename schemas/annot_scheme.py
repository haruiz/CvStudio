from marshmallow import Schema, fields
class AnnotScheme(Schema):
    label = fields.Str()
    points = fields.List(fields.Integer)
    kind = fields.Str()
