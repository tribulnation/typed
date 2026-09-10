from typing_extensions import cast
from dataclasses import dataclass

from typed_mexc.futures.streams.core import FuturesStreamsEndpoint
from typed_mexc.futures.streams.core.auth import FuturesPrivateStreamsClient


@dataclass(kw_only=True, frozen=True)
class Login(FuturesStreamsEndpoint):
  async def login(self):
    """
    Authenticate the futures private WebSocket connection.

    References:
      - [MEXC futures WebSocket API](https://www.mexc.com/api-docs/futures/websocket-api/login-authentication)
    """
    # `Login` is only ever composed into `User`, constructed with the private
    # connection (`FuturesStreamsBase`'s own `user_client` field) -- `self.client`'s
    # declared type is the narrower `FuturesStreamsClient` protocol every sibling
    # leaf shares, so the one real method this leaf needs beyond it is resolved here.
    await cast(FuturesPrivateStreamsClient, self.client).authenticate()
