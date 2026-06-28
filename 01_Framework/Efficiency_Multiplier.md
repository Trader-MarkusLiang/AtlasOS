# Efficiency Multiplier

This framework judges whether AI algorithm optimization weakens hardware demand or expands it.

Typical logic:

```text
Inference efficiency improves
 ↓
Token cost falls
 ↓
Call volume increases
 ↓
More agents run
 ↓
Inference duration increases
 ↓
Total Memory / GPU / Bandwidth demand rises
```

Core economics:

> Jevons Paradox: efficiency improvement can expand total resource consumption.

## Cases

- DeepSeek Spark
- Speculative Decoding
- Flash Attention
- MoE
- KV Cache optimization
