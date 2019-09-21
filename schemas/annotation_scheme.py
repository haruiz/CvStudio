from marshmallow import Schema, fields


class AnnotSchema(Schema):
    kind = fields.Str()
    points = fields.Str()
    label_name = fields.Str()
    label_color = fields.Str()


class AnnotSchemeVO:
    def __init__(self):
        self._kind = None
        self._points = None
        self._label_name = None
        self._label_color = None

    @property
    def kind(self):
        return self._kind

    @kind.setter
    def kind(self, value):
        self._kind = value

    @property
    def points(self):
        return self._points

    @points.setter
    def points(self, value):
        self._points = value

    @property
    def label_name(self):
        return self._label_name

    @label_name.setter
    def label_name(self, value):
        self._label_name = value

    @property
    def label_color(self):
        return self._label_color

    @label_color.setter
    def label_color(self, value):
        self._label_color = value




