"""`ClientBase`: what the `Extended` root inherits, credential resolution and the shared
transports every surface is composed over.

The root is the only owner of both transports: entering it opens nothing (the REST pool
connects lazily, each stream connects when subscribed) and leaving it closes them.
"""

from typing_extensions import Self
from dataclasses import dataclass

from typed_core.http import HttpClient

from .auth import Credentials, resolve_credentials
from .exc import AuthError, BadRequest
from .networks import NETWORKS, Network, NetworkProfile
from .stark.backend import BackendName
from .stark.settlement import StarkAccount
from .transport.http import DEFAULT_USER_AGENT, HttpRpcClient
from .transport.ws import SocketStreamClient


@dataclass(kw_only=True)
class ClientBase:
  """Network, credentials and the shared transports of one Extended client.

  Every REST surface shares one connection pool (`http`); every stream opens its own
  connection through `streams_client`. `async with client:` closes both on exit.
  """

  network: NetworkProfile
  """Hosts and signing domain of the deployment this client talks to."""
  http: HttpRpcClient
  """REST transport, shared by every REST surface."""
  streams_client: SocketStreamClient
  """WebSocket v1 stream transport (`client.streams`)."""
  validate: bool = True
  """Validate responses by default."""

  @classmethod
  def new(
    cls,
    *,
    network: Network = 'mainnet',
    api_key: str | None = None,
    stark_private_key: str | None = None,
    stark_public_key: str | None = None,
    vault: int | str | None = None,
    public: bool = False,
    validate: bool = True,
    user_agent: str = DEFAULT_USER_AGENT,
    stark_backend: BackendName | None = None,
  ) -> Self:
    """Build a client. Three modes: signing (API key, Stark private key and vault: every
    surface), read-only (an API key alone: private reads and unsigned writes, no orders,
    transfers or withdrawals) and `public=True` (market data and public streams).

    Arguments fall back to environment variables, prefixed `EXTENDED_` on mainnet and
    `EXTENDED_TESTNET_` on testnet.

    Args:
      network: Deployment: `mainnet` (Starknet) or `testnet` (Starknet Sepolia).
      api_key: The sub-account's API key (`EXTENDED_API_KEY`).
      stark_private_key: The sub-account's Stark private key, hex (`EXTENDED_STARK_PRIVATE_KEY`).
      stark_public_key: Its Stark public key, hex, checked against the private key
        (`EXTENDED_STARK_PUBLIC_KEY`); derived when omitted.
      vault: The sub-account's vault, i.e. position id (`EXTENDED_VAULT`).
      public: Skip credentials entirely.
      validate: Validate responses by default.
      user_agent: `User-Agent` sent on every request (the venue rejects requests without one).
      stark_backend: Force a Stark crypto backend: `python`, or `fast-stark-crypto` (the
        default whenever it is installed).

    Raises:
      AuthError: No API key was found (and `public` is false), or the Stark settings are
        incomplete or inconsistent.
      BadRequest: `network` is not a known deployment.
    """
    profile = NETWORKS.get(network)
    if profile is None:
      raise BadRequest(
        f'Unknown network {network!r}: one of {", ".join(map(repr, NETWORKS))}'
      )
    credentials = resolve_credentials(
      profile=profile,
      public=public,
      api_key=api_key,
      stark_private_key=stark_private_key,
      stark_public_key=stark_public_key,
      vault=vault,
      backend=stark_backend,
    )
    return cls(
      network=profile,
      http=HttpRpcClient(
        network=profile,
        http=HttpClient(),
        credentials=credentials,
        user_agent=user_agent,
        validate=validate,
      ),
      streams_client=SocketStreamClient(
        base_url=profile.stream_url,
        credentials=credentials,
        user_agent=user_agent,
        validate=validate,
      ),
      validate=validate,
    )

  @property
  def credentials(self) -> Credentials | None:
    """The client's credentials; `None` for a public client."""
    return self.http.credentials

  @property
  def stark_account(self) -> StarkAccount:
    """The Stark key pair and vault signed calls use.

    Raises:
      AuthError: The client has no Stark private key.
    """
    stark = self.credentials.stark if self.credentials is not None else None
    if stark is None:
      raise AuthError(
        'No Stark account: build the client with `stark_private_key` and `vault`.'
      )
    return stark

  async def __aenter__(self) -> Self:
    """Take ownership of both transports. Nothing connects yet."""
    await self.http.__aenter__()
    await self.streams_client.__aenter__()
    return self

  async def __aexit__(self, exc_type, exc_value, traceback):
    """Close every open stream and the REST connection pool."""
    try:
      await self.streams_client.__aexit__(exc_type, exc_value, traceback)
    finally:
      await self.http.__aexit__(exc_type, exc_value, traceback)
