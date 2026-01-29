import pytorch_lightning as pl
from torch.utils.data import DataLoader, Dataset
import torch
from typing import Optional

class BaseDataModule(pl.LightningDataModule):
    """
    IMMUTABLE Base Class for data handling.
    """
    def __init__(self, data_dir: str = "/data/gankim", batch_size: int = 64, num_workers: int = 4, pin_memory: bool = True):
        super().__init__()
        self.save_hyperparameters()
        self.data_dir = data_dir
        self.batch_size = batch_size
        self.num_workers = num_workers
        self.pin_memory = pin_memory

    def prepare_data(self):
        # Download logic here
        pass

    def setup(self, stage: Optional[str] = None):
        # Split logic here
        pass

    def train_dataloader(self):
        return None # To be implemented by subclass

    def val_dataloader(self):
        return None

    def test_dataloader(self):
        return None
