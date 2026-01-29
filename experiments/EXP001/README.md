---
id: EXP001
parent: ROOT
status: complete
created: 2026-01-29
---

# EXP001: CIFAR-10 Baseline CNN

## Context
Template verification experiment. Proves the entire pipeline works end-to-end.

## Hypothesis
A simple CNN with batch normalization and dropout should achieve ~85% accuracy on CIFAR-10.

## Method
- 3-block CNN (32 → 64 → 128 channels)
- BatchNorm + ReLU after each conv
- MaxPool + Dropout between blocks
- AdaptiveAvgPool → Linear classifier
- CrossEntropyLoss, AdamW optimizer

## Config
```yaml
model:
  hidden_dim: 128
  lr: 1e-3
  weight_decay: 1e-4
trainer:
  max_epochs: 50
data:
  batch_size: 128
```

## Run
```bash
# Local dry run
uv run python3 src/train.py experiment=EXP001 trainer.accelerator=cpu trainer.fast_dev_run=true

# Full training
python3 scripts/submit.py --experiment EXP001 --device "1x3090" --cluster soda
```

## References
- [@cifar] - CIFAR-10 dataset for baseline validation

## Results
(Baseline reference - to be filled after first run)
