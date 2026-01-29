# Literature

This directory tracks papers relevant to this research project.

## Structure

```
literature/
├── README.md          # This file
├── related-work.md    # Survey document (create via setup.py or manually)
└── papers.yaml        # Paper database with metadata
```

## How It Works

### 1. Add Papers to `papers.yaml`

```yaml
transformer:
  title: "Attention Is All You Need"
  authors: "Vaswani et al."
  year: 2017
  venue: NeurIPS
  arxiv: "1706.03762"
  tags: [attention, architecture]
  notes: "Foundation for modern LLMs"
```

### 2. Cite in Experiments

In `experiments/EXPXXX/README.md`:

```markdown
## References
Based on [@transformer] attention mechanism.
Compares against [@resnet] baseline.
```

### 3. Auto-Generated Index

Run `python scripts/lit_index.py` to generate:
- Reverse index: which experiments cite which papers
- Missing citations: papers referenced but not in database
- Orphan papers: papers never cited

## Integration with Experiments

When creating an experiment, the README template includes:

```markdown
## References
<!-- List paper keys from papers.yaml -->
- [@key1] - why relevant
- [@key2] - what we borrow
```

This creates a bidirectional link between literature and experiments.
