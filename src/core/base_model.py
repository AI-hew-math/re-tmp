import pytorch_lightning as pl
import torch
import torch.nn as nn
from typing import Any, Dict

class BaseModel(pl.LightningModule):
    """
    IMMUTABLE Base Class for all models.
    Agents: You MUST inherit from this. Do not modify the train/val/test loops 
    unless absolutely necessary for the research.
    """
    def __init__(self, lr: float = 1e-3, weight_decay: float = 1e-5, **kwargs):
        super().__init__()
        self.save_hyperparameters()
        self.lr = lr
        self.weight_decay = weight_decay
        
        # Default architecture - intended to be overridden by subclasses
        self.net = nn.Identity()
        self.criterion = nn.CrossEntropyLoss()

    def forward(self, x):
        return self.net(x)

    def training_step(self, batch, batch_idx):
        x, y = batch
        logits = self(x)
        loss = self.criterion(logits, y)
        self.log("train/loss", loss, on_step=True, on_epoch=True, prog_bar=True)
        return loss

    def validation_step(self, batch, batch_idx):
        x, y = batch
        logits = self(x)
        loss = self.criterion(logits, y)
        self.log("val/loss", loss, on_step=False, on_epoch=True, prog_bar=True)
        return loss

    def test_step(self, batch, batch_idx):
        x, y = batch
        logits = self(x)
        loss = self.criterion(logits, y)
        self.log("test/loss", loss, on_step=False, on_epoch=True)
        return loss

    def configure_optimizers(self):
        return torch.optim.AdamW(
            self.parameters(), 
            lr=self.lr, 
            weight_decay=self.weight_decay
        )
