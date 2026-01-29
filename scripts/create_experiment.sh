#!/bin/bash
# scripts/create_experiment.sh

if [ -z "$3" ]; then
  echo "Usage: $0 <NEW_ID> <PARENT_ID> <DESCRIPTION>"
  exit 1
fi

NEW_ID=$1
PARENT_ID=$2
DESC=$3
DATE=$(date +%Y-%m-%d)

# 1. Source skeleton - copy from parent if it exists
mkdir -p src/experiments/$NEW_ID
touch src/experiments/$NEW_ID/__init__.py

PARENT_MODEL="src/experiments/$PARENT_ID/model.py"
if [ -f "$PARENT_MODEL" ] && [ "$PARENT_ID" != "ROOT" ]; then
    # Copy parent model as starting point
    cp "$PARENT_MODEL" src/experiments/$NEW_ID/model.py
    # Update docstring
    sed -i '' "s/$PARENT_ID/$NEW_ID/g" src/experiments/$NEW_ID/model.py 2>/dev/null || \
    sed -i "s/$PARENT_ID/$NEW_ID/g" src/experiments/$NEW_ID/model.py
    echo "  Copied model from $PARENT_ID (modify as needed)"
else
    # Create skeleton with guidance
    cat <<EOF > src/experiments/$NEW_ID/model.py
"""
$NEW_ID: $DESC
Parent: $PARENT_ID

TODO: Implement your experiment changes here.
See src/experiments/EXP001/model.py for a complete example.
"""
from src.core.base_model import BaseModel
import torch.nn as nn


class Model(BaseModel):
    """
    $DESC
    
    Changes from parent ($PARENT_ID):
    - TODO: List what you're changing
    """
    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        # TODO: Define your architecture
        # Example:
        # self.net = nn.Sequential(
        #     nn.Linear(784, 256),
        #     nn.ReLU(),
        #     nn.Linear(256, 10)
        # )
        raise NotImplementedError("Implement your model architecture")
EOF
fi

# 2. Config override
cat <<EOF > configs/experiment/$NEW_ID.yaml
# @package _global_
defaults:
  - override /model: default

experiment_name: "$NEW_ID"
model:
  _target_: src.experiments.$NEW_ID.model.Model
EOF

# 3. Documentation
mkdir -p experiments/$NEW_ID
cat <<EOF > experiments/$NEW_ID/README.md
---
id: $NEW_ID
parent: $PARENT_ID
status: planned
created: $DATE
---

# $NEW_ID: $DESC

## Context
Extends $PARENT_ID.

## Hypothesis
<!-- FILL BEFORE RUNNING: What do you expect and why? -->


## Method
<!-- What specifically are you changing from the parent? -->


## Success Criteria
<!-- How will you measure if this worked? -->
- [ ] Metric improves by X%
- [ ] Training converges faster
- [ ] ...

## References
<!-- Cite papers from literature/papers.yaml using [@key] -->


---

## Results
<!-- FILL AFTER RUNNING -->

### Metrics
| Metric | Expected | Actual |
|--------|----------|--------|
| | | |

### Observations


### Conclusion
<!-- Hypothesis confirmed/rejected? What's next? -->

EOF

# 4. Update graph
python3 scripts/update_graph.py

echo "Created experiment $NEW_ID (Child of $PARENT_ID)"
