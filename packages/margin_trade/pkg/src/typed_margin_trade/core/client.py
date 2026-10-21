"""`ClientBase`: what the `MarginTrade` root inherits: network selection, credential
resolution, and the two transports every surface is composed over.

The root is the only owner of those transports: entering it takes ownership of both (opening
nothing: each connects lazily, on first use) and leaving it closes them. Surfaces share them,
so a surface's own `async with` opens and closes nothing.
"""

from typing_extensions import Self
from contextlib import AsyncExitStack
from dataclasses import dataclass
from datetime import timedelta

from typed_core.http import HttpClient

from .auth import Credentials, Wallet, resolve_credentials
from .networks import NetworkProfile, network_profile
from .transport.http import HttpRpcClient
from .transport.ws import SocketClient


@dataclass(kw_only=True)
class ClientBase:
  """Network, signer and the shared transports of one Margin Trade client.

  Every HTTP surface (`info`, `exchange`, `user`, `solana`, `public`, `coingecko`) shares one
  connection pool (`http`); `streams` uses the one WebSocket connection (`ws`).
  """

  network: NetworkProfile
  """Hosts and network code of the deployment this client talks to."""
  http: HttpRpcClient
  """HTTP transport, shared by every HTTP surface."""
  ws: SocketClient
  """WebSocket transport (`client.streams`)."""
  validate: bool = True
  """Validate responses by default."""

  @classmethod
  def new(
    cls,
    wallet: Wallet | str | bytes | None = None,
    *,
    vault: str | None = None,
    mainnet: bool = True,
    public: bool = False,
    validate: bool = True,
    ping_interval: timedelta = timedelta(seconds=10),
  ) -> Self:
    """Build a client.

    Args:
      wallet: Signing key: a `Wallet`, or a private key in any format `Wallet.parse` takes
        (a hex 32-byte seed, a base58 64-byte Solana secret key, ...). Needed for
        `exchange`, `solana` and the signed `user` calls; never read from the environment.
      vault: Master account address, when `wallet` is an approved agent ("API wallet").
      mainnet: Talk to mainnet when true, testnet when false. Picks the host and the network
        code signed into every envelope together.
      public: Build without a wallet (none may be given): `info`, `public`, `coingecko`,
        `streams` and the unsigned `user` reads only.
      validate: Validate responses by default.
      ping_interval: How often `streams` pings its connection. The venue closes a connection
        pinged every 30 s within about a minute; keep it well below that.

    Raises:
      ValueError: `public` is true and a `wallet` or `vault` was given too.
      AuthError: No wallet was given and `public` is false, or the key is malformed.

    References:
      - [API overview](https://docs.margin.trade/api/overview)
      - [Authentication](https://docs.margin.trade/api/authentication)
    """
    profile = network_profile(mainnet)
    credentials = resolve_credentials(wallet, vault=vault, public=public)
    return cls(
      network=profile,
      http=HttpRpcClient(
        network=profile, http=HttpClient(), credentials=credentials, validate=validate
      ),
      ws=SocketClient.new(
        profile.ws_url, validate=validate, ping_interval=ping_interval
      ),
      validate=validate,
    )

  @property
  def credentials(self) -> Credentials | None:
    """The signer, or `None` for a public client."""
    return self.http.credentials

  @property
  def account(self) -> str | None:
    """The account signed calls act on: the master address (`vault`) for an agent, the
    wallet's own address otherwise; `None` for a public client.
    """
    return None if self.credentials is None else self.credentials.account

  async def __aenter__(self) -> Self:
    """Take ownership of both transports. Nothing connects until first use.

    If entering the WebSocket side fails, the already-entered HTTP side is closed again.
    """
    async with AsyncExitStack() as stack:
      await stack.enter_async_context(self.http)
      await stack.enter_async_context(self.ws)
      stack.pop_all()
    return self

  async def __aexit__(self, exc_type, exc_value, traceback):
    """Close both transports, even if closing one of them raises."""
    async with AsyncExitStack() as stack:
      stack.push_async_exit(self.http)
      stack.push_async_exit(self.ws)
