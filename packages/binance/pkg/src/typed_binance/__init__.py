"""A fully typed, validated async client for the Binance API.

Examples:
  ```python
  from typed_binance import Binance

  async with Binance.new(public=True) as client:
    result = await client.spot.market.server_time()
    print(result)
  ```
"""

import lazy_loader as lazy

__getattr__, __dir__, __all__ = lazy.attach_stub(__name__, __file__)
