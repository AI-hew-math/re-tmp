# Literature

This directory tracks papers relevant to this research project.

## Structure

```
literature/
├── README.md          # This file
├── papers.yaml        # Paper database (metadata + links)
├── papers/            # Detailed notes for important papers
│   ├── .template.md   # Template for new paper notes
│   └── <key>.md       # Deep-dive notes (optional per paper)
├── related-work.md    # Survey narrative (create via setup.py)
└── index.md           # Auto-generated reverse index
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
  repo: "https://github.com/tensorflow/tensor2tensor"
  tags: [attention, architecture]
  notes: "Self-attention mechanism"
  details: papers/transformer.md  # Optional: detailed notes
```

### 1b. (Optional) Add Detailed Notes

For important papers, create `papers/<key>.md` using the template:
```bash
cp papers/.template.md papers/transformer.md
```

Include:
- Key contributions & method details
- Architecture diagrams / equations
- Code snippets worth borrowing
- How it connects to your experiments

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
