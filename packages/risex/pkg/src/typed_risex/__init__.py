"""A fully typed, validated async client for the RISEx API.

Examples:
  ```python
  from typed_risex import RISEx

  async with RISEx.new(public=True) as client:
    book = await client.markets.orderbook(market_id=1, limit=5)
  ```
"""

import lazy_loader as lazy

__getattr__, __dir__, __all__ = lazy.attach_stub(__name__, __file__)
