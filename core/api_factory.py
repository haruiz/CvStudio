from .api_client import ApiClient
from .framework import Framework
from .pytorch_api_client import PytorchApiClient


class ApiClientFactory:
    @classmethod
    def create(cls,provider=Framework.PyTorch) -> ApiClient:
        if provider == Framework.PyTorch:
            return PytorchApiClient()
        elif provider == Framework.TensorFlow:
            raise NotImplementedError
        else:
            raise ModuleNotFoundError