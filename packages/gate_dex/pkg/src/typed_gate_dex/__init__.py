"""A fully typed, validated async client for the Gate DEX API.

Examples:
  ```python
  from typed_gate_dex import GateDex

  async with GateDex.new() as client:
    chains = await client.trade.chains()
    print(chains)
  ```
"""

import lazy_loader as lazy

__getattr__, __dir__, __all__ = lazy.attach_stub(__name__, __file__)
