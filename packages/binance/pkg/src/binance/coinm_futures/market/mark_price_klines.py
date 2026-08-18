from typing_extensions import Literal
from typed_core.validation import validator
from binance.core.endpoint.rpc import RpcEndpoint


class MarkPriceKlines(RpcEndpoint):
  """Kline/candlestick bars for the mark price of a symbol. Klines are uniquely identified by their open time."""

  async def mark_price_klines(
    self,
    *,
    symbol: str,
    interval: Literal[
      '1m',
      '3m',
      '5m',
      '15m',
      '30m',
      '1h',
      '2h',
      '4h',
      '6h',
      '8h',
      '12h',
      '1d',
      '3d',
      '1w',
      '1M',
    ],
    start_time: int | None = None,
    end_time: int | None = None,
    limit: int | None = None,
    validate: bool | None = None,
  ) -> list[tuple[int, str, str, str, str, str, int, str, int, str, str, str]]:
    """Kline/candlestick bars for the mark price of a symbol. Klines are uniquely identified by their open time.

    Args:
      symbol: Symbol. After the CM migration, accepts both CM and UM symbols.
      interval: Candle interval.
      start_time: Start time, in milliseconds since epoch.
      end_time: End time, in milliseconds since epoch.
      limit: Number of candles to return.

    References:
      - [Official docs](https://developers.binance.com/en/docs/catalog/core-trading-derivatives-trading-coin-m-futures/api/rest-api/market-data#mark-price-kline-candlestick-data)
    """
    params: dict = {
      'symbol': symbol,
      'interval': interval,
    }
    if start_time is not None:
      params['startTime'] = start_time
    if end_time is not None:
      params['endTime'] = end_time
    if limit is not None:
      params['limit'] = limit
    _Response = list[tuple[int, str, str, str, str, str, int, str, int, str, str, str]]
    _validator = validator[_Response](_Response)
    return await self.request(
      'GET',
      '/dapi/v1/markPriceKlines',
      params=params,
      validator=_validator,
      validate=validate,
    )
