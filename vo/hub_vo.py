class HubVO:
    def __init__(self):
        self._path =""
        self._source = ""
        self._author = ""
        self._models = []

    @property
    def path(self):
        return self._path

    @path.setter
    def path(self,value):
        self._path = value

    @property
    def source(self):
        return self._source

    @source.setter
    def source(self, value):
        self._source = value

    @property
    def author(self):
        return self._author

    @author.setter
    def author(self, value):
        self._author = value

    @property
    def models(self):
        return self._models

    @models.setter
    def models(self, value):
        self._models = value






