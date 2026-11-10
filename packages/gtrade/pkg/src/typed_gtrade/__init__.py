"""A fully typed, validated async client for gTrade by Gains Network.

Examples:
  ```python
  from typed_gtrade import GTrade

  async with GTrade.new(public=True) as client:
    prices = await client.trading.markets.prices()
  ```
"""

import lazy_loader as lazy

__getattr__, __dir__, __all__ = lazy.attach_stub(__name__, __file__)
