"""A fully typed, validated async client for the Coinbase API.

Examples:
  ```python
  from typed_coinbase import Coinbase

  async with Coinbase.new(public=True) as client:
    product = await client.app.advanced_trade.http.products.public.get('BTC-USD')
    print(product['price'])
  ```
"""

import lazy_loader as lazy

__getattr__, __dir__, __all__ = lazy.attach_stub(__name__, __file__)
