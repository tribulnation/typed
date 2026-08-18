from typing_extensions import NotRequired, TypedDict
from typed_core.validation import validator
from binance.core.endpoint.rpc import RpcEndpoint


class CountdownCancelAllConfig(TypedDict):
  """Kill-switch config for one underlying."""

  underlying: NotRequired[str]
  """Underlying asset."""
  countdownTime: NotRequired[int]
  """Countdown time in milliseconds. Only active configs (nonzero) are returned."""


class CountdownCancelAllSet(RpcEndpoint):
  """Set the auto-cancel-all-open-orders (kill-switch) config: cancel all open orders (both MMP and non-MMP) of the underlying at the end of countdownTime if no heartbeat arrives first. After the countdown, all open orders are cancelled and new orders are rejected with error -2010 until a heartbeat is sent or the feature is turned off (countdownTime=0)."""

  async def countdown_cancel_all_set(
    self,
    *,
    underlying: str,
    countdown_time: int,
    validate: bool | None = None,
  ) -> CountdownCancelAllConfig:
    """Set the auto-cancel-all-open-orders (kill-switch) config: cancel all open orders (both MMP and non-MMP) of the underlying at the end of countdownTime if no heartbeat arrives first. After the countdown, all open orders are cancelled and new orders are rejected with error -2010 until a heartbeat is sent or the feature is turned off (countdownTime=0).

    Args:
      underlying: Underlying asset, e.g. BTCUSDT.
      countdown_time: Countdown time.

    References:
      - [Official docs](https://developers.binance.com/docs/derivatives/option/market-maker-endpoints#set-auto-cancel-all-open-orders)
    """
    params: dict = {
      'underlying': underlying,
      'countdownTime': countdown_time,
    }
    _Response = CountdownCancelAllConfig
    _validator = validator[_Response](_Response)
    return await self.authed_request(
      'POST',
      '/eapi/v1/countdownCancelAll',
      params=params,
      validator=_validator,
      validate=validate,
    )
