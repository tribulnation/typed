from typing_extensions import NotRequired, TypedDict
from typed_core.validation import validator
from binance.core.endpoint.rpc import RpcEndpoint


class PmStartUserDataStream(TypedDict):
  """Start a new user data stream. The stream will close after 60 minutes unless a keepalive is sent. If the account has an active `listenKey`, that `listenKey` will be returned and its validity will be extended for 60 minutes."""

  listenKey: NotRequired[str]
  """Listen Key."""


class UserDataStreamStart(RpcEndpoint):
  """Start User Data Stream"""

  async def user_data_stream_start(
    self,
    *,
    validate: bool | None = None,
  ) -> PmStartUserDataStream:
    """Start a new user data stream. The stream will close after 60 minutes unless a keepalive is sent. If the account has an active `listenKey`, that `listenKey` will be returned and its validity will be extended for 60 minutes.

    References:
      - [Official docs](https://developers.binance.com/en/docs/catalog/advanced-trading-derivatives-trading-portfolio-margin/api/rest-api/user-data-streams#start-user-data-stream)
    """
    _Response = PmStartUserDataStream
    _validator = validator[_Response](_Response)
    return await self.request(
      'POST', '/papi/v1/listenKey', validator=_validator, validate=validate
    )
