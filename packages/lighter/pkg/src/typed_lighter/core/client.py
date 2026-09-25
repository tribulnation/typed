"""`ClientBase`: what the `Lighter` root inherits, credential resolution and the
shared transports every surface is composed over.

The root is the only owner of those transports: entering it takes ownership of all four
(opening nothing: each connects lazily, on first use) and leaving it closes them. Surfaces
(`client.api`, `client.tx`, `client.streams`, `client.explorer`, `client.deposit_bridge`)
share them, so a surface's own `async with` opens and closes nothing.
"""

from typing_extensions import Awaitable, Mapping, Self, TypeVar
from contextlib import AsyncExitStack
from dataclasses import dataclass
import asyncio
import os

from typed_core.http import HttpClient

from ..deposit_bridge.core import BridgeClient
from ..explorer.core import ExplorerClient
from ..scaling import Scaler
from .auth import (
  Credentials,
  DerivedTokens,
  StaticToken,
  TokenProvider,
  env_int,
  resolve_api_keys,
)
from .exc import AuthError, BadRequest
from .networks import NETWORKS, Network, NetworkProfile
from .signer.account import AccountSigner
from .signer.key import Signer
from .transport.http import HttpRpcClient
from .transport.ws import SocketClient

T = TypeVar('T')


async def run_to_completion(work: Awaitable[T]) -> T:
  """Await `work` to its end even if the caller is cancelled meanwhile, then re-raise that
  cancellation.

  Closing transports has to finish once started: a close interrupted halfway (a WebSocket
  closing handshake, a connection pool shutting down) would leave a connection open that
  nothing owns any more.

  Args:
    work: The cleanup to run.
  """
  task = asyncio.ensure_future(work)
  interrupted = False
  while not task.done():
    try:
      await asyncio.wait({task})
    except asyncio.CancelledError:
      interrupted = True
  if interrupted:
    error = None if task.cancelled() else task.exception()
    raise asyncio.CancelledError from error
  return task.result()


def resolve_credentials(
  *,
  profile: NetworkProfile,
  public: bool,
  account_index: int | None,
  api_keys: Mapping[int, str | Signer] | None,
  api_key_index: int | None,
  api_private_key: str | None,
  eth_private_key: str | None,
  auth_token: str | None,
) -> Credentials:
  """Resolve the one signer and token source every surface shares, from arguments first and
  `LIGHTER_*` environment variables second.

  Environment variables carry the network's prefix: `LIGHTER_*` on mainnet,
  `LIGHTER_TESTNET_*`, `LIGHTER_ROBINHOOD_*`, `LIGHTER_ROBINHOOD_TESTNET_*`.

  Raises:
    AuthError: No usable credentials were found and `public` is false.
  """
  if public:
    return Credentials(signer=None, tokens=None)
  prefix = profile.env_prefix
  if account_index is None:
    account_index = env_int(f'{prefix}_ACCOUNT_INDEX')
  keys = resolve_api_keys(api_keys, api_key_index, api_private_key, prefix=prefix)
  if keys is not None:
    if account_index is None:
      raise AuthError(
        f'API keys need an account: set {prefix}_ACCOUNT_INDEX or pass `account_index`.'
      )
    account_signer = AccountSigner.new(
      account_index=account_index,
      api_keys=keys,
      chain_id=profile.chain_id,
      eth_private_key=eth_private_key
      or os.environ.get(f'{prefix}_ETH_PRIVATE_KEY')
      or None,
    )
    return Credentials(
      signer=account_signer, tokens=DerivedTokens(signer=account_signer)
    )
  token = auth_token or os.environ.get(f'{prefix}_AUTH_TOKEN')
  if token:
    tokens: TokenProvider = StaticToken.parse(token)
    if account_index is not None and account_index != tokens.account_index:
      raise AuthError(
        'The auth token belongs to a different account than `account_index`.'
      )
    return Credentials(signer=None, tokens=tokens)
  raise AuthError(
    f'No credentials: set {prefix}_ACCOUNT_INDEX with {prefix}_API_KEY_INDEX/'
    f'{prefix}_API_PRIVATE_KEY (or {prefix}_AUTH_TOKEN for read-only access), '
    'or build with `public=True`.'
  )


@dataclass(kw_only=True)
class ClientBase:
  """Credentials, network profile and the shared transports of one Lighter client.

  `api` and `tx` share one REST connection pool (`http`); `streams` and `tx` share one
  `/stream` WebSocket connection (`ws`). The explorer and the deposit bridge have hosts of
  their own. This root is the only owner of all four: `async with client:` closes them on
  exit, and nothing else does.
  """

  network: NetworkProfile
  """URLs and chain id of the deployment this client talks to."""
  http: HttpRpcClient
  """Main REST API transport (`client.api`, and `client.tx` over HTTP)."""
  ws: SocketClient
  """The `/stream` WebSocket transport (`client.streams`, and `client.tx` over WebSocket)."""
  explorer_client: ExplorerClient
  """Explorer API transport (`client.explorer`)."""
  bridge_client: BridgeClient
  """Deposit bridge transport (`client.deposit_bridge`)."""
  account_signer: AccountSigner | None
  """The local signer, when the client was built with API keys."""
  validate: bool = True
  """Validate responses by default."""

  @classmethod
  def new(
    cls,
    *,
    network: Network = 'mainnet',
    account_index: int | None = None,
    api_keys: Mapping[int, str | Signer] | None = None,
    api_key_index: int | None = None,
    api_private_key: str | None = None,
    eth_private_key: str | None = None,
    auth_token: str | None = None,
    bridge_api_key: str | None = None,
    public: bool = False,
    validate: bool = True,
  ) -> Self:
    """Build a client. Three credential modes: full (API keys: every surface), read-only
    (an auth token: private reads and streams, no transactions) and `public=True`.

    Args:
      network: Deployment; its URLs and chain id are always picked together.
      account_index: Account the credentials belong to (`{prefix}_ACCOUNT_INDEX`, where
        `{prefix}` is the network's: `LIGHTER` on mainnet, `LIGHTER_TESTNET`,
        `LIGHTER_ROBINHOOD`, `LIGHTER_ROBINHOOD_TESTNET`).
      api_keys: API keys by slot index, for several keys at once: hex private keys, or any
        `Signer` implementation (an HSM, a signing service, a compiled backend).
      api_key_index: Slot of a single API key (`{prefix}_API_KEY_INDEX`).
      api_private_key: Private key of that single API key (`{prefix}_API_PRIVATE_KEY`).
      eth_private_key: L1 wallet key, for the few L1-signed transactions
        (`{prefix}_ETH_PRIVATE_KEY`).
      auth_token: Read-only `ro:` token (or a pre-signed standard token), used when no API
        key is configured (`{prefix}_AUTH_TOKEN`).
      bridge_api_key: Deposit bridge key (`{prefix}_BRIDGE_API_KEY`).
      public: Skip credentials entirely: public reads and streams only.
      validate: Validate responses by default.

    Raises:
      AuthError: No usable credentials were found (and `public` is false), or an API
        private key is malformed.
      BadRequest: `network` is not a known deployment.
    """
    profile = NETWORKS.get(network)
    if profile is None:
      raise BadRequest(
        f'Unknown network {network!r}: one of {", ".join(map(repr, NETWORKS))}'
      )
    bridge_variable = f'{profile.env_prefix}_BRIDGE_API_KEY'
    credentials = resolve_credentials(
      profile=profile,
      public=public,
      account_index=account_index,
      api_keys=api_keys,
      api_key_index=api_key_index,
      api_private_key=api_private_key,
      eth_private_key=eth_private_key,
      auth_token=auth_token,
    )
    return cls(
      network=profile,
      http=HttpRpcClient(
        base_url=profile.api_url,
        http=HttpClient(),
        tokens=credentials.tokens,
        validate=validate,
      ),
      ws=SocketClient.new(profile.ws_url, tokens=credentials.tokens, validate=validate),
      explorer_client=ExplorerClient(base_url=profile.explorer_url, validate=validate),
      bridge_client=BridgeClient(
        api_key=bridge_api_key or os.environ.get(bridge_variable) or None,
        api_key_variable=bridge_variable,
        validate=validate,
      ),
      account_signer=credentials.signer,
      validate=validate,
    )

  @property
  def account_index(self) -> int | None:
    """Account the client's credentials belong to: the API keys' account in full mode, the
    auth token's in read-only mode, `None` for a public client."""
    if self.account_signer is not None:
      return self.account_signer.account_index
    tokens = self.http.tokens
    return None if tokens is None else tokens.account_index

  async def scaler(self, market_id: int, *, validate: bool | None = None) -> Scaler:
    """Fetch a market's price and size decimals once, for converting prices and sizes to
    the scaled integers `client.tx` and `client.signer` take, and back.

    Args:
      market_id: Perp or spot market id.
      validate: Override response validation for the one request.

    Raises:
      BadRequest: The venue does not know the market.

    Examples:
      ```python
      from decimal import Decimal

      scaler = await client.scaler(0)
      price = scaler.price(Decimal('2500.5'))  # 250050: ETH prices have 2 decimals
      scaler.price_of(price)  # Decimal('2500.5')
      ```
    """
    return await Scaler.fetch(self.http, market_id, validate=validate)

  @property
  def signer(self) -> AccountSigner:
    """Local signing: one sign twin per `tx` method, plus auth tokens and key generation.

    Raises:
      AuthError: The client was built without API keys.
    """
    if self.account_signer is None:
      raise AuthError('Signing needs API keys: build the client with `api_keys=...`.')
    return self.account_signer

  @property
  def transports(
    self,
  ) -> tuple[HttpRpcClient, SocketClient, ExplorerClient, BridgeClient]:
    """The four transports this root owns, in the order it enters them."""
    return (self.http, self.ws, self.explorer_client, self.bridge_client)

  async def close_transports(self, exc_type=None, exc_value=None, traceback=None):
    """Close every transport, in reverse order; closing one never opens it.

    Every close runs even if another raises, and all of them run to completion even if
    the caller is cancelled meanwhile (the cancellation is re-raised afterwards), so no
    transport is left open. An error raised by a close propagates after the rest have run
    (as the cancellation's cause, when the caller was cancelled).
    """
    stack = AsyncExitStack()
    for transport in self.transports:
      stack.push_async_exit(transport)
    await run_to_completion(stack.__aexit__(exc_type, exc_value, traceback))

  async def __aenter__(self) -> Self:
    """Take ownership of every transport, in order. Nothing connects: each transport opens
    lazily, on first use.

    If entering fails or is cancelled, every transport is closed before the error
    propagates, including one already opened by use before `async with`.
    """
    try:
      for transport in self.transports:
        await transport.__aenter__()
    except BaseException as e:
      await self.close_transports(type(e), e, e.__traceback__)
      raise
    return self

  async def __aexit__(self, exc_type, exc_value, traceback):
    """Close every transport the client opened: the only place they are closed."""
    await self.close_transports(exc_type, exc_value, traceback)
