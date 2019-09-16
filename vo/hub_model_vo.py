class HubModelVO:
    def __init__(self):
        self._name = ""
        self._description = ""
        self._hub = None
        self._downloaded=None
        self._kind=None
        
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
    
    @property
    def hub(self):
        return self._hub
    
    @hub.setter
    def hub(self, value):
        self._hub = value
    
    @property
    def downloaded(self):
        return self._downloaded
    
    @downloaded.setter
    def downloaded(self, value):
        self._downloaded = value
    
    @property
    def kind(self):
        return self._kind
    
    @kind.setter
    def kind(self, value):
        self._kind = value
    