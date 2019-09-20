from vo import HubVO, HubModelVO
from .hub_client import HubClient
import torch.hub


class PyTorchClient(HubClient):
    def __init__(self):
        super(PyTorchClient, self).__init__()

    def fetch_model(self, repo: str, *args, **kwargs):
        try:
            hub = HubVO()
            hub.path = repo
            force_reload = False
            if "force_reload" in kwargs:
                force_reload = kwargs["force_reload"]
            entry_points_list = torch.hub.list(repo, force_reload=force_reload)
            for entry_point in entry_points_list:
                model = HubModelVO()
                model.name = entry_point
                hub.models.append(model)
            return hub
        except Exception as ex:
            print(ex)
            return None
