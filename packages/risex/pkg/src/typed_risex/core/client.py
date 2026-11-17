"""`ClientBase`: what the `RISEx` root inherits: credential resolution, and the shared
transports every surface is composed over.

The root is the only owner of both transports: entering it opens nothing (the REST pool
connects lazily, the feed on its first subscription) and leaving it closes them.
"""

from typing_extensions import Self
from dataclasses import dataclass

from .auth import Credentials, resolve_credentials
from .exc import BadRequest
from .networks import NETWORKS, Network, NetworkProfile
from .signing import Signing
from .transport.http import HttpRpcClient
from .transport.ws import SocketStreamClient


@dataclass(kw_only=True)
class ClientBase:
  """Network, credentials and the shared transports of one RISEx client.

  Every REST surface shares one connection pool (`http`); every channel shares one feed
  connection (`streams_client`). `async with client:` closes both on exit.
  """

  network: NetworkProfile
  """Hosts and chain of the deployment this client talks to."""
  http: HttpRpcClient
  """REST transport, shared by every REST surface."""
  streams_client: SocketStreamClient
  """WebSocket feed transport (`client.streams`)."""
  validate: bool = True
  """Validate responses by default."""

  @classmethod
  def new(
    cls,
    *,
    network: Network = 'mainnet',
    account_key: str | None = None,
    signer_key: str | None = None,
    account: str | None = None,
    public: bool = False,
    validate: bool = True,
  ) -> Self:
    """Build a client.

    Keys fall back to `RISEX_ACCOUNT_KEY`, `RISEX_SIGNER_KEY` and `RISEX_ACCOUNT` when
    neither key is passed. The signer key alone (with the account's address) is enough to
    trade, log in and read private channels; the account key is needed to register or
    revoke a signer and to grant allowances.

    Args:
      network: Deployment: `mainnet` (access-gated) or `testnet`.
      account_key: The account's private key, hex.
      signer_key: The registered signer (session key)'s private key, hex.
      account: The account's address; needed with a signer key alone.
      public: Skip credentials entirely: public data only.
      validate: Validate responses by default.

    Raises:
      AuthError: No key was found (and `public` is false), or the keys and account don't
        fit together.
      BadRequest: `network` is not a known deployment.
    """
    profile = NETWORKS.get(network)
    if profile is None:
      raise BadRequest(
        f'Unknown network {network!r}: one of {", ".join(map(repr, NETWORKS))}'
      )
    credentials = resolve_credentials(
      account_key=account_key, signer_key=signer_key, account=account, public=public
    )
    signing = Signing(network=profile, credentials=credentials)
    http = HttpRpcClient(network=profile, signing=signing, validate=validate)
    return cls(
      network=profile,
      http=http,
      streams_client=SocketStreamClient.new(
        profile.ws_url, signing=signing, api=http, validate=validate
      ),
      validate=validate,
    )

  @property
  def credentials(self) -> Credentials | None:
    """The client's credentials; `None` for a public client."""
    return self.http.signing.credentials

  async def __aenter__(self) -> Self:
    """Take ownership of both transports. Nothing connects yet."""
    await self.http.__aenter__()
    await self.streams_client.__aenter__()
    return self

  async def __aexit__(self, exc_type, exc_value, traceback):
    """Close the feed connection and the REST connection pool."""
    try:
      await self.streams_client.__aexit__(exc_type, exc_value, traceback)
    finally:
      await self.http.__aexit__(exc_type, exc_value, traceback)
