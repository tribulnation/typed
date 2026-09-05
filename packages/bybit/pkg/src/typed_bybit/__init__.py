"""A fully typed, validated async client for the Bybit v5 API.

Examples:
  ```python
  from typed_bybit import Bybit

  async with Bybit.new(public=True) as client:
    candles = await client.market.kline(symbol='BTCUSDT', interval='60')
  ```

References:
  - [Bybit v5 API docs](https://bybit-exchange.github.io/docs/v5/intro)
"""

import lazy_loader as lazy

__getattr__, __dir__, __all__ = lazy.attach_stub(__name__, __file__)
