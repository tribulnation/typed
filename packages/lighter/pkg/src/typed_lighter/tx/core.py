"""`TxCore`: the base every `client.tx` method inherits, and the one `request()` they call.

A `tx` method's request holds the transaction's own fields plus two controls the core
consumes, `api_key_index` and `nonce`; `meta['tx_type']` names the transaction type. The core
takes a key and nonce (from the nonce manager unless the caller pinned them), signs with the
matching signer function (`tx/signing.py`), and submits: `POST /api/v1/sendTx` (form:
`tx_type`, `tx_info` as a JSON string) over HTTP, or `jsonapi/sendtx` (`tx_info` as a JSON
object) over the shared WebSocket connection. No auth token is involved: the signature is the
authentication. A `200` only means the API server accepted the transaction; the sequencer can
still reject it later, which only shows up in the account's streams or transaction lookups.

A method whose `meta` also names a `submit` target (`lit_lease`, `fast_withdraw`) is a REST
endpoint of its own that takes a signed transaction directly: the core signs with that
target's adapter (`tx/signing.py` `DIRECT_SUBMITS`) and posts `tx_info` plus the target's
form fields to the method's own `path`, over HTTP only, with a derived auth token.

Transactions signed beforehand with `client.signer` go out through `tx.send` and
`tx.batch` (`submit`/`submit_batch`), which move the nonce cache past them once accepted,
as a pinned nonce does. `reserve_nonces` hands out consecutive nonces of one key from the
same nonce manager, for a batch the caller signs itself.

`client.tx` shares its transports with `client.api` and `client.streams`, and only the root
client (`core.client.ClientBase`) closes them: `async with client.tx:` opens and closes
nothing.
"""

from typing_extensions import (
  Any,
  AsyncIterator,
  Literal,
  NotRequired,
  Self,
  Sequence,
  TypedDict,
  TypeVar,
)
from contextlib import asynccontextmanager
from dataclasses import dataclass
from types import UnionType
import json

from typed_core.validation import validator

from ..api.account.keys.next_nonce import NextNonce
from ..core.exc import AuthError, BadRequest, LogicError
from ..core.transport.http import HttpRpcClient
from ..core.transport.ws import SocketClient
from ..core.signer.account import AccountSigner
from ..core.signer.txs.base import SignedTx
from .nonce import NonceManager
from .signing import (
  DIRECT_SUBMITS,
  TX_SIGNERS,
  DirectForm,
  Submit,
  TxSigner,
  TxType,
)

T = TypeVar('T')

Transport = Literal['http', 'ws']
"""Which connection carries a transaction."""

SEND_TX_PATH = '/api/v1/sendTx'
CHANGE_PUB_KEY = 8
"""`L2ChangePubKey`'s tx type: its slot may be one the client has no key for yet."""
SEND_TX_BATCH_PATH = '/api/v1/sendTxBatch'
MAX_BATCH_HTTP = 50
"""Most transactions one `sendTxBatch` takes (error `21514` above it)."""
MAX_BATCH_WS = 15
"""Most transactions one `jsonapi/sendtxbatch` message takes, per the docs."""


class TxMeta(TypedDict):
  """Per-endpoint quirks of a `tx` method."""

  tx_type: TxType
  """Lighter transaction type id (`14` create order, `15` cancel order, ...)."""
  submit: NotRequired[Submit]
  """A REST endpoint taking the signed transaction directly, at the method's own `path`,
  instead of `sendTx`/`jsonapi/sendtx`; names its signing adapter and form fields."""


@dataclass(frozen=True)
class NonceReservation:
  """Consecutive nonces of one API key, held for one batch."""

  api_key_index: int
  """Key to sign every transaction of the batch with."""
  nonces: range
  """The nonces to sign with, in order."""


@dataclass(frozen=True, kw_only=True)
class BatchKey:
  """What every transaction of one batch has to share, read back from its `tx_info`."""

  account_index: int
  """Account every transaction is signed for."""
  api_key_index: int
  """Key every transaction is signed with."""


def signed_position(signed: SignedTx) -> tuple[BatchKey, int]:
  """The account and key a signed transaction is for, and its nonce, read from its
  `tx_info`.

  Raises:
    BadRequest: `signed` is not a signed Lighter transaction.
  """
  try:
    info = signed.tx_info_object()
    account = info.get('AccountIndex', info.get('FromAccountIndex'))
    api_key_index = info['ApiKeyIndex']
    nonce = info['Nonce']
    if not isinstance(account, int):
      raise TypeError(account)
  except (ValueError, KeyError, TypeError, AttributeError):
    raise BadRequest(
      f'Not a signed Lighter transaction: {signed.tx_info[:80]!r}'
    ) from None
  return BatchKey(account_index=account, api_key_index=api_key_index), nonce


def check_batch(signed_txs: Sequence[SignedTx], *, limit: int) -> BatchKey:
  """Check a batch client-side, as the venue would: at most `limit` transactions, one
  account and API key (`21121`), strictly increasing nonces (`21105`).

  Raises:
    BadRequest: The batch breaks one of those rules, or an item is not a signed
      transaction.
  """
  if not signed_txs:
    raise BadRequest('A batch needs at least one transaction')
  if len(signed_txs) > limit:
    raise BadRequest(
      f'A batch takes at most {limit} transactions over this transport, got {len(signed_txs)}'
    )
  keys: set[BatchKey] = set()
  previous: int | None = None
  for signed in signed_txs:
    key, nonce = signed_position(signed)
    keys.add(key)
    if previous is not None and nonce <= previous:
      raise BadRequest(
        f'Batch nonces must strictly increase: {nonce} follows {previous}'
      )
    previous = nonce
  if len(keys) > 1:
    raise BadRequest('Every transaction of a batch must share one account and API key')
  return keys.pop()


@dataclass(kw_only=True, frozen=True)
class TxCore:
  """Base of `client.tx`: the signer, the nonce manager, and both submission transports."""

  account_signer: AccountSigner | None
  """Signer; `None` for a public or read-only client, where every tx method raises `AuthError`."""
  nonces: NonceManager | None
  """Nonce manager over the signer's keys; `None` without a signer."""
  http: HttpRpcClient
  """Main REST transport: `sendTx`, `sendTxBatch`, `nextNonce` and direct submits."""
  ws: SocketClient
  """The `/stream` WebSocket transport: `jsonapi/sendtx` and `jsonapi/sendtxbatch`."""
  validate: bool = True
  """Validate responses by default."""

  @classmethod
  def new(
    cls,
    client: HttpRpcClient,
    *,
    ws: SocketClient,
    account_signer: AccountSigner | None,
    validate: bool = True,
  ) -> Self:
    """Wire a signer and both transports, with a nonce manager over the signer's keys.

    Args:
      client: The main REST transport (`sendTx`, `nextNonce`, direct submits).
      ws: The `/stream` WebSocket transport (`jsonapi/sendtx`).
      account_signer: Signer; `None` for a public or read-only client.
      validate: Validate responses by default.
    """
    http = client
    signer = account_signer
    nonces = None
    if signer is not None:
      account_index = signer.account_index

      async def fetch(api_key_index: int) -> int:
        """Fetch the next nonce of one key (`GET /api/v1/nextNonce`), always validated."""
        response = await http.request(
          'GET',
          '/api/v1/nextNonce',
          params={'account_index': account_index, 'api_key_index': api_key_index},
          validator=validator(NextNonce),
          validate=True,
        )
        return response['nonce']

      nonces = NonceManager(signer.api_key_indices, fetch)
    return cls(
      account_signer=signer, nonces=nonces, http=http, ws=ws, validate=validate
    )

  async def __aenter__(self) -> Self:
    """Return this surface; both transports open lazily, on first use.

    Entering or leaving it with `async with` opens and closes nothing: the transports are
    shared with `client.api` and `client.streams`, and only the root client
    (`core.client.ClientBase`) closes them.
    """
    return self

  async def __aexit__(self, exc_type, exc_value, traceback):
    """Do nothing: only the root client closes the transports, which sibling surfaces may
    still be using."""

  @property
  def signer(self) -> AccountSigner:
    """The configured signer.

    Raises:
      AuthError: The client was built without API keys.
    """
    if self.account_signer is None:
      raise AuthError(
        'Transactions need API keys: build the client with `api_keys=...`.'
      )
    return self.account_signer

  @property
  def nonce_manager(self) -> NonceManager:
    """The nonce manager over the signer's keys.

    Raises:
      AuthError: The client was built without API keys.
    """
    if self.nonces is None:
      raise AuthError(
        'Transactions need API keys: build the client with `api_keys=...`.'
      )
    return self.nonces

  def should_validate(self, validate: bool | None) -> bool:
    """Per-call override of the client-level `validate` default."""
    return self.validate if validate is None else validate

  @asynccontextmanager
  async def reserve_nonces(
    self, count: int, *, api_key_index: int | None = None
  ) -> AsyncIterator[NonceReservation]:
    """Hold the next `count` nonces of one API key, to sign a batch with.

    Sign each transaction with `client.signer` using the reservation's key and nonces, and
    submit them with `tx.batch` inside the block. The key's lock is held until the block
    exits, so no other `client.tx` call on that key interleaves. The block's outcome settles
    every reserved nonce together, as for a single transaction: a clean exit consumes them
    all (so exit only after submitting). Only a `BadRequest`, `AuthError` or `RateLimited`
    carrying a Lighter business code other than `21104` leaves them unconsumed; anything
    else (`21104 invalid nonce`, an HTTP 5xx, a network error or cancellation, an error with
    no business code or an unclassified one, a local error) drops the cached nonce, to be
    refetched before the key's next transaction.

    Args:
      count: How many consecutive nonces to hold (one per transaction of the batch).
      api_key_index: Key to use; defaults to the next one in rotation.

    Raises:
      AuthError: The client was built without API keys, or `api_key_index` is not one
        of its keys.
      BadRequest: `count` is below 1.

    Examples:
      ```python
      async with client.tx.reserve_nonces(2) as reservation:
        signed = [
          client.signer.cancel_order(
            market_index=0,
            order_index=index,
            nonce=nonce,
            api_key_index=reservation.api_key_index,
          )
          for index, nonce in zip([101, 102], reservation.nonces)
        ]
        await client.tx.batch(signed)
      ```
    """
    if api_key_index is not None:
      self.signer.key_signer(api_key_index)
    async with self.nonce_manager.reserve(api_key_index, count=count) as (key, first):
      yield NonceReservation(api_key_index=key, nonces=range(first, first + count))

  @asynccontextmanager
  async def presigned(self, key: BatchKey, *, last_nonce: int) -> AsyncIterator[None]:
    """Track one submission of transactions signed beforehand, as a pinned nonce is.

    When they are signed for this client's own account, a clean exit (an accepted
    submission) moves `key`'s cached next nonce past `last_nonce`, never backwards; a
    refusal leaves the cache untouched; any other outcome drops it, to be refetched
    (`NonceManager.pinned`). Takes no lock, so it also works inside `reserve_nonces`.
    Transactions of another account leave every cache alone.

    Args:
      key: The account and key the transactions are signed for.
      last_nonce: The highest nonce among them.
    """
    own = self.account_signer is not None and (
      key.account_index == self.account_signer.account_index
    )
    if self.nonces is None or not own:
      yield
      return
    async with self.nonces.pinned(api_key_index=key.api_key_index, nonce=last_nonce):
      yield

  async def submit(
    self,
    signed: SignedTx,
    *,
    transport: Transport = 'http',
    path: str = SEND_TX_PATH,
    validator: validator[T] | None = None,
    validate: bool | None = None,
  ) -> T:
    """Submit one signed transaction to `sendTx` or `jsonapi/sendtx`; nonce bookkeeping is the
    caller's (`request`, `tx.send`).

    Args:
      signed: The signed transaction.
      transport: Submit over HTTP or over the WebSocket connection.
      path: HTTP path to submit to.
      validator: Response validator.
      validate: Per-call override of response validation.
    """
    should_validate = self.should_validate(validate)
    if transport == 'ws':
      return await self.ws.rpc(
        {
          'type': 'jsonapi/sendtx',
          'data': {'tx_type': signed.tx_type, 'tx_info': signed.tx_info_object()},
        },
        validator=validator,
        validate=should_validate,
      )
    return await self.http.request(
      'POST',
      path,
      form={'tx_type': signed.tx_type, 'tx_info': signed.tx_info},
      validator=validator,
      validate=should_validate,
    )

  async def submit_batch(
    self,
    signed_txs: Sequence[SignedTx],
    *,
    transport: Transport = 'http',
    validator: validator[T] | None = None,
    validate: bool | None = None,
  ) -> T:
    """Submit signed transactions in one `sendTxBatch` or `jsonapi/sendtxbatch`, after
    checking the batch client-side (`check_batch`); nonce bookkeeping is the caller's
    (`tx.batch`).

    Args:
      signed_txs: The signed transactions, in nonce order.
      transport: Submit over HTTP or over the WebSocket connection.
      validator: Response validator.
      validate: Per-call override of response validation.

    Raises:
      BadRequest: The batch is empty, too long for the transport, mixes accounts or API
        keys, or its nonces do not strictly increase.
    """
    check_batch(signed_txs, limit=MAX_BATCH_WS if transport == 'ws' else MAX_BATCH_HTTP)
    tx_types = json.dumps([signed.tx_type for signed in signed_txs])
    tx_infos = json.dumps([signed.tx_info for signed in signed_txs])
    should_validate = self.should_validate(validate)
    if transport == 'ws':
      return await self.ws.rpc(
        {
          'type': 'jsonapi/sendtxbatch',
          'data': {'tx_types': tx_types, 'tx_infos': tx_infos},
        },
        validator=validator,
        validate=should_validate,
      )
    return await self.http.request(
      'POST',
      SEND_TX_BATCH_PATH,
      form={'tx_types': tx_types, 'tx_infos': tx_infos},
      validator=validator,
      validate=should_validate,
    )

  async def submit_direct(
    self,
    signed: SignedTx,
    fields: DirectForm,
    *,
    path: str,
    validator: validator[T] | None = None,
    validate: bool | None = None,
  ) -> T:
    """Post a signed transaction to a REST endpoint that takes one directly (`litLease`,
    `fastwithdraw`): form `tx_info` plus `fields`, with a derived auth token.

    Args:
      signed: The signed transaction.
      fields: The endpoint's own form fields.
      path: The endpoint's path.
      validator: Response validator.
      validate: Per-call override of response validation.
    """
    return await self.http.request(
      'POST',
      path,
      form={'tx_info': signed.tx_info, **fields},
      auth='write',
      validator=validator,
      validate=self.should_validate(validate),
    )

  async def request(
    self,
    request: Any,
    *,
    method: Literal['POST'],
    path: str,
    meta: TxMeta,
    validate: bool | None = None,
    transport: Transport = 'http',
    request_type: type[Any] | UnionType | None = None,
    response_type: type[T] | UnionType | None = None,
  ) -> T:
    """Sign and submit one transaction: the one call every `client.tx` method makes.

    With an explicit `nonce` in the request, the caller owns ordering: no lock is taken
    and no nonce reserved, but once the transaction is accepted, a pinned nonce at or past
    the key's cached next nonce moves the cache to `nonce + 1`, so later managed calls do
    not reuse it; an outcome other than acceptance or a refusal drops the key's cache. Otherwise the manager picks the key (or uses the request's
    `api_key_index`) and its next nonce, holding that key's lock through submission.

    Args:
      request: The method's request: transaction fields plus `api_key_index`/`nonce`.
      method: Wire HTTP verb (always `POST`).
      path: HTTP path: `/api/v1/sendTx`, or a `submit` target's own path.
      meta: Which transaction type this is, and its `submit` target if any.
      validate: Per-call override of response validation.
      transport: Submit over HTTP or over the WebSocket connection.
      request_type: The method's request type (unused: the signer consumes the request).
      response_type: The method's response type, used to validate the reply.

    Raises:
      AuthError: The client was built without API keys, or `api_key_index` is not one of
        its keys (except for `change_api_key`, whose slot is the one being registered).
      LogicError: No signer function is registered for `meta`, a `submit` target was asked
        to go over WebSocket, or its adapter signed another transaction type.
    """
    submit = meta.get('submit')
    direct = None
    if submit is not None:
      direct = DIRECT_SUBMITS.get(submit)
      if direct is None:
        raise LogicError(f'No submit target registered for {submit!r}')
      if transport != 'http':
        raise LogicError(f'{submit} is only reachable over HTTP')
    sign: TxSigner | None = (
      direct if direct is not None else TX_SIGNERS.get(meta['tx_type'])
    )
    if sign is None:
      raise LogicError(f'No signer registered for tx type {meta["tx_type"]}')
    sign_request: TxSigner = sign
    signer = self.signer
    response_validator = validator(response_type) if response_type is not None else None  # type: ignore[type-var]

    async def sign_and_submit(*, api_key_index: int, nonce: int) -> Any:
      """Sign with one key and nonce, check the signed type, then submit."""
      signed = sign_request.sign(
        signer, request, api_key_index=api_key_index, nonce=nonce
      )
      if signed.tx_type != meta['tx_type']:
        raise LogicError(
          f'Signed tx type {signed.tx_type}, but the endpoint declares {meta["tx_type"]}'
        )
      if direct is not None:
        return await self.submit_direct(
          signed,
          direct.fields(request),
          path=path,
          validator=response_validator,
          validate=validate,
        )
      return await self.submit(
        signed,
        transport=transport,
        path=path,
        validator=response_validator,
        validate=validate,
      )

    api_key_index: int | None = request.get('api_key_index')
    nonce: int | None = request.get('nonce')
    if api_key_index is not None and meta['tx_type'] != CHANGE_PUB_KEY:
      # Fail before fetching a nonce; a ChangePubKey is signed by the key it registers,
      # so its slot needs no configured key.
      signer.key_signer(api_key_index)
    if nonce is not None:
      key = signer.key(api_key_index)
      async with self.nonce_manager.pinned(api_key_index=key, nonce=nonce):
        return await sign_and_submit(api_key_index=key, nonce=nonce)
    async with self.nonce_manager.reserve(api_key_index) as (key, next_nonce):
      return await sign_and_submit(api_key_index=key, nonce=next_nonce)
