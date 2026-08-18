"""`POST /api/v1/convert/limit/order` — Add Convert Limit Order."""

from typed_core.validation import TypedDict, validator
from kucoin.types import ConvertOrderResult
from kucoin.core import RpcEndpoint


class ConvertAddLimitOrder(TypedDict):
  """Parameters to place a convert limit order."""

  clientOrderId: str
  """Client-chosen order id, unique per account."""
  fromCurrency: str
  """Source currency, for example `USDT`."""
  toCurrency: str
  """Target currency, for example `BTC`."""
  fromCurrencySize: str
  """Amount of `fromCurrency` to convert."""
  toCurrencySize: str
  """Amount of `toCurrency` to receive; implies the order's limit price together with `fromCurrencySize`."""


_Type = ConvertOrderResult
adapter = validator[_Type](_Type)  # type: ignore


class AddLimitOrder(RpcEndpoint):
  """`Add Convert Limit Order` — mixed into `Convert`, the product exposing `convert.add_limit_order`."""

  async def add_limit_order(
    self,
    convert_add_limit_order: ConvertAddLimitOrder,
    *,
    validate: bool | None = None,
  ) -> ConvertOrderResult:
    """Place a convert limit order, resting until it fills, is cancelled, or expires. The venue rejects a price worse than Get Convert Limit Quote's protection price; querying that endpoint first is recommended.

    Args:
      convert_add_limit_order: Conversion limit order parameters.
      validate: Validate the response against the generated schema.

    References:
      - [KuCoin API docs](https://www.kucoin.com/docs-new)
    """
    return await self.authed_request(
      'POST',
      '/api/v1/convert/limit/order',
      json=convert_add_limit_order,
      validator=adapter,
      validate=validate,
    )
