import hydra
from omegaconf import DictConfig, OmegaConf
import pytorch_lightning as pl
from pytorch_lightning.callbacks import ModelCheckpoint, RichProgressBar
from pytorch_lightning.loggers import WandbLogger
import os
import torch
from dotenv import load_dotenv

# Load .env file for API keys
load_dotenv()

@hydra.main(version_base="1.3", config_path="../configs", config_name="config")
def train(cfg: DictConfig) -> None:
    # 1. Setup
    if cfg.get("seed"):
        pl.seed_everything(cfg.seed, workers=True)

    # 2. Instantiate Data
    datamodule = hydra.utils.instantiate(cfg.data)

    # 3. Instantiate Model
    model = hydra.utils.instantiate(cfg.model)

    # 4. Logger (WandB)
    logger = None
    if os.getenv("WANDB_API_KEY"):
        logger = WandbLogger(
            project=cfg.project_name,
            name=cfg.experiment_name,
            save_dir=cfg.output_dir,
            offline=False
        )

    # 5. Callbacks
    callbacks = [
        ModelCheckpoint(
            dirpath=os.path.join(cfg.output_dir, "checkpoints"),
            monitor="val/loss",
            mode="min",
            save_top_k=1
        ),
        RichProgressBar()
    ]

    # 6. Trainer
    trainer: pl.Trainer = hydra.utils.instantiate(
        cfg.trainer,
        callbacks=callbacks,
        logger=logger,
        default_root_dir=cfg.output_dir
    )

    # 7. Execute
    trainer.fit(model=model, datamodule=datamodule)

if __name__ == "__main__":
    train()
