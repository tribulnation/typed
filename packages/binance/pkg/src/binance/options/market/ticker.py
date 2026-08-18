from typing_extensions import NotRequired, TypedDict
from typed_core.validation import validator
from binance.core import Timestamp
from binance.core.endpoint.rpc import RpcEndpoint


class Ticker24hr(TypedDict):
  """24-hour rolling window price-change statistics for one option symbol."""

  symbol: NotRequired[str]
  """Option trading pair, formatted UNDERLYING-EXPIRYDATE-STRIKE-C|P, e.g. BTC-260925-145000-C (a BTC call expiring 2026-09-25 with strike 145000)."""
  priceChange: NotRequired[str]
  """24-hour price change."""
  priceChangePercent: NotRequired[str]
  """24-hour percent price change."""
  lastPrice: NotRequired[str]
  """Last trade price."""
  lastQty: NotRequired[str]
  """Last trade amount."""
  open: NotRequired[str]
  """24-hour open price."""
  high: NotRequired[str]
  """24-hour high."""
  low: NotRequired[str]
  """24-hour low."""
  volume: NotRequired[str]
  """Trading volume, in contracts."""
  amount: NotRequired[str]
  """Trade amount, in quote asset."""
  bidPrice: NotRequired[str]
  """Best buy price."""
  askPrice: NotRequired[str]
  """Best sell price."""
  openTime: NotRequired[Timestamp]
  """Time the first trade occurred within the last 24 hours."""
  closeTime: NotRequired[Timestamp]
  """Time the last trade occurred within the last 24 hours."""
  firstTradeId: NotRequired[int]
  """First trade ID."""
  tradeCount: NotRequired[int]
  """Number of trades."""
  strikePrice: NotRequired[str]
  """Strike price."""
  exercisePrice: NotRequired[str]
  """Estimated settlement price one hour before exercise; index price at other times."""


class Ticker(RpcEndpoint):
  """24 hour rolling window price change statistics."""

  async def ticker(
    self,
    *,
    symbol: str | None = None,
    validate: bool | None = None,
  ) -> list[Ticker24hr]:
    """24 hour rolling window price change statistics.

    Args:
      symbol: Option trading pair, formatted UNDERLYING-EXPIRYDATE-STRIKE-C|P, e.g. BTC-260925-145000-C (a BTC call expiring 2026-09-25 with strike 145000).

    References:
      - [Official docs](https://developers.binance.com/docs/derivatives/option/market-data#ticker24hr-price-change-statistics)
    """
    params = {}
    if symbol is not None:
      params['symbol'] = symbol
    _Response = list[Ticker24hr]
    _validator = validator[_Response](_Response)
    return await self.request(
      'GET', '/eapi/v1/ticker', params=params, validator=_validator, validate=validate
    )
