from dataclasses import dataclass, field
from typing import Any, List


@dataclass
class DataConfig:
    _target_: str = "src.core.base_data.BaseDataModule"
    data_dir: str = "/data/${oc.env:USER}/datasets"
    batch_size: int = 64
    num_workers: int = 4
    pin_memory: bool = True


@dataclass
class ModelConfig:
    _target_: str = "src.core.base_model.BaseModel"
    lr: float = 1e-3
    weight_decay: float = 1e-5


@dataclass
class TrainerConfig:
    _target_: str = "pytorch_lightning.Trainer"
    max_epochs: int = 10
    accelerator: str = "gpu"
    devices: Any = 1
    precision: str = "16-mixed"
    log_every_n_steps: int = 10


@dataclass
class ExperimentConfig:
    """
    The master config schema.
    Agents: read this to see valid top-level fields.
    """

    defaults: List[Any] = field(default_factory=lambda: [
        "_self_",
        {"data": "default"},
        {"model": "default"},
        {"trainer": "default"},
    ])

    seed: int = 42
    project_name: str = "dl-research"
    experiment_name: str = "EXP_DEFAULT"

    data: DataConfig = field(default_factory=DataConfig)
    model: ModelConfig = field(default_factory=ModelConfig)
    trainer: TrainerConfig = field(default_factory=TrainerConfig)

    work_dir: str = "${hydra:runtime.cwd}"
    output_dir: str = "outputs/${experiment_name}/${now:%Y-%m-%d_%H-%M-%S}"
