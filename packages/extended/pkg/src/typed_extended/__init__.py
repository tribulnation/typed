"""A fully typed, validated async client for the Extended API.

Examples:
  ```python
  from typed_extended import Extended

  async with Extended.new(public=True) as client:
    markets = await client.info.markets(['BTC-USD'])
  ```
"""

import lazy_loader as lazy

__getattr__, __dir__, __all__ = lazy.attach_stub(__name__, __file__)
