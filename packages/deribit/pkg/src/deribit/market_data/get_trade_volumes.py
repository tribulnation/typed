"""`public/get_trade_volumes` — `public/get_trade_volumes`."""

from typing_extensions import NotRequired, TypedDict
from typed_core.validation import validator
from deribit.core import RpcEndpoint


class TradeVolumeItem(TypedDict):
  """24h/7d/30d trade volume for one currency."""

  currency: str
  """Currency, i.e `"BTC"`, `"ETH"`, `"USDC"`"""
  calls_volume: float
  """Total 24h trade volume for call options."""
  puts_volume: float
  """Total 24h trade volume for put options."""
  futures_volume: float
  """Total 24h trade volume for futures."""
  spot_volume: NotRequired[float]
  """Total 24h trade for spot."""
  calls_volume_7d: NotRequired[float]
  """Total 7d trade volume for call options."""
  puts_volume_7d: NotRequired[float]
  """Total 7d trade volume for put options."""
  futures_volume_7d: NotRequired[float]
  """Total 7d trade volume for futures."""
  spot_volume_7d: NotRequired[float]
  """Total 7d trade for spot."""
  calls_volume_30d: NotRequired[float]
  """Total 30d trade volume for call options."""
  puts_volume_30d: NotRequired[float]
  """Total 30d trade volume for put options."""
  futures_volume_30d: NotRequired[float]
  """Total 30d trade volume for futures."""
  spot_volume_30d: NotRequired[float]
  """Total 30d trade for spot."""
  currency_pair: NotRequired[str]
  """Currency pair the volumes are quoted against, e.g. `ada_usd`. Observed live; not documented in the OpenAPI schema."""


validate_get_trade_volumes = validator[list[TradeVolumeItem]](list[TradeVolumeItem])


class GetTradeVolumes(RpcEndpoint):
  """`public/get_trade_volumes`."""

  async def get_trade_volumes(
    self,
    *,
    extended: bool | None = None,
    validate: bool | None = None,
  ) -> list[TradeVolumeItem]:
    """Retrieves aggregated 24-hour trade volumes for different instrument types and currencies. The volume statistics include all executed trades across the platform.

    **Note:** Position moves are not included in this volume. Block trades and Block RFQ trades are included in the volume calculations.

    Use the `extended` parameter to include additional volume statistics and breakdowns.

    Args:
      extended: Request for extended statistics. Including also 7 and 30 days volumes (default false)
      validate: Validate the response against the generated schema.

    References:
      - [Deribit API docs](https://docs.deribit.com/api-reference/market-data/public-get_trade_volumes)
    """
    params = {}
    if extended is not None:
      params['extended'] = extended
    return await self.request(
      'public/get_trade_volumes',
      params=params,
      validator=validate_get_trade_volumes,
      validate=validate,
    )
