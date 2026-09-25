"""How `TxCore` turns a `client.tx` method's request into a signed transaction, per `tx_type`.

Each `client.tx` transaction method sends its request (the transaction's own fields, plus
the `api_key_index`/`nonce` controls the core consumes) with `meta={'tx_type': <id>}`. The
function registered here for that id calls the matching `AccountSigner` sign twin, whose
arguments are exactly the request's fields (the twins take the same shapes as `client.tx`,
nested unions included), so every request is forwarded unchanged.

A method whose `meta` also names a `submit` target (`lit_lease`, `fast_withdraw`) is not a
`sendTx` transaction but a REST endpoint taking a signed `tx_info` beside its own form
fields. `DIRECT_SUBMITS` holds, per target, how its request is signed (its own adapter, not
`TX_SIGNERS`: both sign a transfer with fixed asset and routes) and which extra form fields
go beside `tx_info`.

Signers are objects with a `sign` method rather than bare callables, so the key and nonce
(both integers) are keyword-only.
"""

from typing_extensions import TYPE_CHECKING, Any, Literal, Mapping, Protocol, TypedDict
from dataclasses import dataclass

from ..core.exc import AuthError, BadRequest
from ..core.signer.account import AccountSigner
from ..core.signer.txs.base import SignedTx

if TYPE_CHECKING:
  # The request modules import `tx.core`, which imports this one.
  from . import fast_withdraw, lit_lease


class TxSigner(Protocol):
  """Signs one request of a `tx` method for a given API key and nonce."""

  def sign(
    self, signer: AccountSigner, request: Any, *, api_key_index: int, nonce: int
  ) -> SignedTx:
    """Sign `request` with `signer`.

    Args:
      signer: The account's signer.
      request: The method's request: transaction fields plus the core's controls.
      api_key_index: Slot to sign with.
      nonce: Nonce of that slot.
    """
    ...


Twin = Literal[
  'create_order',
  'create_grouped_orders',
  'cancel_all_orders',
  'approve_integrator',
  'change_api_key',
  'create_sub_account',
  'create_public_pool',
  'update_public_pool',
  'transfer',
  'withdraw',
  'cancel_order',
  'modify_order',
  'mint_shares',
  'burn_shares',
  'update_leverage',
  'update_margin',
  'stake',
  'unstake',
  'update_account_config',
  'update_account_asset_config',
]
"""`AccountSigner` twins: each takes exactly its request's fields as arguments."""

CONTROLS = ('api_key_index', 'nonce')
"""Request keys the core consumes itself."""


@dataclass(frozen=True)
class Forward:
  """Signs a request by passing its fields straight to one `AccountSigner` twin."""

  twin: Twin
  """The twin to call."""

  def sign(
    self,
    signer: AccountSigner,
    request: Mapping[str, Any],
    *,
    api_key_index: int,
    nonce: int,
  ) -> SignedTx:
    """Sign `request` with the twin, leaving the core's controls out of its fields.

    Args:
      signer: The account's signer.
      request: The method's request.
      api_key_index: Slot to sign with.
      nonce: Nonce of that slot.
    """
    fields = {k: v for k, v in request.items() if k not in CONTROLS}
    method = getattr(signer, self.twin)
    return method(**fields, nonce=nonce, api_key_index=api_key_index)


TxType = Literal[
  8, 9, 10, 11, 12, 13, 14, 15, 16, 17, 18, 19, 20, 28, 29, 35, 36, 41, 42, 45
]
"""Every user transaction type id: `8` change API key, `14` create order, `15` cancel order, ..."""

TX_SIGNERS: dict[TxType, TxSigner] = {
  8: Forward('change_api_key'),
  9: Forward('create_sub_account'),
  10: Forward('create_public_pool'),
  11: Forward('update_public_pool'),
  12: Forward('transfer'),
  13: Forward('withdraw'),
  14: Forward('create_order'),
  15: Forward('cancel_order'),
  16: Forward('cancel_all_orders'),
  17: Forward('modify_order'),
  18: Forward('mint_shares'),
  19: Forward('burn_shares'),
  20: Forward('update_leverage'),
  28: Forward('create_grouped_orders'),
  29: Forward('update_margin'),
  35: Forward('stake'),
  36: Forward('unstake'),
  41: Forward('update_account_config'),
  42: Forward('update_account_asset_config'),
  45: Forward('approve_integrator'),
}
"""Signer per Lighter `tx_type`: every user transaction type."""


LIT_ASSET_INDEX = 2
"""Asset id of LIT, the asset a lease fee is paid in."""
USDC_ASSET_INDEX = 3
"""Asset id of USDC, the only asset the fast-withdrawal pool pays out."""

Submit = Literal['lit_lease', 'fast_withdraw']
"""REST endpoints that take a signed transaction directly instead of through `sendTx`."""


class LitLeaseForm(TypedDict):
  """`litLease`'s lease terms, posted beside the signed fee transfer."""

  lease_amount: str
  """LIT to lease, in raw units, as a decimal string."""
  duration_days: int
  """Lease duration in days."""


class FastWithdrawForm(TypedDict):
  """`fastwithdraw`'s destination, posted beside the signed transfer."""

  to_address: str
  """Destination L1 address."""


DirectForm = LitLeaseForm | FastWithdrawForm
"""The form fields a direct-submit target posts beside `tx_info`."""


class DirectSubmit(TxSigner, Protocol):
  """How one `meta['submit']` target signs its request and fills its form."""

  def fields(self, request: Any) -> DirectForm:
    """The form fields posted beside `tx_info`.

    Args:
      request: The method's request.
    """
    ...


@dataclass(frozen=True)
class LitLeaseSubmit:
  """`tx.lit_lease`: the fee as an L1-signed LIT transfer, posted with the lease terms."""

  def sign(
    self,
    signer: AccountSigner,
    request: 'lit_lease.Request',
    *,
    api_key_index: int,
    nonce: int,
  ) -> SignedTx:
    """Sign `tx.lit_lease`'s fee: a spot-to-spot LIT transfer (`L2Transfer`, tx type 12) to
    the incentives account, L1-signed.

    Args:
      signer: The account's signer.
      request: The `lit_lease` request.
      api_key_index: Slot to sign with.
      nonce: Nonce of that slot.

    Raises:
      AuthError: The client has no `eth_private_key`: the incentives account never shares
        this account's master, so the venue rejects the fee transfer without the L1
        signature (`21504 fail to l1 signature`, verified live).
    """
    if signer.eth_private_key is None:
      raise AuthError(
        'A LIT lease needs an L1 signature: build the client with `eth_private_key`.'
      )
    return signer.transfer(
      to_account_index=request['to_account_index'],
      amount=request['fee_amount'],
      asset_index=LIT_ASSET_INDEX,
      from_route='spot',
      to_route='spot',
      usdc_fee=request.get('usdc_fee', 0),
      nonce=nonce,
      api_key_index=api_key_index,
    )

  def fields(self, request: 'lit_lease.Request') -> LitLeaseForm:
    """`litLease`'s lease terms, posted beside the signed fee transfer.

    Args:
      request: The `lit_lease` request.
    """
    return LitLeaseForm(
      lease_amount=str(request['lease_amount']),
      duration_days=request['duration_days'],
    )


def fast_withdraw_memo(to_address: str) -> str:
  """The transfer memo naming a fast withdrawal's L1 destination: the 20 address bytes,
  then 12 zero bytes, as hex.

  Raises:
    BadRequest: `to_address` is not a 20-byte hex address.
  """
  address = to_address.lower().removeprefix('0x')
  if len(address) != 40 or any(c not in '0123456789abcdef' for c in address):
    raise BadRequest(f'to_address is not a 20-byte L1 address: {to_address!r}')
  return address + '00' * 12


@dataclass(frozen=True)
class FastWithdrawSubmit:
  """`tx.fast_withdraw`: an L1-signed USDC transfer to the pool, posted with its address."""

  def sign(
    self,
    signer: AccountSigner,
    request: 'fast_withdraw.Request',
    *,
    api_key_index: int,
    nonce: int,
  ) -> SignedTx:
    """Sign `tx.fast_withdraw`: a perps-to-perps USDC transfer (`L2Transfer`, tx type 12) to
    the fast-withdrawal pool, its memo naming the L1 destination, L1-signed.

    Args:
      signer: The account's signer.
      request: The `fast_withdraw` request.
      api_key_index: Slot to sign with.
      nonce: Nonce of that slot.

    Raises:
      AuthError: The client has no `eth_private_key`: a transfer to the pool, which never
        shares this account's master, needs the L1 signature.
      BadRequest: `to_address` is not a 20-byte hex address.
    """
    if signer.eth_private_key is None:
      raise AuthError(
        'A fast withdrawal needs an L1 signature: build the client with `eth_private_key`.'
      )
    return signer.transfer(
      to_account_index=request['to_account_index'],
      amount=request['amount'],
      asset_index=USDC_ASSET_INDEX,
      from_route='perps',
      to_route='perps',
      usdc_fee=request.get('usdc_fee', 0),
      memo=fast_withdraw_memo(request['to_address']),
      nonce=nonce,
      api_key_index=api_key_index,
    )

  def fields(self, request: 'fast_withdraw.Request') -> FastWithdrawForm:
    """`fastwithdraw`'s destination address, posted beside the signed transfer.

    Args:
      request: The `fast_withdraw` request.
    """
    return FastWithdrawForm(to_address=request['to_address'])


DIRECT_SUBMITS: dict[Submit, DirectSubmit] = {
  'lit_lease': LitLeaseSubmit(),
  'fast_withdraw': FastWithdrawSubmit(),
}
"""Signing and form fields per `meta['submit']` target."""
