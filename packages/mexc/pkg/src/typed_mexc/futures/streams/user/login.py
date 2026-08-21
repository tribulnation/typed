from dataclasses import dataclass

from typed_mexc.futures.streams.core import AuthedStreamsMixin

@dataclass
class Login(AuthedStreamsMixin):
  async def login(self):
    """
    Authenticate the futures private WebSocket connection.

    References:
      - [MEXC futures WebSocket API](https://mexcdevelop.github.io/apidocs/contract_v1_en/#login)
    """
    await self.authenticated_ws.authenticate()
