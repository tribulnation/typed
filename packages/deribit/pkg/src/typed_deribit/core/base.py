"""Deribit client root base (design §5c): a hand-written class holding the two
transports every generated section forwards -- one HTTP-backed JSON-RPC connection
(`rpc_client`) and one shared WebSocket connection (`ws_client`), which itself answers
both roles Deribit's socket genuinely serves on one connection: the alternate transport
for every dual-transport rpc method, and the client backing the whole `streams`
subscription surface.
"""

from typing_extensions import Literal, Self
from dataclasses import dataclass

from .auth import Credentials, resolve_credentials
from .transport.http import HmacHttpRpcClient, OAuthHttpRpcClient, resolve_http_base_url
from .transport.ws import SocketRpcStreamClient, resolve_ws_url

HttpAuth = Literal['token', 'hmac']


@dataclass(kw_only=True, frozen=True)
class ClientBase:
  """Deribit client root: builds and owns the two physical transports every generated
  section forwards unchanged."""

  rpc_client: OAuthHttpRpcClient | HmacHttpRpcClient
  ws_client: SocketRpcStreamClient

  @classmethod
  def new(
    cls,
    *,
    client_id: str | None = None,
    client_secret: str | None = None,
    public: bool = False,
    testnet: bool = False,
    http_auth: HttpAuth = 'token',
    validate: bool = True,
  ) -> Self:
    """Create a Deribit client. Connects nothing yet -- both transports connect lazily,
    on first real use.

    Args:
      client_id: Deribit API client id; read from `{TEST_,}DERIBIT_CLIENT_ID` when
        omitted (prefix picked by `testnet`).
      client_secret: Deribit API client secret; read from `{TEST_,}DERIBIT_CLIENT_SECRET`
        when omitted.
      public: Build a credential-free client instead of requiring one.
      testnet: Target `test.deribit.com` (HTTP) / `wss://test.deribit.com` (WS) instead
        of the mainnet hosts, and read the `TEST_`-prefixed environment variables.
      http_auth: The HTTP transport's authentication scheme. `'token'` (default)
        exchanges `client_id`/`client_secret` for a Bearer token via `public/auth`,
        cached and refreshed automatically. `'hmac'` signs every request individually
        instead (Deribit's `client_signature` grant) -- see `core.auth`. The WebSocket
        transport always uses token auth; `http_auth` has no effect on it.
      validate: Validate responses by default.

    Raises:
      AuthError: `public` is false and no credentials were passed or found in the
        environment.

    References:
      - [Deribit API docs](https://docs.deribit.com/)
    """
    credentials = resolve_credentials(
      client_id, client_secret, public=public, testnet=testnet
    )
    http_base_url = resolve_http_base_url(testnet)
    rpc_client = (
      HmacHttpRpcClient(
        base_url=http_base_url, credentials=credentials, validate=validate
      )
      if http_auth == 'hmac'
      else OAuthHttpRpcClient(
        base_url=http_base_url, credentials=credentials, validate=validate
      )
    )
    ws_client = SocketRpcStreamClient.new(
      resolve_ws_url(testnet), credentials=credentials, validate=validate
    )
    return cls(rpc_client=rpc_client, ws_client=ws_client)

  async def __aenter__(self) -> Self:
    await self.rpc_client.__aenter__()
    await self.ws_client.__aenter__()
    return self

  async def __aexit__(self, exc_type, exc_value, traceback):
    await self.rpc_client.__aexit__(exc_type, exc_value, traceback)
    await self.ws_client.__aexit__(exc_type, exc_value, traceback)
