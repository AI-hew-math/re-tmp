# Attention Is All You Need

**Key:** `transformer` (cite as `[@transformer]`)  
**Authors:** Vaswani et al.  
**Year:** 2017 | **Venue:** NeurIPS  
**Links:** [arXiv](https://arxiv.org/abs/1706.03762) | [Code](https://github.com/tensorflow/tensor2tensor)

---

## Summary (In Context of This Project)

The Transformer architecture replaces recurrence entirely with self-attention, enabling parallel computation and better long-range dependency modeling. For our experiments, the key insight is that attention mechanisms can replace traditional sequential processing in many domains beyond NLP.

If we're working on vision or multimodal tasks, the core multi-head attention block is directly applicable. The positional encoding approach is also relevant for any sequence-based input.

## Key Contributions

1. **Self-attention as primary mechanism** - No recurrence or convolution needed
2. **Multi-head attention** - Parallel attention heads capture different relationship types
3. **Positional encoding** - Sinusoidal encoding to inject sequence order information

## Method

### Core Idea

Instead of processing sequences step-by-step (RNN) or with local windows (CNN), compute attention scores between all positions simultaneously. Each position can directly attend to every other position in O(1) sequential operations.

### Architecture

```
Input → Embedding + Positional Encoding
      → N × (Multi-Head Attention → Add & Norm → FFN → Add & Norm)
      → Output
```

Encoder-decoder structure with cross-attention in decoder layers.

### Key Equations

**Scaled Dot-Product Attention:**
```
Attention(Q, K, V) = softmax(QK^T / √d_k) V
```

**Multi-Head Attention:**
```
MultiHead(Q, K, V) = Concat(head_1, ..., head_h) W^O
where head_i = Attention(QW_i^Q, KW_i^K, VW_i^V)
```

**Positional Encoding:**
```
PE(pos, 2i) = sin(pos / 10000^(2i/d_model))
PE(pos, 2i+1) = cos(pos / 10000^(2i/d_model))
```

## Results Worth Noting

| Task | Metric | Score | Notes |
|------|--------|-------|-------|
| WMT14 EN-DE | BLEU | 28.4 | +2.0 over previous SOTA |
| WMT14 EN-FR | BLEU | 41.8 | New SOTA, 3.5 days on 8 GPUs |

## Code to Borrow

```python
import torch
import torch.nn as nn
import math

class MultiHeadAttention(nn.Module):
    def __init__(self, d_model: int, n_heads: int, dropout: float = 0.1):
        super().__init__()
        assert d_model % n_heads == 0
        self.d_k = d_model // n_heads
        self.n_heads = n_heads
        
        self.W_q = nn.Linear(d_model, d_model)
        self.W_k = nn.Linear(d_model, d_model)
        self.W_v = nn.Linear(d_model, d_model)
        self.W_o = nn.Linear(d_model, d_model)
        self.dropout = nn.Dropout(dropout)
    
    def forward(self, q, k, v, mask=None):
        batch_size = q.size(0)
        
        # Linear projections and reshape to (batch, heads, seq_len, d_k)
        q = self.W_q(q).view(batch_size, -1, self.n_heads, self.d_k).transpose(1, 2)
        k = self.W_k(k).view(batch_size, -1, self.n_heads, self.d_k).transpose(1, 2)
        v = self.W_v(v).view(batch_size, -1, self.n_heads, self.d_k).transpose(1, 2)
        
        # Scaled dot-product attention
        scores = torch.matmul(q, k.transpose(-2, -1)) / math.sqrt(self.d_k)
        if mask is not None:
            scores = scores.masked_fill(mask == 0, -1e9)
        attn = self.dropout(torch.softmax(scores, dim=-1))
        
        # Apply attention to values and reshape
        out = torch.matmul(attn, v)
        out = out.transpose(1, 2).contiguous().view(batch_size, -1, self.n_heads * self.d_k)
        return self.W_o(out)


def positional_encoding(max_len: int, d_model: int) -> torch.Tensor:
    """Sinusoidal positional encoding."""
    pe = torch.zeros(max_len, d_model)
    position = torch.arange(0, max_len, dtype=torch.float).unsqueeze(1)
    div_term = torch.exp(torch.arange(0, d_model, 2).float() * (-math.log(10000.0) / d_model))
    pe[:, 0::2] = torch.sin(position * div_term)
    pe[:, 1::2] = torch.cos(position * div_term)
    return pe.unsqueeze(0)  # (1, max_len, d_model)
```

## Relevance to Our Experiments

- **Potential use:** Any experiment needing to model relationships across sequence/spatial positions
- **EXP002+:** Could add attention to CNN baseline for global context
- **Differs from CNNs:** Global receptive field from layer 1, but quadratic memory in sequence length

## Questions / Notes

- For vision: see ViT (Vision Transformer) for patch-based application
- Memory scales O(n²) - consider linear attention variants for long sequences
- Pre-norm (LayerNorm before attention) often trains better than post-norm

---

<details>
<summary><strong>📄 Full Paper Content</strong> (click to expand)</summary>

```
[Abstract]
The dominant sequence transduction models are based on complex recurrent or
convolutional neural networks that include an encoder and a decoder. The best
performing models also connect the encoder and decoder through an attention
mechanism. We propose a new simple network architecture, the Transformer,
based solely on attention mechanisms, dispensing with recurrence and convolutions
entirely. Experiments on two machine translation tasks show these models to
be superior in quality while being more parallelizable and requiring significantly
less time to train...

[See arxiv for full paper: https://arxiv.org/abs/1706.03762]
```

</details>
