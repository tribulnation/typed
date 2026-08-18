from typing_extensions import NotRequired, TypedDict
from typed_core.validation import validator
from binance.core.endpoint.rpc import RpcEndpoint


class CountdownCancelAllConfig(TypedDict):
  """Kill-switch config for one underlying."""

  underlying: NotRequired[str]
  """Underlying asset."""
  countdownTime: NotRequired[int]
  """Countdown time in milliseconds. Only active configs (nonzero) are returned."""


class CountdownCancelAllGet(RpcEndpoint):
  """Get the auto-cancel-all-open-orders (kill-switch) config for each underlying. Only active configs are returned — an underlying with countdownTime turned off (0) is omitted."""

  async def countdown_cancel_all_get(
    self,
    *,
    underlying: str | None = None,
    validate: bool | None = None,
  ) -> list[CountdownCancelAllConfig]:
    """Get the auto-cancel-all-open-orders (kill-switch) config for each underlying. Only active configs are returned — an underlying with countdownTime turned off (0) is omitted.

    Args:
      underlying: Underlying asset, e.g. BTCUSDT.

    References:
      - [Official docs](https://developers.binance.com/docs/derivatives/option/market-maker-endpoints#get-auto-cancel-all-open-orders)
    """
    params = {}
    if underlying is not None:
      params['underlying'] = underlying
    _Response = list[CountdownCancelAllConfig]
    _validator = validator[_Response](_Response)
    return await self.authed_request(
      'GET',
      '/eapi/v1/countdownCancelAll',
      params=params,
      validator=_validator,
      validate=validate,
    )
