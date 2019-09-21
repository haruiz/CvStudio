from marshmallow import Schema, fields


class TagSchema(Schema):
    annot_kind = fields.Str()
    annot_points = fields.Str()
    label_name = fields.Str()
    label_color = fields.Str()


class AnnotationScheme(Schema):
    image = fields.Str()
    anns = fields.List(fields.Nested(TagSchema()))
