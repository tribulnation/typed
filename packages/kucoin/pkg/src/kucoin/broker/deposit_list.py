"""`GET /api/v1/asset/ndbroker/deposit/list` — Get Deposit List."""

from typing_extensions import Literal
from typed_core.validation import TypedDict, validator
from kucoin.core import RpcEndpoint


class BrokerDeposit(TypedDict):
  """One deposit record."""

  uid: int
  """Depositing sub-account's UID."""
  hash: str
  """On-chain transaction hash, or an internal reference for `isInner` deposits."""
  address: str
  """Deposit address (or originating identifier for an internal deposit)."""
  memo: str
  """Address memo/tag; empty string if none."""
  amount: str
  """Deposit amount."""
  fee: str
  """Fee charged for the deposit."""
  currency: str
  """Currency deposited."""
  isInner: bool
  """Whether this was an internal (KuCoin-to-KuCoin) deposit rather than on-chain."""
  walletTxId: str
  """Wallet transaction id."""
  status: Literal['PROCESSING', 'SUCCESS', 'FAILURE']
  """Deposit status."""
  remark: str
  """Free-text remark; empty string if none."""
  chain: str
  """Chain id; empty string observed for an internal deposit."""
  createdAt: int
  """Record creation time, Unix milliseconds."""
  updatedAt: int
  """Record last-update time, Unix milliseconds."""


_Type = list[BrokerDeposit]
adapter = validator[_Type](_Type)  # type: ignore


class DepositList(RpcEndpoint):
  """`Get Deposit List` — mixed into `Broker`, the product exposing `broker.deposit_list`."""

  async def deposit_list(
    self,
    *,
    currency: str | None = None,
    status: Literal['PROCESSING', 'SUCCESS', 'FAILURE'] | None = None,
    hash: str | None = None,
    start_timestamp: int | None = None,
    end_timestamp: int | None = None,
    limit: int | None = None,
    validate: bool | None = None,
  ) -> list[BrokerDeposit]:
    """List deposit records across every sub-account of the authenticated Exchange (ND) Broker, most recent first, optionally filtered by currency, status, transaction hash and/or a time window.

    Args:
      currency: Filter to one currency. Omit for every currency.
      status: Filter by deposit status.
      hash: Filter to one on-chain transaction hash.
      start_timestamp: Range start, Unix milliseconds.
      end_timestamp: Range end, Unix milliseconds.
      limit: Maximum rows to return, most recent first.
      validate: Validate the response against the generated schema.

    References:
      - [KuCoin API docs](https://www.kucoin.com/docs-new)
    """
    params = {}
    if currency is not None:
      params['currency'] = currency
    if status is not None:
      params['status'] = status
    if hash is not None:
      params['hash'] = hash
    if start_timestamp is not None:
      params['startTimestamp'] = start_timestamp
    if end_timestamp is not None:
      params['endTimestamp'] = end_timestamp
    if limit is not None:
      params['limit'] = limit
    return await self.authed_request(
      'GET',
      '/api/v1/asset/ndbroker/deposit/list',
      params=params,
      validator=adapter,
      validate=validate,
    )
