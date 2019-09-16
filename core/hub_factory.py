from .hub_client import HubClient
from .hub_provider import HubProvider
from .pytorch_client import PyTorchClient
from .tf_client import TfClient


class HubFactory:
    @classmethod
    def create(cls, provider = HubProvider.PyTorch) -> HubClient:
        if provider == HubProvider.PyTorch:
            return PyTorchClient()
        elif provider == HubProvider.TensorFlow:
            return TfClient()
        else:
            raise ModuleNotFoundError