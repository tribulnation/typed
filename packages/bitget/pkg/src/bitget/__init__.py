"""A fully typed, validated async client for the Bitget API.

Examples:
  ```python
  from bitget import Bitget

  async with Bitget.new(public=True) as client:
    result = await client.classic.spot.symbols()
    print(result)
  ```
"""

import lazy_loader as lazy

__getattr__, __dir__, __all__ = lazy.attach_stub(__name__, __file__)
