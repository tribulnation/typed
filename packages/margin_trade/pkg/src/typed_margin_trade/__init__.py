"""A fully typed, validated async client for the Margin Trade API.

Examples:
  ```python
  from typed_margin_trade import MarginTrade

  async with MarginTrade.new(public=True) as client:
    book = await client.info.l2_book('BTC')
  ```
"""

import lazy_loader as lazy

__getattr__, __dir__, __all__ = lazy.attach_stub(__name__, __file__)
