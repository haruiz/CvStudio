from abc import ABCMeta, abstractmethod


class ApiClient(metaclass=ABCMeta):
    @abstractmethod
    def list_models(self, *args, **kwargs):
        raise NotImplementedError

    @abstractmethod
    def build_dataset(self, dataset_id: int):
        raise NotImplementedError
