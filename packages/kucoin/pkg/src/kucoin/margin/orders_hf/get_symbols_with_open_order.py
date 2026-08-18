"""`GET /api/v3/hf/margin/order/active/symbols` — Get Symbols With Open Order."""

from typed_core.validation import TypedDict, validator
from kucoin.core import RpcEndpoint


class HfMarginOpenOrderSymbols(TypedDict):
  """Trading pairs currently holding at least one open hf margin order."""

  symbolSize: int
  """Count of symbols in `symbols`."""
  symbols: list[str]
  """Trading pair symbols with an open hf margin order."""


_Type = HfMarginOpenOrderSymbols
adapter = validator[_Type](_Type)  # type: ignore


class GetSymbolsWithOpenOrder(RpcEndpoint):
  """`Get Symbols With Open Order` — mixed into `OrdersHf`, the product exposing `margin.orders_hf.get_symbols_with_open_order`."""

  async def get_symbols_with_open_order(
    self,
    *,
    trade_type: str,
    validate: bool | None = None,
  ) -> HfMarginOpenOrderSymbols:
    """List every trading pair symbol that currently has at least one open margin hf order for the authenticated account, in the given margin mode.

    Args:
      trade_type: Margin mode to look up. Confirmed live 2026-08-08: both `MARGIN_TRADE` (cross) and `MARGIN_ISOLATED_TRADE` (isolated) are accepted, but this endpoint's docs page never states the field is a closed set, so it is left as a plain string rather than a guessed enum.
      validate: Validate the response against the generated schema.

    References:
      - [KuCoin API docs](https://www.kucoin.com/docs-new)
    """
    params: dict = {
      'tradeType': trade_type,
    }
    return await self.authed_request(
      'GET',
      '/api/v3/hf/margin/order/active/symbols',
      params=params,
      validator=adapter,
      validate=validate,
    )
