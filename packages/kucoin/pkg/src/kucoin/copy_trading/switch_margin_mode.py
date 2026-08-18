"""`POST /api/v1/copy-trade/futures/position/changeMarginMode` — Switch Margin Mode."""

from typing_extensions import Literal
from typed_core.validation import TypedDict, validator
from kucoin.core import RpcEndpoint


class CopyTradeMarginMode(TypedDict):
  """Margin mode currently set for a copy-trading contract symbol."""

  symbol: str
  """Symbol of the contract."""
  marginMode: Literal['ISOLATED', 'CROSS']
  """Margin mode now in effect."""


class SwitchCopyTradeMarginModeParams(TypedDict):
  """Symbol and target margin mode to switch to."""

  symbol: str
  """Symbol of the contract, e.g. `XBTUSDTM`."""
  marginMode: Literal['ISOLATED', 'CROSS']
  """Margin mode to switch to."""


_Type = CopyTradeMarginMode
adapter = validator[_Type](_Type)  # type: ignore


class SwitchMarginMode(RpcEndpoint):
  """`Switch Margin Mode` — mixed into `CopyTrading`, the product exposing `copy_trading.switch_margin_mode`."""

  async def switch_margin_mode(
    self,
    switch_copy_trade_margin_mode_params: SwitchCopyTradeMarginModeParams,
    *,
    validate: bool | None = None,
  ) -> CopyTradeMarginMode:
    """Modify the margin mode (cross or isolated) of a copy-trading futures position's symbol. Requires the API key's `LeadtradeFutures` permission.

    Args:
      switch_copy_trade_margin_mode_params: Symbol and target margin mode to switch to.
      validate: Validate the response against the generated schema.

    References:
      - [KuCoin API docs](https://www.kucoin.com/docs-new)
    """
    return await self.authed_request(
      'POST',
      '/api/v1/copy-trade/futures/position/changeMarginMode',
      json=switch_copy_trade_margin_mode_params,
      validator=adapter,
      validate=validate,
    )
