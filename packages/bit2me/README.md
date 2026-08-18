# Typed Bit2Me

> A fully typed, validated async client for the Bit2Me API

**Use autocomplete instead of documentation.**

```python
from bit2me import Bit2Me

async with Bit2Me.new() as client:
  result = await client.data.ticker(...)
  print(result)
```

## Why Typed Bit2Me?

- **🎯 Precise Types**: Strong typing throughout, so your editor can help before runtime does.
- **✅ Automatic Validation**: Catch upstream API changes earlier, where they are easier to debug.
- **⚡ Async First**: Built for concurrent, network-heavy workflows.
- **🔒 Safer Usage**: Typed inputs and explicit errors reduce avoidable mistakes.
- **🎨 Better DX**: Clear routing, sensible defaults, and minimal ceremony.
- **📦 Practical Extras**: A place for pagination, streams, and client-specific helpers when they add real value.

## Installation

```bash
pip install typed-bit2me
```

## Documentation

> [**Read the docs**](https://bit2me.tribulnation.com)
