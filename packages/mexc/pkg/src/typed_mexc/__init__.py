"""A fully typed, validated async client for the MEXC API.

Examples:
  ```python
  from typed_mexc import MEXC

  async with MEXC.new(public=True) as client:
    result = await client.spot.market.ping()
    print(result)
  ```
"""

import lazy_loader as lazy

__getattr__, __dir__, __all__ = lazy.attach_stub(__name__, __file__)
