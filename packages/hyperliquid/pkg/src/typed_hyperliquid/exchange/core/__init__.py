"""Exchange endpoint base: RPC-shaped, wallet-signed, reachable over HTTP or the shared
WebSocket connection. See `spec/core.md` for the full surface writeup.

Every `exchange.*` operation posts a signed `{action, nonce, signature, vaultAddress,
expiresAfter}` envelope to one fixed surface -- `path` (`RpcEndpointSpec.path`, e.g.
`"cancel"`, `"perpDeploy.registerAsset2"`) names the wire `action.type` (its first dotted
segment) and, for a nested sub-action, the further wrapper key(s) the rest of the dotted
path nests the flat `request` fields under (`docs/spec/authoring.md` rule 0's own worked
positional/nested-object cases -- this is the fixed, hand-written convention design §2
delegates that decision to). `vaultAddress`/`expiresAfter`/`nonce` are envelope-level
concerns, not action fields, so a caller-facing `request` declares them (design §7 has no
other channel for a per-call generated parameter) and this method pops them back off
before building the action -- except `vaultTransfer`, whose own action genuinely reuses
both as real action fields (declared `meta: {"envelope_overlap": true}`; see `Meta`).
"""

from typing_extensions import Any, Literal, Mapping, NotRequired, Self, TypedDict, TypeVar, cast
from types import UnionType
from dataclasses import dataclass
from datetime import timedelta

from eth_account.account import Account
from eth_account.signers.local import LocalAccount
from typed_core.exceptions import ApiError, AuthError
from typed_core.http import HttpClient
from typed_core.validation import validator

from typed_hyperliquid.core.endpoint.rpc import RpcClient, RpcEndpoint
from typed_hyperliquid.core.types import timestamp_millis
from typed_hyperliquid.core.urls import http_base_url, ws_url as resolve_ws_url
from typed_hyperliquid.core.wire import dump_request
from typed_hyperliquid.core.ws import SocketClient

from .auth import sign_l1_action, sign_user_signed_action, stringify_decimals
from .envelope import ExchangeResponse, OkResponse, ErrorResponse, raise_on_error
from .transport.http import ExchangeHttpClient
from .transport.ws import ExchangeSocketClient

T = TypeVar('T')

ExchangeClient = RpcClient
"""Transport for Hyperliquid exchange requests -- same shape as the shared `RpcClient`."""

Wallet = LocalAccount | str | bytes | int


def _parse_wallet(wallet: Wallet) -> LocalAccount:
  """Resolve a private key, byte string, or account object into a signer."""
  if isinstance(wallet, LocalAccount):
    return wallet
  return Account.from_key(wallet)


def _pascal_case(value: str) -> str:
  """PascalCase a dotted-or-camelCase wire identifier, matching
  `typed_dev.codegen.layout.class_name` closely enough for the EIP-712 `primaryType` this
  builds -- every user-signed action's own wire `path` (`"agentSendAsset"`, ...) is already
  camelCase with no separators, so this only needs to capitalize the first letter."""
  return value[:1].upper() + value[1:]


class Meta(TypedDict):
  """Per-call quirks `ExchangeCore.request` needs, matching `codegen/config.toml`'s
  `[cores.exchange].meta` JSON Schema exactly (design §2/§6, S27's own precedent for a
  hand-written type matching a spec-declared schema)."""

  scheme: NotRequired[Literal['l1', 'user_signed']]
  """Signing scheme. Defaults to `'l1'` when omitted."""
  action: NotRequired[Literal['ordinary', 'batched']]
  """`'batched'` on the four wire actions (`order`, `cancel`, `cancelByCloid`,
  `batchModify`) whose response carries a per-item `data.statuses` array rather than one
  single result -- S9 (`docs/production_standards.md`): a batched action's own top-level
  `status: "ok"` says nothing about whether any individual order/cancel/modify in the
  batch itself succeeded, so raising on it would either hide a real per-item error or
  false-positive on a mixed-result batch. These four keep returning the whole
  `ExchangeResponse[T]` envelope unraised; every other action raises via `raise_on_error`
  instead, narrowing its return type from `ExchangeResponse[T]` to `T`. Omitted (or
  `'ordinary'`) everywhere else."""
  envelope_overlap: NotRequired[bool]
  """`True` on the one action (`vaultTransfer`) whose own action already declares
  `vaultAddress`/`expiresAfter` as real action fields. Everywhere else, those two are
  purely envelope-level and popped off `values` before the action is built; here the same
  dumped value has to reach both the action body and the envelope."""


_EIP712_SKIP: frozenset[str] = frozenset({'signatureChainId', 'nonce'})
"""Dumped request fields excluded from a user-signed action's own EIP-712 field list:
`signatureChainId` becomes the payload's `domain.chainId`, not a message field;
`nonce` is appended once, separately, always last."""


def _eip712_type(value: Any) -> str:
  """EIP-712 field type for one already-dumped (wire-shape) action value. Correct for
  every field this client's user-signed actions carry today -- all plain strings, an
  integer nonce, or a boolean -- see `auth.py`'s own docstring for the scope of what this
  intentionally doesn't cover (an address/bytes-typed field)."""
  if isinstance(value, bool):
    return 'bool'
  if isinstance(value, int):
    return 'uint64'
  return 'string'


def _build_payload_types(values: Mapping[str, Any]) -> list[dict[str, str]]:
  """Build a user-signed action's EIP-712 `payload_types` list from its dumped, flat
  request fields (`nonce` already excluded by the caller -- appended once, here, always
  last)."""
  types = [{'name': 'hyperliquidChain', 'type': 'string'}]
  for key, value in values.items():
    if key in _EIP712_SKIP:
      continue
    types.append({'name': key, 'type': _eip712_type(value)})
  types.append({'name': 'nonce', 'type': 'uint64'})
  return types


def _build_action(path: str, values: Mapping[str, Any]) -> dict[str, Any]:
  """Build the wire `action` object: `{"type": <first dotted segment>, ...fields}` for a
  flat action, or nested under each further dotted segment for a sub-action
  (`docs/spec/authoring.md` rule 0's worked nested/positional cases). A sub-action whose
  every dumped field collapses to exactly one entry is unwrapped -- sent as that single
  value directly, not wrapped in an enclosing object (Hyperliquid's `perpDeploy.disableDex`
  -- `{"disableDex": "<dex>"}` -- is the worked example): true for every real endpoint
  this shape covers today, since none of them also declares a second, merely-omitted
  optional field alongside the lone required one.

  Args:
    path: The endpoint's wire `type`/nested-path identifier (`RpcEndpointSpec.path`).
    values: The dumped, flat request fields -- envelope-only keys
      (`vaultAddress`/`expiresAfter`, except when `meta.get('envelope_overlap')`) already
      excluded by the caller.
  """
  chain = path.split('.')
  if len(chain) == 1:
    return {'type': chain[0], **values}
  nest = chain[1:]
  inner: Any = next(iter(values.values())) if len(values) == 1 else dict(values)
  for key in reversed(nest[1:]):
    inner = {key: inner}
  return {'type': chain[0], nest[0]: inner}


@dataclass(kw_only=True)
class ExchangeCore(RpcEndpoint):
  """Base for Hyperliquid exchange (signed) endpoint groups."""

  wallet: LocalAccount | None = None
  mainnet: bool = True
  ws_client: RpcClient | None = None
  """The alternate transport a per-call `transport='ws'` selects (`request`'s own
  `transport` parameter). Unset on an instance already built WS-only (`.ws_of`) -- there's
  nothing to switch to, so every call there must stay on the default `transport='http'`
  (`self.client` itself is the WS-backed transport in that case)."""

  async def request(
    self,
    request: Any = None,
    *,
    method: str | None = None,
    path: str,
    meta: Meta,
    validate: bool | None = None,
    request_type: type[Any] | UnionType | None = None,
    response_type: type[T] | UnionType | None = None,
    transport: Literal['http', 'ws'] = 'http',
  ) -> T:
    """Perform one signed `exchange` call: build and sign the wire action, POST or send
    the signed envelope over the requested transport, and validate/unwrap the reply.

    Args:
      request: The generated `Request` value, or `None` for a parameterless action.
      method: Unused -- `exchange` has exactly one wire operation (`POST /exchange`);
        kept only so this signature matches `InfoCore.request`'s.
      path: The wire action type, dotted for a nested sub-action.
      meta: `endpoint.meta`, checked against `codegen/config.toml`'s `[cores.exchange].meta`
        schema at spec-test time (design §2/§6) -- `scheme` selects the signing scheme;
        `action`/`envelope_overlap` select the batched-response and envelope-overlap
        branches below. `vault_scoped` (the one signing fact `meta` never carried) is
        read indirectly, via whether the endpoint's own `request` declares `vaultAddress`.
      validate: Per-call override of response validation.
      request_type: The generated request type, used to serialize `request`.
      response_type: The generated response type, used to validate the reply.
      transport: Which transport carries this call (S23, `docs/production_standards.md`)
        -- `self.client` (`'http'`, the default) or `self.ws_client` (`'ws'`). The
        exchange envelope response is byte-identical on both, so this changes nothing
        else about how the call is built or validated.

    Raises:
      ValueError: `transport='ws'` was requested, but this instance has no WebSocket
        transport configured.
    """
    if self.wallet is None:
      raise AuthError(
        'Exchange is not available for public usage. Construct the client without '
        '`public=True` and provide a private key to use exchange methods.'
      )
    if transport == 'ws':
      if self.ws_client is None:
        raise ValueError('No WebSocket transport is configured for this Exchange client.')
      client = self.ws_client
    else:
      client = self.client
    values = dump_request(request, request_type)
    scheme = meta.get('scheme', 'l1')
    if meta.get('envelope_overlap', False):
      vault_address = values.get('vaultAddress')
      expires_after = values.get('expiresAfter')
    else:
      vault_address = values.pop('vaultAddress', None)
      expires_after = values.pop('expiresAfter', None)

    if scheme == 'l1':
      nonce = timestamp_millis.now()
      action = stringify_decimals(_build_action(path, values))
      signature = sign_l1_action(
        action, wallet=self.wallet, vault_address=vault_address,
        nonce=nonce, expires_after=expires_after, mainnet=self.mainnet,
      )
      wire_action = action
    else:
      caller_nonce = values.pop('nonce', None)
      nonce = caller_nonce if caller_nonce is not None else timestamp_millis.now()
      payload_types = _build_payload_types(values)
      values['nonce'] = nonce
      action = stringify_decimals(_build_action(path, values))
      primary_type = f'HyperliquidTransaction:{_pascal_case(path)}'
      wire_action, signature = sign_user_signed_action(
        action, wallet=self.wallet, payload_types=payload_types,
        primary_type=primary_type, mainnet=self.mainnet,
      )
      vault_address = None
      expires_after = None

    result = await client.request({
      'action': wire_action,
      'nonce': nonce,
      'signature': signature,
      'vaultAddress': vault_address,
      'expiresAfter': expires_after,
    })
    should_validate = self.validate if validate is None else validate
    if meta.get('action') == 'batched':
      # The batched four (`order`/`cancel`/`cancelByCloid`/`batchModify`, each declaring
      # `meta: {"action": "batched"}`) never raise on the wire envelope's own `status`
      # (S9) -- the generated response_type IS the whole `{status, response}` envelope,
      # so it's validated directly, unwrapped by nothing.
      return (
        validator(cast(type, response_type)).python(result)
        if should_validate and response_type is not None
        else result
      )
    # Every other action's response_type is the unwrapped success shape (rule 6) -- so
    # `status`/`response` have to be read off the raw wire envelope first, raising on
    # `status: "err"` (S9) before the success value ever reaches response_type's own
    # validator, which was never built to accept the wrapping envelope at all.
    if isinstance(result, dict) and result.get('status') == 'err':
      raise ApiError(result.get('response'))
    value = result.get('response') if isinstance(result, dict) else result
    if not should_validate or response_type is None:
      return value  # type: ignore[return-value]
    return validator(cast(type, response_type)).python(value)

  @classmethod
  def new(
    cls,
    client: RpcClient,
    *,
    exchange_ws_client: RpcClient | None = None,
    wallet: LocalAccount | None = None,
    mainnet: bool = True,
    validate: bool = True,
  ) -> Self:
    """Build an Exchange core forwarding a root client's already-built transports
    (design §5a) -- not meant to be called directly; `client.exchange`'s generated
    `@cached_property` calls this, forwarding `ClientBase`'s own same-named fields.

    Args:
      client: The active (HTTP-backed, by default) transport.
      exchange_ws_client: The alternate transport a per-call `transport='ws'` selects.
      wallet: Parsed signer, or `None` for a public-only client (every call then raises
        `AuthError`).
      mainnet: Use mainnet signing rules when true, testnet signing rules when false.
      validate: Validate responses.
    """
    return cls(
      client=client, ws_client=exchange_ws_client,
      wallet=wallet, mainnet=mainnet, validate=validate,
    )

  @classmethod
  def http(
    cls,
    wallet: Wallet,
    *,
    mainnet: bool = True,
    validate: bool = True,
    http: HttpClient | None = None,
    ws: SocketClient | None = None,
    base_url: str | None = None,
  ) -> Self:
    """Create an Exchange client, active over HTTP with an optional WebSocket alternate
    (a per-call `transport='ws'`) available on the same instance (S23).

    Args:
      wallet: Private key or account object used to sign exchange actions.
      mainnet: Use mainnet when true, testnet when false.
      validate: Validate responses.
      http: Shared HTTP transport.
      ws: Shared WebSocket transport, selected by a per-call `transport='ws'`. Omit to
        build an HTTP-only instance -- `transport='ws'` then raises `ValueError`.
      base_url: Custom HTTP API root. If provided, takes precedence over `mainnet`.
    """
    client = ExchangeHttpClient(base_url=base_url or http_base_url(mainnet), http=http or HttpClient())
    ws_client = ExchangeSocketClient(ws=ws) if ws is not None else None
    return cls(
      client=client, ws_client=ws_client,
      wallet=_parse_wallet(wallet), mainnet=mainnet, validate=validate,
    )

  @classmethod
  def ws_of(
    cls, wallet: Wallet, *, ws: SocketClient, mainnet: bool = True, validate: bool = True,
  ) -> Self:
    """Create an Exchange client active over an existing WebSocket transport.

    Args:
      wallet: Private key or account object used to sign exchange actions.
      ws: Shared WebSocket transport.
      mainnet: Use mainnet signing rules when true, testnet signing rules when false.
      validate: Validate responses.
    """
    client = ExchangeSocketClient(ws=ws)
    return cls(client=client, wallet=_parse_wallet(wallet), mainnet=mainnet, validate=validate)


__all__ = [
  'ExchangeClient',
  'ExchangeCore',
  'Meta',
  'ExchangeResponse',
  'OkResponse',
  'ErrorResponse',
  'raise_on_error',
  'ExchangeHttpClient',
  'ExchangeSocketClient',
  'sign_l1_action',
  'sign_user_signed_action',
  'stringify_decimals',
  'Wallet',
]
