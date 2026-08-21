"""Hand-written PoC for the `crypto_ws` surface — a plain connect/authenticate/receive
wrapper, since there's no subscribe/unsubscribe protocol to fit `StreamEndpoint`'s
shape (see `spec/core.md`). Every notification stays a permissive `dict`, matching
the spec's own deliberate choice for all 34 documented notification types.
"""

from dataclasses import dataclass
from typing_extensions import Any, AsyncIterator, Self

from typed_bit2me.core.transport.ws.crypto import CryptoWsClient


@dataclass(kw_only=True, frozen=True)
class CryptoWs:
  client: CryptoWsClient

  async def __aenter__(self) -> Self:
    await self.client.__aenter__()
    return self

  async def __aexit__(self, exc_type, exc_value, traceback):
    await self.client.__aexit__(exc_type, exc_value, traceback)

  async def authenticate(self, *, token: str | None = None, api_key: str | None = None):
    """Authenticate the connection, so account notifications start arriving.

    Args:
      token: A JWT to authenticate with — confirmed working live; mint one with
        `bit2me.core.auth.mint_ws_token`, the same flow `trading_ws` uses.
      api_key: A Bit2Me API key to authenticate with, when no `token` is given.
        Documented by Bit2Me, but currently known to reproducibly fail (an abrupt WS
        close, code `1006`) rather than authenticate — prefer `token`.

    References:
      - [Bit2Me API docs](https://api.bit2me.com/doc#section/WebSockets)
    """
    await self.client.authenticate(token=token, api_key=api_key)

  def notifications(self) -> AsyncIterator[dict[str, Any]]:
    """Every account notification received after authenticating."""
    return self.client.notifications()
