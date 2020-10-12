class DatasetVO:
    def __init__(self):
        self._id = None
        self._name = ""
        self._folder = ""
        self._description = ""
        self._data_type = ""
        self._size = 0
        self._count = 0

    @property
    def count(self):
        return self._count

    @count.setter
    def count(self, value):
        if self._size and self._size > 0:
            self._count = value
        else:
            self._count = 0

    @property
    def size(self):
        return self._size

    @size.setter
    def size(self, value):
        self._size = value

    @property
    def id(self):
        return self._id

    @id.setter
    def id(self, value):
        self._id = value

    @property
    def name(self):
        return self._name

    @name.setter
    def name(self, value):
        self._name = value

    @property
    def description(self):
        return self._description

    @description.setter
    def description(self, value):
        self._description = value

