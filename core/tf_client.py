from .hub_client import HubClient


class TfClient(HubClient):
    def __init__(self):
        super(TfClient, self).__init__()

    def fetch_model(self, repo: str, *args, **kwargs):
        raise NotImplementedError
