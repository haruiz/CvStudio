from .hub_client import HubClient


class TfHubClient(HubClient):
    def __init__(self):
        super(TfHubClient, self).__init__()

    def fetch_model(self, repo: str, *args, **kwargs):
        raise NotImplementedError
