"""Hand-written construction of every transport, and the bases the composed client
classes subclass.

The root binds one chain. Four surfaces hang off it, each with its own transports:

- `trading`: the Trading API, `client` (REST) and `streams_client` (WebSocket).
- `backend`: the chain's trading backend, `client` (REST) and `streams_client` (event stream).
- `backend_global`: Backend Global, one REST `client`, not chain-bound.
- `pricing`: prices, `client` (REST) and `streams_client` (price stream), not chain-bound.

Every transport is built once, in `GTradeBase.new()`, and forwarded field by field: a
surface's REST routers take `client`, its `streams` router takes `streams_client`.
"""

from typing_extensions import Awaitable, Self, TypedDict
from contextlib import AbstractAsyncContextManager
from dataclasses import dataclass
from datetime import timedelta
import asyncio
import logging

from typed_core.http import HttpClient

from .auth import AgentSigner, Credentials, SigningDomain, Wallet, resolve_credentials
from .chains import (
  BACKEND_GLOBAL_URL,
  PRICING_URL,
  PRICING_WS_URL,
  Chain,
  deployment_of,
)
from .transport.http import PublicHttpClient, TradingHttpClient
from .transport.ws.feed import BackendEventSocket, FeedSocketClient, PricingSocket
from .transport.ws.trading import TradingSocketClient

logger = logging.getLogger(__name__)


async def exit_all(*exits: Awaitable[object]):
  """Run every transport's exit to completion, then raise the first failure.

  One transport failing to close never leaves the others open; the failures after the
  first are logged.
  """
  results = await asyncio.gather(*exits, return_exceptions=True)
  errors = [result for result in results if isinstance(result, BaseException)]
  for error in errors[1:]:
    logger.error('Another transport also failed to close', exc_info=error)
  if errors:
    raise errors[0]


async def enter_all(*transports: AbstractAsyncContextManager[object]):
  """Enter every transport concurrently; if any fails, exit the ones that entered, then
  raise the first failure.

  A failed enter never leaves the others open: the ones that succeeded are exited with
  the failure (a failure while exiting them is logged, never raised instead of it), and
  the enter failures after the first are logged.
  """
  entered: list[AbstractAsyncContextManager[object]] = []

  async def enter(transport: AbstractAsyncContextManager[object]):
    """Enter one transport, recording it once entered."""
    await transport.__aenter__()
    entered.append(transport)

  try:
    results = await asyncio.gather(*map(enter, transports), return_exceptions=True)
    errors = [result for result in results if isinstance(result, BaseException)]
  except BaseException as error:  # cancelled while entering
    errors = [error]
  if not errors:
    return
  error = errors[0]
  for other in errors[1:]:
    logger.error('Another transport also failed to open', exc_info=other)
  try:
    await exit_all(
      *(
        transport.__aexit__(type(error), error, error.__traceback__)
        for transport in entered
      )
    )
  except BaseException as exit_error:
    logger.error(
      'A transport failed to close after another failed to open', exc_info=exit_error
    )
  raise error


class Urls(TypedDict, total=False):
  """URL overrides, each replacing the default the chain selects (for a proxy or a test
  server). Signatures always name the path actually sent."""

  trading: str
  """Trading API chain root, default `https://api.gains.trade/v1/{chain}`."""
  trading_host: str
  """Trading API host, for `/health` and `/ready`, default `https://api.gains.trade`."""
  trading_ws: str
  """Trading API WebSocket, default `wss://api.gains.trade/v1/{chain}/ws`."""
  backend: str
  """Per-chain backend, default `https://backend-{chain}.gains.trade`."""
  backend_ws: str
  """Per-chain backend event stream, default `wss://backend-{chain}.gains.trade`."""
  backend_global: str
  """Backend Global, default `https://backend-global.gains.trade`."""
  pricing: str
  """Pricing REST, default `https://backend-pricing.eu.gains.trade`."""
  pricing_ws: str
  """Pricing stream, default `wss://backend-pricing.eu.gains.trade/v3`."""


@dataclass(kw_only=True, frozen=True)
class TradingClients:
  """The Trading API's transports, REST and WebSocket, and the chain's signing domain."""

  client: TradingHttpClient
  streams_client: TradingSocketClient
  signing_domain: SigningDomain
  """The EIP-712 domain every Trading API signature of the client's chain is bound to:
  pass it to `typed_gtrade.signing`'s builders for the master wallet's signatures."""

  async def __aenter__(self) -> Self:
    await enter_all(self.client, self.streams_client)
    return self

  async def __aexit__(self, exc_type, exc_value, traceback):
    await exit_all(
      self.client.__aexit__(exc_type, exc_value, traceback),
      self.streams_client.__aexit__(exc_type, exc_value, traceback),
    )


@dataclass(kw_only=True, frozen=True)
class TradingBase(TradingClients):
  """Base of the `trading` composite: REST routers sit directly on it (forwarding
  `client`), beside `streams` (forwarding `streams_client`)."""

  @classmethod
  def new(cls, client: TradingClients) -> Self:
    """Unpack already-built transports into this base."""
    return cls(
      client=client.client,
      streams_client=client.streams_client,
      signing_domain=client.signing_domain,
    )


@dataclass(kw_only=True, frozen=True)
class PublicClients:
  """A public backend's transports: REST and a push-only feed."""

  client: PublicHttpClient
  streams_client: FeedSocketClient

  async def __aenter__(self) -> Self:
    await enter_all(self.client, self.streams_client)
    return self

  async def __aexit__(self, exc_type, exc_value, traceback):
    await exit_all(
      self.client.__aexit__(exc_type, exc_value, traceback),
      self.streams_client.__aexit__(exc_type, exc_value, traceback),
    )


@dataclass(kw_only=True, frozen=True)
class PublicBase(PublicClients):
  """Base of the `backend` and `pricing` composites: REST routers sit directly on it
  (forwarding `client`), beside `streams` (forwarding `streams_client`)."""

  @classmethod
  def new(cls, client: PublicClients) -> Self:
    """Unpack already-built transports into this base."""
    return cls(client=client.client, streams_client=client.streams_client)


@dataclass(kw_only=True, frozen=True)
class GTradeBase:
  """Base of the `GTrade` root: the bound chain, and every surface's transports."""

  chain: Chain
  """The chain the Trading API and the per-chain backend serve this client."""
  credentials: Credentials | None
  """`None` for a public client."""
  trading_clients: TradingClients
  backend_clients: PublicClients
  backend_global_client: PublicHttpClient
  pricing_clients: PublicClients

  @classmethod
  def new(
    cls,
    *,
    chain: Chain = 'arbitrum',
    agent: Wallet | None = None,
    api_key: str | None = None,
    public: bool = False,
    validate: bool = True,
    urls: Urls | None = None,
    timeout: float = 5.0,
    ws_timeout: float = 10.0,
  ) -> Self:
    """Create a gTrade client for one chain.

    Three modes: an agent key (every Trading API call: private reads, prepared writes,
    private channels), a read-only API key alone (private reads and channels, no writes),
    and `public=True` (market data, the backends and pricing). When neither credential is
    passed, both are read from `GTRADE_AGENT_PRIVATE_KEY` and `GTRADE_API_KEY`; passing
    either reads neither, so explicit credentials are never mixed with the environment's.

    The client never signs or broadcasts EVM transactions: a write returns the prepared,
    unsigned transaction for the agent to sign and send through its own RPC.

    Args:
      chain: The Trading API and per-chain backend deployment. The Trading API serves
        `arbitrum` only, for now.
      agent: The agent's private key or account: the trader's on-chain trading delegate,
        registered with `trading.agents`.
      api_key: A read-only Trading API key.
      public: Read no credentials: public data only. Passing a credential too is an
        error, never silently ignored.
      validate: Validate responses by default.
      urls: URL overrides per service; omitted ones keep the chain's default.
      timeout: HTTP request timeout, in seconds. Order and position writes are the
        slowest calls: the API validates and simulates the transaction before answering
        with it, so raise this if they time out.
      ws_timeout: WebSocket timeout, in seconds: of each connection handshake, and of the
        Trading API's reply to each subscribe, unsubscribe and `auth` frame (a missing
        reply raises `NetworkError` instead of waiting forever).

    Raises:
      AuthError: `public` is false and no credential was found, or the agent key is invalid.
      ValueError: `chain` is not a known deployment, or `public` is true and a credential
        was passed.
    """
    deployment = deployment_of(chain)
    credentials = resolve_credentials(agent=agent, api_key=api_key, public=public)
    domain = SigningDomain.of(deployment)
    signer = (
      AgentSigner(account=credentials.agent, domain=domain)
      if credentials is not None and credentials.agent is not None
      else None
    )
    key = credentials.api_key if credentials is not None else None
    urls = urls or {}
    ws = timedelta(seconds=ws_timeout)

    def http() -> HttpClient:
      """One HTTP client with the configured timeout."""
      return HttpClient(timeout=timeout)

    return cls(
      chain=chain,
      credentials=credentials,
      trading_clients=TradingClients(
        client=TradingHttpClient(
          base_url=urls.get('trading') or deployment.trading_url,
          host_url=urls.get('trading_host') or deployment.api_url,
          http=http(),
          signer=signer,
          api_key=key,
          validate=validate,
        ),
        streams_client=TradingSocketClient.new(
          urls.get('trading_ws') or deployment.trading_ws_url,
          signer=signer,
          api_key=key,
          validate=validate,
          timeout=ws,
        ),
        signing_domain=domain,
      ),
      backend_clients=PublicClients(
        client=PublicHttpClient(
          base_url=urls.get('backend') or deployment.backend_url,
          http=http(),
          validate=validate,
        ),
        streams_client=FeedSocketClient(
          socket=BackendEventSocket(
            urls.get('backend_ws') or deployment.backend_ws_url, timeout=ws
          ),
          validate=validate,
        ),
      ),
      backend_global_client=PublicHttpClient(
        base_url=urls.get('backend_global') or BACKEND_GLOBAL_URL,
        http=http(),
        validate=validate,
      ),
      pricing_clients=PublicClients(
        client=PublicHttpClient(
          base_url=urls.get('pricing') or PRICING_URL, http=http(), validate=validate
        ),
        streams_client=FeedSocketClient(
          socket=PricingSocket(urls.get('pricing_ws') or PRICING_WS_URL, timeout=ws),
          validate=validate,
        ),
      ),
    )

  async def __aenter__(self) -> Self:
    await enter_all(
      self.trading_clients,
      self.backend_clients,
      self.backend_global_client,
      self.pricing_clients,
    )
    return self

  async def __aexit__(self, exc_type, exc_value, traceback):
    await exit_all(
      self.trading_clients.__aexit__(exc_type, exc_value, traceback),
      self.backend_clients.__aexit__(exc_type, exc_value, traceback),
      self.backend_global_client.__aexit__(exc_type, exc_value, traceback),
      self.pricing_clients.__aexit__(exc_type, exc_value, traceback),
    )
