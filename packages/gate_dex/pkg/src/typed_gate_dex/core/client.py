"""Root base of the Gate DEX client: construction and lifecycle of its one transport."""

from typing_extensions import Self
from dataclasses import dataclass

from .auth import resolve_credentials
from .endpoint.rpc import RpcClient
from .transport.http import GATE_DEX_API_URL, HttpRpcClient


@dataclass(kw_only=True, frozen=True)
class ClientBase:
  """Holds the one authenticated HTTP client every section of the API shares."""

  client: RpcClient
  """Signed transport every section sends its actions through."""

  @classmethod
  def new(
    cls,
    *,
    api_key: str | None = None,
    api_secret: str | None = None,
    base_url: str = GATE_DEX_API_URL,
    validate: bool = True,
  ) -> Self:
    """Create a client. Every Gate DEX action is authenticated, so credentials are required.

    Args:
      api_key: API Key (AK); read from `GATE_DEX_API_KEY` when omitted.
      api_secret: Secret Key (SK); read from `GATE_DEX_SECRET_KEY` when omitted.
      base_url: API host, overridable for testing.
      validate: Validate responses by default; each call can override it.

    Raises:
      AuthError: No credentials were passed or found in the environment.
    """
    credentials = resolve_credentials(api_key, api_secret)
    return cls(
      client=HttpRpcClient(
        credentials=credentials, base_url=base_url, validate=validate
      )
    )

  async def __aenter__(self) -> Self:
    """Own the shared transport for an `async with` block; every section uses it."""
    await self.client.__aenter__()
    return self

  async def __aexit__(self, exc_type, exc_value, traceback):
    """Release the shared transport, closing any open connection."""
    await self.client.__aexit__(exc_type, exc_value, traceback)
