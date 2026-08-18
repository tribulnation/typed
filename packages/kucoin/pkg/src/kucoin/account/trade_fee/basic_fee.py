"""`GET /api/v1/base-fee` — Get Basic Fee - Spot/Margin."""

from typing_extensions import Literal
from typed_core.validation import TypedDict, validator
from kucoin.core import RpcEndpoint


class BasicFee(TypedDict):
  takerFeeRate: str
  """Base taker fee rate, decimal string."""
  makerFeeRate: str
  """Base maker fee rate, decimal string."""


_Type = BasicFee
adapter = validator[_Type](_Type)  # type: ignore


class BasicFeeEndpoint(RpcEndpoint):
  """`Get Basic Fee - Spot/Margin` — mixed into `TradeFee`, the product exposing `account.trade_fee.basic_fee`."""

  async def basic_fee(
    self,
    *,
    currency_type: Literal[0, 1] | None = None,
    validate: bool | None = None,
  ) -> BasicFee:
    """Get the authenticated account's basic (non-symbol-specific) spot/margin fee rate -- the rate that applies before any per-symbol override.

    Args:
      currency_type: Which fee-rate currency to report.
      validate: Validate the response against the generated schema.

    References:
      - [KuCoin API docs](https://www.kucoin.com/docs-new)
    """
    params = {}
    if currency_type is not None:
      params['currencyType'] = currency_type
    return await self.authed_request(
      'GET',
      '/api/v1/base-fee',
      params=params,
      validator=adapter,
      validate=validate,
    )
