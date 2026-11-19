"""A fully typed, validated async client for the Evedex API.

Examples:
  ```python
  from typed_evedex import Evedex

  async with Evedex.new(public=True) as client:
    info = await client.exchange.market.info()
    print(info['state'])
  ```
"""

import lazy_loader as lazy

__getattr__, __dir__, __all__ = lazy.attach_stub(__name__, __file__)
