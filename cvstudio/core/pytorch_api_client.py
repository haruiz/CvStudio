# Ignore warnings
import warnings

import torch
from PIL import Image
from torch.utils.data import Dataset, DataLoader

from cvstudio.dao import DatasetDao
from .api_client import ApiClient

warnings.filterwarnings("ignore")


class PytorchCVDataset(Dataset):
    def __init__(self, dataset_id):
        self.ds_dao = DatasetDao()
        self.entries = self.ds_dao.fetch_entries_for_classification(dataset_id)

    def __len__(self):
        return len(self.entries)

    def __getitem__(self, idx):
        if torch.is_tensor(idx):
            idx = idx.tolist()
        image_path = self.entries[idx]["file_path"]
        image_label = self.entries[idx]["label"]
        image_array = Image.open(image_path)
        return image_array, image_label


class PytorchApiClient(ApiClient):
    def __init__(self):
        super(PytorchApiClient, self).__init__()

    def list_models(self, *args, **kwargs):
        import torchvision.models as models
        model_names = sorted(name for name in models.__dict__
                             if name.islower() and not name.startswith("__")
                             and callable(models.__dict__[name]))
        # models = inspect.getmembers(models, inspect.isclass)
        # model_name = {mname: mclass.__doc__ for mname,mclass in models}
        return model_names

    def build_dataset(self, dataset_id: int) -> DataLoader:
        dataset = PytorchCVDataset(dataset_id)
        return DataLoader(dataset, batch_size=256, shuffle=True, num_workers=4)
