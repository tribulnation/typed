from dataclasses import dataclass
from typed_core.validation import validator
from typing_extensions import AsyncIterator, Literal, NotRequired, TypedDict
from coinbase.core.endpoint.rpc import RpcEndpoint


class MoneyAmount(TypedDict):
  """Transaction amount. Negative for a debit (e.g. `sell`, `advanced_trade_fill`)."""

  amount: str
  """Amount, as a decimal string."""
  currency: str
  """Currency code of `amount`."""


class MoneyNativeAmount(TypedDict):
  """Transaction amount in the user's native currency. Negative for a debit."""

  amount: str
  """Amount, as a decimal string."""
  currency: str
  """Currency code of `amount`."""


class MoneyTransactionFee(TypedDict):
  """Network fee paid. Only present for `send` transactions."""

  amount: str
  """Fee amount, as a decimal string."""
  currency: str
  """Currency code of `amount`."""


class TransactionAdvancedTradeFill(TypedDict):
  """Advanced Trade fill info. Only present when `type` is `advanced_trade_fill`."""

  fill_price: str
  """Price this fill was posted at."""
  product_id: str
  """The Advanced Trade product id this fill belongs to."""
  order_id: str
  """The id of the order this fill belongs to."""
  commission: str
  """Commission charged for this fill, in the quote currency."""
  order_side: Literal['BUY', 'SELL']
  """Side the order was placed on."""


class TransactionDetails(TypedDict):
  """Human-readable transaction summary. Upstream prose (`Details` table) names these fields `title`/`subsidebar_label`/`header`/`health`, but every worked example on the docs page shows only `title`/`subtitle` — spec'd from the examples, see `upstream.md`."""

  title: str
  """Short description with currency, e.g. "Bought bitcoin"."""
  subtitle: NotRequired[str]
  """Supplementary detail, e.g. the payment method or counterparty used."""


class TransactionToAccount(TypedDict):
  """The transaction sent to another one of the user's own accounts (a `transfer`)."""

  id: str
  """The destination account's id."""
  resource: Literal['account']
  """Resource type tag."""
  resource_path: str
  """The destination account's own API path."""


class TransactionToBitcoinAddress(TypedDict):
  """The transaction sent to an onchain bitcoin address."""

  resource: Literal['bitcoin_address']
  """Resource type tag."""
  address: str
  """The destination bitcoin address."""


class TransactionToEmail(TypedDict):
  """The transaction sent to an email address (not yet a Coinbase account)."""

  resource: Literal['email']
  """Resource type tag."""
  email: str
  """The destination email address."""


class TransactionToEthereumAddress(TypedDict):
  """The transaction sent to an onchain ethereum address."""

  resource: Literal['ethereum_address']
  """Resource type tag."""
  address: str
  """The destination ethereum address."""


class TransactionToGenericAddress(TypedDict):
  """The transaction sent to an onchain address, chain unspecified. Verified live: real send transactions use this generic shape (resource `address`) rather than a chain-specific `bitcoin_address`/`ethereum_address` tag."""

  resource: Literal['address']
  """Resource type tag."""
  address: str
  """The destination address."""


class TransactionToUser(TypedDict):
  """The transaction sent to another Coinbase user."""

  id: str
  """The destination user's id."""
  resource: Literal['user']
  """Resource type tag."""
  resource_path: str
  """The destination user's own API path."""


class TransactionsPagination(TypedDict):
  """Cursor pagination state for this page."""

  ending_before: str | None
  """Echo of the request's `ending_before`, or null."""
  starting_after: str | None
  """Echo of the request's `starting_after`, or null."""
  limit: int
  """Page size used for this response."""
  order: Literal['asc', 'desc']
  """Sort order used for this response."""
  previous_uri: str | None
  """Relative URI for the previous page, or null when there isn't one."""
  next_uri: str | None
  """Relative URI for the next page, or null when there isn't one."""
  next_starting_after: NotRequired[str | None]
  """Cursor value to pass as `starting_after` to fetch the next page; null on the last page. `clients/coinbase/spec/core.md` records this field name as live-verified for `GET /v2/accounts`; the generic v2 pagination doc page's own example omits it — kept here on the live-verified core's authority, same as `accounts.list`'s sibling spec."""


class TransactionNetwork(TypedDict):
  """Crypto network info, e.g. onchain transaction status. Only present for certain transaction types."""

  status: Literal['off_blockchain', 'confirmed', 'pending', 'unconfirmed']
  """Onchain confirmation status."""
  status_description: NotRequired[str | None]
  """Human-readable status description."""
  hash: NotRequired[str]
  """Onchain transaction hash. Only present for `send` transactions."""
  transaction_fee: NotRequired[MoneyTransactionFee]
  network_name: NotRequired[str]
  """Network name, e.g. `arbitrum`. Verified live: the wire key is `network_name`, not `name` as an earlier pass assumed from upstream docs prose."""


class Transaction(TypedDict):
  """An event on the account. `amount` is positive (credit) or negative (debit)."""

  id: str
  """Transaction id."""
  type: Literal[
    'advanced_trade_fill',
    'buy',
    'clawback',
    'derivatives_settlement',
    'earn_payout',
    'fiat_deposit',
    'fiat_withdrawal',
    'incentives_rewards_payout',
    'incentives_shared_clawback',
    'intx_deposit',
    'intx_withdrawal',
    'receive',
    'request',
    'retail_simple_dust',
    'sell',
    'send',
    'staking_transfer',
    'subscription_rebate',
    'subscription',
    'trade',
    'transfer',
    'tx',
    'unstaking_transfer',
    'unsupported_asset_recovery',
    'unwrap_asset',
    'vault_withdrawal',
    'wrap_asset',
    'fcm_futures_usdc_sell',
    'fcm_futures_usdc_sell_additional_encumberment_rollup',
  ]
  """Transaction type. `tx` is the default, uncategorized type; new types may be added over time."""
  status: Literal[
    'canceled',
    'completed',
    'expired',
    'failed',
    'pending',
    'waiting_for_clearing',
    'waiting_for_signature',
  ]
  """Transaction status. Statuses vary by transaction type; use `details` (when present) for a human-readable description rather than branching on this alone."""
  amount: MoneyAmount
  native_amount: MoneyNativeAmount
  description: NotRequired[str | None]
  """User-defined description."""
  created_at: str
  """Transaction creation time, ISO 8601."""
  updated_at: NotRequired[str]
  """Last transaction update time, ISO 8601. Present in every response body seen while authoring this spec; upstream docs prose flags it as removed for List/Show as of an unspecified past date, but the documented example response still includes it — kept here on the example's authority (see `upstream.md`)."""
  resource: Literal['transaction']
  """Resource type tag."""
  resource_path: str
  """The transaction's own API path."""
  network: NotRequired[TransactionNetwork]
  to: NotRequired[
    TransactionToBitcoinAddress
    | TransactionToEthereumAddress
    | TransactionToAccount
    | TransactionToUser
    | TransactionToEmail
    | TransactionToGenericAddress
  ]
  """Receiving party of a debit transaction. Only present for certain transaction types."""
  details: NotRequired[TransactionDetails]
  advanced_trade_fill: NotRequired[TransactionAdvancedTradeFill]
  cancelable: NotRequired[bool]
  """Whether this transaction can still be canceled. Only present for `send` transactions."""
  idem: NotRequired[str]
  """The idempotency key the transaction was created with. Only present for `send` transactions."""


class TransactionsPage(TypedDict):
  """The whole v2 response frame — not unwrapped by the client core, since `pagination`'s cursor fields live outside `data`."""

  data: list[Transaction]
  """The transaction list for this page."""
  pagination: TransactionsPagination


@dataclass(frozen=True, kw_only=True)
class List(RpcEndpoint):
  """`GET /v2/accounts/{account_id}/transactions`."""

  async def list(
    self,
    account_id: str,
    *,
    limit: int | None = None,
    starting_after: str | None = None,
    ending_before: str | None = None,
    order: Literal['asc', 'desc'] | None = None,
  ) -> TransactionsPage:
    """List an account's transactions, newest first. Requires the `wallet:transactions:read` scope.

    Args:
      account_id: The account's id.
      limit: Page size, 0-100. Defaults to 25.
      starting_after: Cursor from a previous page's `pagination.next_starting_after`; fetches the page after this transaction id.
      ending_before: Cursor from a previous page's response; fetches the page before this transaction id.
      order: Sort order.

    References:
      - [Official docs](https://docs.cdp.coinbase.com/coinbase-app/track-apis/transactions)
    """
    params = {}
    if limit is not None:
      params['limit'] = limit
    if starting_after is not None:
      params['starting_after'] = starting_after
    if ending_before is not None:
      params['ending_before'] = ending_before
    if order is not None:
      params['order'] = order
    return await self.authed_request(
      'GET',
      f'/v2/accounts/{account_id}/transactions',
      params=params,
      validator=validator(TransactionsPage),
    )

  async def list_paged(
    self,
    account_id: str,
    *,
    limit: int | None = None,
    ending_before: str | None = None,
    order: Literal['asc', 'desc'] | None = None,
    max_pages: int | None = None,
  ) -> AsyncIterator[TransactionsPage]:
    """Yield successive pages of `list`.

    Passes each page's token back as `starting_after` and stops when a response carries
    no `pagination.next_starting_after`, or after `max_pages` pages when one is given.
    """
    starting_after: str | None = None
    pages = 0
    while True:
      response = await self.list(
        account_id,
        limit=limit,
        ending_before=ending_before,
        order=order,
        starting_after=starting_after,
      )
      yield response
      pages += 1
      if max_pages is not None and pages >= max_pages:
        break
      starting_after_0 = response.get('pagination') if response is not None else None
      starting_after = (
        starting_after_0.get('next_starting_after')
        if starting_after_0 is not None
        else None
      )
      if not starting_after:
        break
