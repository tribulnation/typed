"""A fully typed, validated async client for the Kraken API.

Examples:
  ```python
  from typed_kraken import Kraken

  async with Kraken.new() as client:
    result = await client.spot.market_data.ticker(pair='XBTUSD')
    print(result)
  ```
"""

import lazy_loader as lazy

__getattr__, __dir__, __all__ = lazy.attach_stub(__name__, __file__)
