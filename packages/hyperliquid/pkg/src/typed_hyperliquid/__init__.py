"""A fully typed, validated async client for the Hyperliquid API.

Examples:
  ```python
  from typed_hyperliquid import Hyperliquid

  async with Hyperliquid.new(public=True) as client:
    result = await client.info.all_mids()
    print(result)
  ```
"""

import lazy_loader as lazy

__getattr__, __dir__, __all__ = lazy.attach_stub(__name__, __file__)
