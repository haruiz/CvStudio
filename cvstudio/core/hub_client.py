from abc import ABCMeta, abstractmethod


class HubClient(metaclass=ABCMeta):
    @abstractmethod
    def fetch_model(self, repo: str, *args, **kwargs):
        raise NotImplementedError
