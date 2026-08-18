from typing_extensions import Literal, NotRequired, TypedDict
from typed_core.validation import validator
from binance.core.endpoint.ws_rpc import WsRpcEndpoint


class CoinMWsPosition(TypedDict):
  """One position."""

  symbol: str
  """Symbol."""
  positionAmt: str
  """Position amount, in contracts."""
  entryPrice: NotRequired[str]
  """Position entry price."""
  markPrice: NotRequired[str]
  """Mark price."""
  unRealizedProfit: NotRequired[str]
  """Unrealized profit, in the settlement asset."""
  liquidationPrice: NotRequired[str]
  """Estimated liquidation price."""
  leverage: NotRequired[str]
  """Current leverage."""
  maxQty: NotRequired[str]
  """Maximum position quantity, in the base asset, allowed at this leverage."""
  marginType: NotRequired[Literal['cross', 'isolated']]
  """Margin type."""
  isolatedMargin: NotRequired[str]
  """Isolated margin amount, in the settlement asset."""
  isAutoAddMargin: NotRequired[str]
  """Whether auto-add-margin is enabled for this isolated position. Sent as a literal string, not a JSON boolean."""
  positionSide: Literal['BOTH', 'LONG', 'SHORT']
  """Position side. BOTH for One-way Mode; LONG or SHORT for Hedge Mode."""
  notionalValue: NotRequired[str]
  """Notional value of this position."""
  isolatedWallet: NotRequired[str]
  """Isolated wallet balance backing this position."""
  updateTime: NotRequired[int]
  """Time this position was last updated."""
  breakEvenPrice: NotRequired[str]
  """Break-even price for this position."""


class Position(WsRpcEndpoint):
  """Get current position information. Pair with the ACCOUNT_UPDATE user data stream event for timeliness- and accuracy-sensitive use cases rather than polling this method."""

  async def position(
    self,
    *,
    margin_asset: str | None = None,
    pair: str | None = None,
    validate: bool | None = None,
  ) -> list[CoinMWsPosition]:
    """Get current position information. Pair with the ACCOUNT_UPDATE user data stream event for timeliness- and accuracy-sensitive use cases rather than polling this method.

    Args:
      margin_asset: Settlement/margin asset, e.g. BTC. Mutually exclusive with pair.
      pair: Underlying pair. Mutually exclusive with marginAsset.

    References:
      - [Official docs](https://developers.binance.com/en/docs/catalog/core-trading-derivatives-trading-coin-m-futures/api/ws-api/trade#position-information)
    """
    params = {}
    if margin_asset is not None:
      params['marginAsset'] = margin_asset
    if pair is not None:
      params['pair'] = pair
    _Response = list[CoinMWsPosition]
    _validator = validator[_Response](_Response)
    return await self.authed_request(
      'account.position', params=params, validator=_validator, validate=validate
    )
