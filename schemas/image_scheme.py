from marshmallow import Schema, fields
from .annotation_scheme import AnnotSchema


class ImageScheme(Schema):
    path = fields.Str()
    regions = fields.List(fields.Nested(AnnotSchema()))


class ImageSchemeVO:
    def __init__(self):
        self._path=None
        self._regions = []

    @property
    def path(self):
        return self._path

    @path.setter
    def path(self, value):
        self._path = value

    @property
    def regions(self):
        return self._regions

    @regions.setter
    def regions(self, value):
        self._regions = value
