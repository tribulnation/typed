"""REST transport: one `RpcClient` for every REST call, owning the connection pool, the
mandatory `User-Agent`, API-key authentication, settlement signing, the envelope and
validation."""

from typing_extensions import Any, Mapping, NotRequired, Self, TypedDict, TypeVar
from dataclasses import dataclass, field
from decimal import Decimal

from typed_core.http import HttpClient
from typed_core.validation import validator
import httpx

from ..auth import Credentials
from ..endpoint.rpc import Method, RpcClient, SignKind
from ..endpoint.wire import query_values
from ..envelope import EnvelopeMode, NotFound, unwrap
from ..exc import AuthError, BadRequest
from ..networks import NetworkProfile
from ..signing import PREPARERS, AssetSettlement, FeeRates, MarketSettlement, SubAccount
from ..stark.settlement import L2Config, StarkAccount

T = TypeVar('T')

DEFAULT_USER_AGENT = 'typed-extended'
"""`User-Agent` sent by default: the venue rejects requests without one (`403`)."""


class L2ConfigWire(TypedDict):
  """`l2Config` of `GET /info/markets`, as signing reads it."""

  collateralId: str
  collateralResolution: int
  syntheticId: str
  syntheticResolution: int


class TradingConfigWire(TypedDict):
  """`tradingConfig` of `GET /info/markets`, as signing reads it."""

  minOrderSizeChange: Decimal
  maxPositionValue: Decimal


class MarketWire(TypedDict):
  """A market of `GET /info/markets`, as signing reads it."""

  name: str
  l2Config: L2ConfigWire
  tradingConfig: TradingConfigWire


class FeeWire(TypedDict):
  """A row of `GET /user/fees`."""

  market: str
  makerFeeRate: Decimal
  takerFeeRate: Decimal


class AccountWire(TypedDict):
  """A sub-account of `GET /user/accounts` or `GET /user/account/info`."""

  accountId: NotRequired[int]
  id: NotRequired[int]
  l2Key: str
  l2Vault: int
  bridgeStarknetAddress: NotRequired[str | None]


class AssetWire(TypedDict):
  """An asset of `GET /info/assets`, as signing reads it."""

  name: str
  starkexId: str
  starkexResolution: int


def sub_account(row: AccountWire) -> SubAccount:
  """A sub-account's Stark identity, from its wire row.

  Raises:
    BadRequest: The row carries no account id.
  """
  account_id = row.get('accountId', row.get('id'))
  if account_id is None:
    raise BadRequest(f'Sub-account without an id: {row!r}')
  bridge = row.get('bridgeStarknetAddress')
  return SubAccount(
    account_id=account_id,
    l2_key=int(row['l2Key'], 16),
    l2_vault=row['l2Vault'],
    bridge_starknet_address=int(bridge, 16) if bridge else None,
  )


@dataclass(kw_only=True)
class HttpRpcClient(RpcClient):
  """REST client: connection pool, authentication, signing, envelope and validation.

  Also the `SigningContext` signed calls read venue parameters through: markets, fee
  rates, the account and assets are fetched on first use and cached for the client's life.
  """

  network: NetworkProfile
  """Deployment: REST base URL and signing domain."""
  http: HttpClient = field(default_factory=HttpClient)
  """Connection pool."""
  credentials: Credentials | None = None
  """API key and Stark account; `None` means only public calls can be made."""
  user_agent: str = DEFAULT_USER_AGENT
  """`User-Agent` header, mandatory on every request."""
  validate: bool = True
  """Validate responses by default."""
  markets: dict[str, MarketSettlement] = field(
    default_factory=dict, init=False, repr=False
  )
  """Cached market settlement parameters, by market name."""
  fees: dict[str, FeeRates] = field(default_factory=dict, init=False, repr=False)
  """Cached account fee rates, by market name."""
  assets: dict[str, AssetSettlement] = field(
    default_factory=dict, init=False, repr=False
  )
  """Cached asset settlement parameters, by asset name."""
  account: SubAccount | None = field(default=None, init=False, repr=False)
  """Cached identity of the API key's sub-account."""

  async def __aenter__(self) -> Self:
    """Take ownership of the connection pool without connecting (it opens lazily)."""
    await self.http.__aenter__()
    return self

  async def __aexit__(self, exc_type, exc_value, traceback):
    """Close the connection pool, if it was opened. Only the root client calls this."""
    await self.http.__aexit__(exc_type, exc_value, traceback)

  def should_validate(self, validate: bool | None = None) -> bool:
    """Per-call override of the client-level `validate` default."""
    return self.validate if validate is None else validate

  def require_credentials(self) -> Credentials:
    """The credentials, for a private call.

    Raises:
      AuthError: The client was built with `public=True`.
    """
    if self.credentials is None:
      raise AuthError(
        'This call needs an API key: build the client with credentials, not `public=True`.'
      )
    return self.credentials

  def require_stark(self) -> StarkAccount:
    """The Stark account, for a signed call.

    Raises:
      AuthError: The client has no Stark private key and vault.
    """
    stark = self.require_credentials().stark
    if stark is None:
      prefix = self.network.env_prefix
      raise AuthError(
        'This call is signed: configure the Stark private key and vault '
        f'({prefix}_STARK_PRIVATE_KEY, {prefix}_VAULT).'
      )
    return stark

  def headers(self, *, auth: bool) -> dict[str, str]:
    """Headers for one request: `User-Agent` always, `X-Api-Key` when `auth`."""
    headers = {'User-Agent': self.user_agent, 'Accept': 'application/json'}
    if auth:
      headers['X-Api-Key'] = self.require_credentials().api_key
    return headers

  async def request(
    self,
    method: Method,
    path: str,
    *,
    params: Mapping[str, Any] | None = None,
    json: Mapping[str, Any] | None = None,
    auth: bool = False,
    sign: SignKind | None = None,
    envelope: EnvelopeMode = 'data',
    not_found: NotFound | None = None,
    validator: validator[T] | None = None,
    validate: bool | None = None,
  ) -> T:
    """Send one request to the REST base URL plus `path`, unwrap the envelope, then validate.

    Args:
      method: HTTP verb.
      path: URL path below `/api/v1`.
      params: Query parameters.
      json: JSON body fields.
      auth: Send the API key.
      sign: Complete `json` and attach this Stark settlement before sending.
      envelope: What the successful envelope unwraps to (`core.envelope.EnvelopeMode`).
      not_found: What a bodiless `404` returns instead of raising (`core.envelope.NotFound`).
      validator: Response validator.
      validate: Per-call override of response validation.

    Raises:
      AuthError: The call needs credentials this client does not have, or the venue
        rejected them.
    """
    headers = self.headers(auth=auth or sign is not None)
    body = dict(json) if json is not None else None
    if sign is not None:
      account = self.require_stark()
      body = await PREPARERS[sign](
        body or {}, account=account, network=self.network, context=self
      )
    response = await self.http.request(
      method,
      self.network.api_url + path,
      params=query_values(params) if params else None,
      json=body,
      headers=headers,
    )
    return self.result(
      response,
      validator=validator,
      validate=validate,
      envelope=envelope,
      not_found=not_found,
    )

  def result(
    self,
    response: httpx.Response,
    validator: validator[T] | None = None,
    *,
    validate: bool | None = None,
    envelope: EnvelopeMode = 'data',
    not_found: NotFound | None = None,
  ) -> T:
    """Unwrap the envelope and map errors, then validate."""
    payload = unwrap(response, envelope=envelope, not_found=not_found)
    if validator is not None and self.should_validate(validate):
      return validator.python(payload)
    return payload

  async def market_settlement(self, market: str) -> MarketSettlement:
    """A market's settlement parameters (`GET /info/markets?market=`), cached.

    Raises:
      BadRequest: The venue does not list the market.
    """
    if (cached := self.markets.get(market)) is None:
      rows = await self.request(
        'GET',
        '/info/markets',
        params={'market': [market]},
        validator=validator(list[MarketWire]),
        validate=True,
      )
      row = next((r for r in rows if r['name'] == market), None)
      if row is None:
        raise BadRequest(f'Unknown market {market!r}')
      l2 = row['l2Config']
      cached = self.markets[market] = MarketSettlement(
        l2=L2Config(
          synthetic_id=int(l2['syntheticId'], 16),
          synthetic_resolution=l2['syntheticResolution'],
          collateral_id=int(l2['collateralId'], 16),
          collateral_resolution=l2['collateralResolution'],
        ),
        min_order_size_change=row['tradingConfig']['minOrderSizeChange'],
        max_position_value=row['tradingConfig']['maxPositionValue'],
      )
    return cached

  async def fee_rates(self, market: str) -> FeeRates:
    """The account's fee rates on a market (`GET /user/fees?market=`), cached.

    Raises:
      BadRequest: The venue returns no rates for the market.
    """
    if (cached := self.fees.get(market)) is None:
      rows = await self.request(
        'GET',
        '/user/fees',
        params={'market': market},
        auth=True,
        validator=validator(list[FeeWire]),
        validate=True,
      )
      row = next((r for r in rows if r['market'] == market), None)
      if row is None:
        raise BadRequest(f'No fee rates for market {market!r}')
      cached = self.fees[market] = FeeRates(
        maker=row['makerFeeRate'], taker=row['takerFeeRate']
      )
    return cached

  async def sub_accounts(self) -> list[SubAccount]:
    """Every sub-account of the wallet (`GET /user/accounts`); not cached."""
    rows = await self.request(
      'GET',
      '/user/accounts',
      auth=True,
      validator=validator(list[AccountWire]),
      validate=True,
    )
    return [sub_account(row) for row in rows]

  async def account_info(self) -> SubAccount:
    """The API key's sub-account (`GET /user/account/info`), cached."""
    if self.account is None:
      row = await self.request(
        'GET',
        '/user/account/info',
        auth=True,
        validator=validator(AccountWire),
        validate=True,
      )
      self.account = sub_account(row)
    return self.account

  async def asset_settlement(self, asset: str) -> AssetSettlement:
    """An asset's Stark id and resolution (`GET /info/assets?asset=`), cached.

    Raises:
      BadRequest: The venue does not list the asset.
    """
    if (cached := self.assets.get(asset)) is None:
      rows = await self.request(
        'GET',
        '/info/assets',
        params={'asset': [asset]},
        validator=validator(list[AssetWire]),
        validate=True,
      )
      row = next((r for r in rows if r['name'] == asset), None)
      if row is None:
        raise BadRequest(f'Unknown asset {asset!r}')
      cached = self.assets[asset] = AssetSettlement(
        stark_id=int(row['starkexId'], 16), resolution=row['starkexResolution']
      )
    return cached
