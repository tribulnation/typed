"""`GET /api/v1/trade-fees` — Get Actual Fee - Futures."""

from typing_extensions import NotRequired
from typed_core.validation import TypedDict, validator
from kucoin.core import RpcEndpoint


class FuturesActualFee(TypedDict):
  symbol: str
  """The futures contract symbol, echoed back."""
  takerFeeRate: str
  """Actual taker fee rate for this symbol, decimal string."""
  makerFeeRate: str
  """Actual maker fee rate for this symbol, decimal string."""
  feeTaxRate: NotRequired[str]
  """Additional tax rate applied on top of the taker/maker fee, decimal string. Undocumented -- observed in the live response, not mentioned on the docs page."""


_Type = FuturesActualFee
adapter = validator[_Type](_Type)  # type: ignore


class ActualFeeFutures(RpcEndpoint):
  """`Get Actual Fee - Futures` — mixed into `TradeFee`, the product exposing `account.trade_fee.actual_fee_futures`."""

  async def actual_fee_futures(
    self,
    *,
    symbol: str,
    validate: bool | None = None,
  ) -> FuturesActualFee:
    """Get the actual futures taker/maker fee rate for one trading symbol. A sub-account's fee rate matches its master account's. This is the Futures sibling of `account.trade_fee.actual_fee` -- same path, a different host (`api-futures.kucoin.com`), a singular optional `symbol` instead of a required comma-separated `symbols`, and a single object response instead of an array.

    Args:
      symbol: A single futures contract symbol, e.g. `XBTUSDTM`. Documented as optional on the rendered docs page, but a live call without it is rejected -- see `notes`.
      validate: Validate the response against the generated schema.

    References:
      - [KuCoin API docs](https://www.kucoin.com/docs-new)
    """
    params: dict = {
      'symbol': symbol,
    }
    return await self.authed_request(
      'GET',
      '/api/v1/trade-fees',
      params=params,
      validator=adapter,
      validate=validate,
    )
