from .hub_client import HubClient


class TfClient(HubClient):
    def __init__(self):
        super(TfClient, self).__init__()

    def list_models(self, uri: str):
        raise NotImplementedError