from typing_extensions import TypedDict
from typed_core.validation import validator
from binance.core.endpoint.rpc import RpcEndpoint


class CoinMPositionModeResult(TypedDict):
  """The account's current position mode."""

  dualSidePosition: bool
  """Whether Hedge Mode (dual-side position) is enabled."""


class GetCurrentPositionMode(RpcEndpoint):
  """Get Current Position Mode"""

  async def get_current_position_mode(
    self,
    *,
    validate: bool | None = None,
  ) -> CoinMPositionModeResult:
    """Get the account's current position mode (Hedge Mode or One-way Mode).

    References:
      - [Official docs](https://developers.binance.com/en/docs/catalog/core-trading-derivatives-trading-coin-m-futures/api/rest-api/trade#get-current-position-mode)
    """
    _Response = CoinMPositionModeResult
    _validator = validator[_Response](_Response)
    return await self.authed_request(
      'GET', '/dapi/v1/positionSide/dual', validator=_validator, validate=validate
    )
