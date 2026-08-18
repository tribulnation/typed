from typing_extensions import NotRequired, TypedDict
from typed_core.validation import validator
from binance.core import Timestamp
from binance.core.endpoint.rpc import RpcEndpoint


class MmpConfig(TypedDict):
  """Market Maker Protection config for one underlying."""

  underlyingId: NotRequired[int]
  """Underlying ID."""
  underlying: NotRequired[str]
  """Underlying asset."""
  windowTimeInMilliseconds: NotRequired[int]
  """MMP interval, in milliseconds."""
  frozenTimeInMilliseconds: NotRequired[int]
  """MMP frozen time, in milliseconds. 0 means a manual reset is required."""
  qtyLimit: NotRequired[str]
  """Quantity limit."""
  deltaLimit: NotRequired[str]
  """Net delta limit."""
  lastTriggerTime: NotRequired[Timestamp]
  """Time MMP was last triggered."""


class MmpSet(RpcEndpoint):
  """Set the Market Maker Protection (MMP) config for an underlying. MMP is a protection mechanism preventing mass trading in a short period: once the configured threshold is breached, all current MMP orders are cancelled and new MMP orders are rejected until reset."""

  async def mmp_set(
    self,
    *,
    underlying: str,
    window_time_in_milliseconds: int,
    frozen_time_in_milliseconds: int,
    qty_limit: str,
    delta_limit: str,
    validate: bool | None = None,
  ) -> MmpConfig:
    """Set the Market Maker Protection (MMP) config for an underlying. MMP is a protection mechanism preventing mass trading in a short period: once the configured threshold is breached, all current MMP orders are cancelled and new MMP orders are rejected until reset.

    Args:
      underlying: Underlying asset, e.g. BTCUSDT.
      window_time_in_milliseconds: MMP interval, in milliseconds.
      frozen_time_in_milliseconds: MMP frozen time, in milliseconds. 0 requires a manual reset.
      qty_limit: Quantity limit.
      delta_limit: Net delta limit.

    References:
      - [Official docs](https://developers.binance.com/docs/derivatives/option/market-maker-endpoints#set-market-maker-protection-config)
    """
    params: dict = {
      'underlying': underlying,
      'windowTimeInMilliseconds': window_time_in_milliseconds,
      'frozenTimeInMilliseconds': frozen_time_in_milliseconds,
      'qtyLimit': qty_limit,
      'deltaLimit': delta_limit,
    }
    _Response = MmpConfig
    _validator = validator[_Response](_Response)
    return await self.authed_request(
      'POST', '/eapi/v1/mmpSet', params=params, validator=_validator, validate=validate
    )
