"""HTTP transport for the Binance-style REST surfaces: futures, spot, prediction and Aster
Chain REST.

Every parameter, signed or not, travels in the URL query string, for every HTTP verb.
Aster verifies a signature against the query string byte for byte, so the transport
builds that string once, signs it, and sends exactly it: no reordering or re-encoding
by `httpx` in between.
"""

from typing_extensions import Any, Mapping, TypeVar
from dataclasses import dataclass, field
from decimal import Decimal
from urllib.parse import urlencode
import json

import httpx

from typed_core.http import HttpClient
from typed_core.validation import validator

from ..auth import (
  MAINNET_CHAIN_ID,
  TESTNET_CHAIN_ID,
  Credentials,
  Wallet,
  parse_wallet,
  sign_action,
  sign_message,
  sign_withdraw,
)
from ..endpoint.rpc import Meta, RpcClient
from ..envelope import unwrap
from ..exc import AuthError, LogicError

T = TypeVar('T')

Params = list[tuple[str, Any]]

FORM_HEADERS = {'Content-Type': 'application/x-www-form-urlencoded'}


def wire_value(value: Any) -> Any:
  """One parameter value as Aster reads it: booleans `true`/`false`, decimals in plain
  notation, lists as compact JSON arrays."""
  if isinstance(value, bool):
    return 'true' if value else 'false'
  if isinstance(value, Decimal):
    return format(value, 'f')
  if isinstance(value, list | dict):
    return json.dumps(value, separators=(',', ':'))
  return value


def encode(params: Params) -> str:
  """The exact query string sent — and signed — for `params`, in order."""
  return urlencode([(key, wire_value(value)) for key, value in params])


@dataclass(kw_only=True)
class HttpRpcClient(RpcClient):
  """HTTP client for one Binance-style surface, owning its base URL, the shared
  credentials, signing and validation."""

  base_url: str
  """Surface root, e.g. `https://fapi.asterdex.com/fapi/v3`; paths are relative to it."""
  http: HttpClient = field(default_factory=HttpClient)
  credentials: Credentials | None = None
  """`None` means unauthenticated: only public endpoints can be called."""
  mainnet: bool = True
  """Selects the agent signature `chainId` (1666 mainnet, 714 testnet) and `asterChain`."""
  validate: bool = True

  async def __aenter__(self):
    await self.http.__aenter__()
    return self

  async def __aexit__(self, exc_type, exc_value, traceback):
    await self.http.__aexit__(exc_type, exc_value, traceback)

  def should_validate(self, validate: bool | None = None) -> bool:
    """Per-call override of the client-level `validate` default."""
    return self.validate if validate is None else validate

  @property
  def chain_id(self) -> int:
    """The `Message{msg}` signature `chainId` for this network."""
    return MAINNET_CHAIN_ID if self.mainnet else TESTNET_CHAIN_ID

  def url(self, path: str, query: str) -> str:
    """The full request URL for `path` and an already-encoded `query`."""
    url = f'{self.base_url}/{path}'
    return f'{url}?{query}' if query else url

  async def send(self, method: str, path: str, query: str) -> httpx.Response:
    """Send one request with every parameter in the query string."""
    headers = None if method == 'GET' else FORM_HEADERS
    return await self.http.request(method, self.url(path, query), headers=headers)

  def result(
    self,
    response: httpx.Response,
    validator: validator[T] | None = None,
    *,
    validate: bool | None = None,
  ) -> T:
    """Unwrap and map errors, then validate."""
    payload = unwrap(response)
    if validator is not None and self.should_validate(validate):
      return validator.python(payload)
    return payload

  async def request(
    self,
    method: str,
    path: str,
    *,
    params: Mapping[str, Any] | None = None,
    validator: validator[T] | None = None,
    validate: bool | None = None,
  ) -> T:
    """Send an unsigned request."""
    query = encode(list((params or {}).items()))
    response = await self.send(method, path, query)
    return self.result(response, validator, validate=validate)

  async def authed_request(
    self,
    method: str,
    path: str,
    *,
    meta: Meta,
    params: Mapping[str, Any] | None = None,
    child: Wallet | None = None,
    validator: validator[T] | None = None,
    validate: bool | None = None,
  ) -> T:
    """Sign and send one request, in the signing mode `meta` declares.

    Raises:
      AuthError: The wallet this mode needs was not given to the client.
    """
    query = self.sign(meta, list((params or {}).items()), child=child)
    response = await self.send(method, path, query)
    return self.result(response, validator, validate=validate)

  def sign(self, meta: Meta, params: Params, *, child: Wallet | None = None) -> str:
    """Append the authentication parameters for `meta`'s mode to `params`, sign, and
    return the final query string with `signature` last.

    Raises:
      AuthError: No credentials, or the wallet this mode needs is missing.
      ValueError: A co-signed call was made without the `child` wallet.
    """
    creds = self.credentials
    if creds is None:
      raise AuthError(
        'No credentials for this surface: the client was built with `public=True`, '
        'or, for Aster Chain (mainnet only), with `mainnet=False`.'
      )
    mode = meta.get('sign', 'agent')
    params, caller_nonce = pop_nonce(params)
    nonce = creds.nonces.next() if caller_nonce is None else caller_nonce

    if mode == 'typed':
      return self.sign_typed(creds, meta, params, nonce=nonce)

    if mode == 'main':
      return self.sign_main(creds, meta, params, nonce=nonce, child=child)

    if mode == 'withdraw':
      params = self.withdraw_params(creds, params, nonce=creds.nonces.next())

    agent = creds.require_agent()
    msg = encode(
      [*params, ('user', creds.user), ('signer', agent.address), ('nonce', nonce)]
    )
    signature = sign_message(agent, msg, chain_id=self.chain_id)
    return f'{msg}&{encode([("signature", signature)])}'

  def sign_typed(
    self, creds: Credentials, meta: Meta, params: Params, *, nonce: int
  ) -> str:
    """Sign a `typed`-mode call: the main wallet signs the action struct `meta['action']`
    over every sent parameter, domain `chainId` = the request's `signatureChainId`.

    Raises:
      AuthError: The client has no main wallet.
      LogicError: The endpoint declares no action `type`.
    """
    main = creds.require_main()
    primary_type = meta.get('action')
    if primary_type is None:
      raise LogicError('A `typed` endpoint must declare its `action` in `meta`.')
    signature_chain_id = pop_signature_chain_id(params)
    signed = [
      *params,
      ('asterChain', 'Mainnet' if self.mainnet else 'Testnet'),
      ('user', creds.user),
      ('nonce', nonce),
    ]
    signature = sign_action(
      main, signed, primary_type=primary_type, chain_id=signature_chain_id
    )
    tail = [('signatureChainId', signature_chain_id), ('signature', signature)]
    return encode([*signed, *tail])

  def sign_main(
    self,
    creds: Credentials,
    meta: Meta,
    params: Params,
    *,
    nonce: int,
    child: Wallet | None,
  ) -> str:
    """Sign a `main`-mode call: the main wallet signs `Message{msg}`.

    The message is assembled in `meta['order']` when declared: Aster documents a fixed
    field order for these calls, interleaving `nonce`/`user`/`signer` with business
    parameters. Parameters it does not list follow, in sending order. A `childSignature`
    in the order is the sub-account's own signature over the same message without it.

    Raises:
      AuthError: The client has no main wallet (or no agent, when `signer` is sent).
      ValueError: A co-signed call was made without the `child` wallet.
    """
    main = creds.require_main()
    order = meta.get('order', [])
    values: dict[str, Any] = {**dict(params), 'user': creds.user, 'nonce': nonce}
    if 'signer' in order:
      values['signer'] = creds.require_agent().address
    chain_id = signature_chain_id_of(params) or self.chain_id

    def ordered() -> Params:
      listed = [(key, values[key]) for key in order if key in values]
      return listed + [(k, v) for k, v in values.items() if k not in order]

    if 'childSignature' in order:
      if child is None:
        raise ValueError('This call must be co-signed: pass the `child` wallet.')
      child_msg = encode(ordered())
      values['childSignature'] = sign_message(
        parse_wallet(child), child_msg, chain_id=chain_id
      )
    msg = encode(ordered())
    signature = sign_message(main, msg, chain_id=chain_id)
    return f'{msg}&{encode([("signature", signature)])}'

  def withdraw_params(
    self, creds: Credentials, params: Params, *, nonce: int
  ) -> Params:
    """Add the main wallet's `userNonce`/`userSignature` over the EVM withdraw `Action`.

    Raises:
      AuthError: The client has no main wallet.
    """
    main = creds.require_main()
    values = dict(params)
    chain_id = int(values['chainId'])
    signature = sign_withdraw(
      main,
      chain_id=chain_id,
      signature_chain_id=int(values.get('signatureChainId', chain_id)),
      receiver=values['receiver'],
      asset=values['asset'],
      amount=str(wire_value(values['amount'])),
      fee=str(wire_value(values['fee'])),
      nonce=nonce,
      mainnet=self.mainnet,
    )
    return [*params, ('userNonce', nonce), ('userSignature', signature)]


def pop_nonce(params: Params) -> tuple[Params, int | None]:
  """Split a caller-chosen `nonce` off the business parameters.

  Only order placement, the guarded cancels and `noop` declare `nonce` as a parameter:
  a guarded cancel and `noop` must be sent with the nonce of the request they target,
  which the caller therefore has to choose when placing it. When present, the call is
  signed with it (in the usual position) instead of a freshly drawn one.
  """
  rest = [(key, value) for key, value in params if key != 'nonce']
  chosen = [value for key, value in params if key == 'nonce' and value is not None]
  return rest, (int(chosen[-1]) if chosen else None)


def signature_chain_id_of(params: Params) -> int | None:
  """The request's own `signatureChainId`, when it sends one: the EIP-712 domain
  `chainId` has to equal it."""
  for key, value in params:
    if key == 'signatureChainId':
      return int(value)
  return None


def pop_signature_chain_id(params: Params) -> int:
  """Remove `signatureChainId` from a management call's parameters and return it (`56`,
  EVM, when absent): it is sent after the signed struct, not inside it."""
  for i, (key, value) in enumerate(params):
    if key == 'signatureChainId':
      del params[i]
      return int(value)
  return 56
