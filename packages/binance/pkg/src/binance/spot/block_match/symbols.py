from typed_core.validation import validator
from binance.core.endpoint.rpc import RpcEndpoint


class Symbols(RpcEndpoint):
  """Return the trading symbols supported by Spot Block Matching."""

  async def symbols(self, *, validate: bool | None = None) -> list[str]:
    """Return the trading symbols supported by Spot Block Matching.

    References:
      - [Official docs](https://developers.binance.com/en/docs/catalog/vip-and-institutional-spot-block-matching/api/rest-api/~#symbols)
    """
    _Response = list[str]
    _validator = validator[_Response](_Response)
    return await self.authed_request(
      'POST', '/sapi/v1/block-match/symbols', validator=_validator, validate=validate
    )
