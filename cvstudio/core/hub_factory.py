from .framework import Framework
from .hub_client import HubClient
from .pytorch_hub_client import PyTorchHubClient
from .tf_hub_client import TfHubClient


class HubClientFactory:
    @classmethod
    def create(cls, provider=Framework.PyTorch) -> HubClient:
        if provider == Framework.PyTorch:
            return PyTorchHubClient()
        elif provider == Framework.TensorFlow:
            return TfHubClient()
        else:
            raise ModuleNotFoundError
