# Configuration Guide

The `config` package exposes `get_config()` which loads defaults from `config/defaults.yaml` and applies `QA__` environment variable overrides.

Example usage:

```python
from config import get_config
config = get_config()
print(config.data.raw_vault_dir)
```
