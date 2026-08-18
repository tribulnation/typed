"""A fully typed, validated async client for the Coinbase API.

Examples:
  ```python
  from coinbase import Coinbase

  async with Coinbase.new() as client:
    result = await client.data.ticker(...)
    print(result)
  ```
"""

import lazy_loader as lazy

__getattr__, __dir__, __all__ = lazy.attach_stub(__name__, __file__)
