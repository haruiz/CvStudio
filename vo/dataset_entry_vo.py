class DatasetEntryVO:
    def __init__(self):
        self._id = None
        self._file_path =""
        self._file_size = ""
        self._dataset = ""

    @property
    def id(self):
        return self._id

    @id.setter
    def id(self, value):
        self._id = value

    @property
    def file_path(self):
        return self._file_path

    @file_path.setter
    def file_path(self,value):
        self._file_path = value

    @property
    def file_size(self):
        return self._file_size

    @file_size.setter
    def file_size(self, value):
        self._file_size = value

    @property
    def dataset(self):
        return self._dataset

    @dataset.setter
    def dataset(self, value):
        self._dataset = value

    def to_array(self):
        return [self.file_path,self.file_size,self.dataset]
