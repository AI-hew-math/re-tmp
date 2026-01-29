from src.core.base_model import BaseModel
import torch.nn as nn

class Model(BaseModel):
    """
    EXP001: Baseline Experiment
    Inherited from ROOT
    """
    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        # TODO: Implement experiment logic
