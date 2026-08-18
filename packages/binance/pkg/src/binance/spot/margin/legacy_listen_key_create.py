from typing_extensions import TypedDict
from typed_core.validation import validator
from binance.core.endpoint.rpc import RpcEndpoint


class LegacyMarginListenKey(TypedDict):
  """Listen key identifying a cross margin user data stream (legacy path)."""

  listenKey: str
  """Listen key used to connect to the cross margin user data WebSocket stream."""


class LegacyListenKeyCreate(RpcEndpoint):
  """Start a new cross margin user data stream (legacy path) and return a listen key used to connect to it over WebSocket. The stream closes after 60 minutes unless kept alive; if the account already has an active listen key, that key is returned and its validity extended."""

  async def legacy_listen_key_create(
    self,
    *,
    validate: bool | None = None,
  ) -> LegacyMarginListenKey:
    """Start a new cross margin user data stream (legacy path) and return a listen key used to connect to it over WebSocket. The stream closes after 60 minutes unless kept alive; if the account already has an active listen key, that key is returned and its validity extended.

    References:
      - [Official docs](https://github.com/binance/binance-spot-api-docs/blob/master/margin-api.md)
    """
    _Response = LegacyMarginListenKey
    _validator = validator[_Response](_Response)
    return await self.request(
      'POST', '/sapi/v1/userDataStream', validator=_validator, validate=validate
    )
