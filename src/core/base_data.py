import pytorch_lightning as pl
from torch.utils.data import DataLoader, random_split
from torchvision import transforms
from torchvision.datasets import CIFAR10
from typing import Optional
import os


class BaseDataModule(pl.LightningDataModule):
    """
    IMMUTABLE Base Class for data handling.
    Agents: Inherit from this for custom datasets.
    """
    def __init__(
        self,
        data_dir: str = "/data/datasets",
        batch_size: int = 64,
        num_workers: int = 4,
        pin_memory: bool = True,
        **kwargs
    ):
        super().__init__()
        self.save_hyperparameters()
        self.data_dir = data_dir
        self.batch_size = batch_size
        self.num_workers = num_workers
        self.pin_memory = pin_memory

    def prepare_data(self):
        pass

    def setup(self, stage: Optional[str] = None):
        pass

    def train_dataloader(self):
        raise NotImplementedError("Subclass must implement train_dataloader")

    def val_dataloader(self):
        raise NotImplementedError("Subclass must implement val_dataloader")

    def test_dataloader(self):
        raise NotImplementedError("Subclass must implement test_dataloader")


class CIFAR10DataModule(BaseDataModule):
    """
    CIFAR-10 DataModule for baseline experiments.
    Downloads automatically if not present.
    """
    def __init__(
        self,
        data_dir: str = "/data/datasets",
        batch_size: int = 64,
        num_workers: int = 4,
        pin_memory: bool = True,
        val_split: float = 0.1,
        **kwargs
    ):
        super().__init__(data_dir, batch_size, num_workers, pin_memory, **kwargs)
        self.val_split = val_split
        self.train_dataset = None
        self.val_dataset = None
        self.test_dataset = None

        self.train_transform = transforms.Compose([
            transforms.RandomCrop(32, padding=4),
            transforms.RandomHorizontalFlip(),
            transforms.ToTensor(),
            transforms.Normalize((0.4914, 0.4822, 0.4465), (0.2470, 0.2435, 0.2616)),
        ])
        self.test_transform = transforms.Compose([
            transforms.ToTensor(),
            transforms.Normalize((0.4914, 0.4822, 0.4465), (0.2470, 0.2435, 0.2616)),
        ])

    def prepare_data(self):
        # Download if needed
        CIFAR10(self.data_dir, train=True, download=True)
        CIFAR10(self.data_dir, train=False, download=True)

    def setup(self, stage: Optional[str] = None):
        if stage == "fit" or stage is None:
            full_train = CIFAR10(self.data_dir, train=True, transform=self.train_transform)
            val_size = int(len(full_train) * self.val_split)
            train_size = len(full_train) - val_size
            self.train_dataset, self.val_dataset = random_split(full_train, [train_size, val_size])

        if stage == "test" or stage is None:
            self.test_dataset = CIFAR10(self.data_dir, train=False, transform=self.test_transform)

    def train_dataloader(self):
        return DataLoader(
            self.train_dataset,
            batch_size=self.batch_size,
            shuffle=True,
            num_workers=self.num_workers,
            pin_memory=self.pin_memory,
        )

    def val_dataloader(self):
        return DataLoader(
            self.val_dataset,
            batch_size=self.batch_size,
            shuffle=False,
            num_workers=self.num_workers,
            pin_memory=self.pin_memory,
        )

    def test_dataloader(self):
        return DataLoader(
            self.test_dataset,
            batch_size=self.batch_size,
            shuffle=False,
            num_workers=self.num_workers,
            pin_memory=self.pin_memory,
        )
