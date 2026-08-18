from dataclasses import dataclass
from typed_core.validation import validator
from typing_extensions import Any, Literal, NotRequired, TypedDict
from coinbase.core.endpoint.rpc import RpcEndpoint


class TransactionAdvancedTradeFill(TypedDict):
  """Advanced Trade fill info. Only present when `type` is `advanced_trade_fill`."""

  fill_price: NotRequired[str]
  """Price this fill was posted at."""
  product_id: NotRequired[str]
  """The Advanced Trade product id this fill belongs to."""
  order_id: NotRequired[str]
  """The id of the order this fill belongs to."""
  commission: NotRequired[str]
  """Commission charged for this fill, in the quote currency."""
  order_side: NotRequired[Literal['BUY', 'SELL']]
  """Side the order was placed on."""


class TransactionAmountAmount(TypedDict):
  """Amount of the transacted asset. Negative for debits (e.g. `advanced_trade_fill`, `sell`, `pro_deposit`)."""

  amount: str
  """Signed amount, as a decimal string."""
  currency: str
  """Currency code of `amount`."""


class TransactionAmountNativeAmount(TypedDict):
  """Amount in the user's native currency. Negative for debits (e.g. `advanced_trade_fill`, `sell`, `pro_deposit`)."""

  amount: str
  """Signed amount, as a decimal string."""
  currency: str
  """Currency code of `amount`."""


class TransactionAmountTransactionFee(TypedDict):
  """Network fee charged for this transaction."""

  amount: str
  """Fee amount, as a decimal string."""
  currency: str
  """Currency code of `amount`."""


class TransactionCounterpartyFrom(TypedDict):
  """Originating party of a credit transaction."""

  id: NotRequired[str]
  """Resource id of the counterparty, when it is an internal resource (e.g. an account)."""
  resource: NotRequired[str]
  """Resource type of the counterparty, e.g. `account`, `bitcoin_address`, `email`. Not documented as an exhaustive enumeration."""
  resource_path: NotRequired[str]
  """API path to the counterparty resource, when it is an internal resource."""
  address: NotRequired[str]
  """Blockchain address, when the counterparty is an onchain address."""
  email: NotRequired[str]
  """Email address, when the counterparty was addressed by email."""


class TransactionCounterpartyTo(TypedDict):
  """Receiving party of a debit transaction."""

  id: NotRequired[str]
  """Resource id of the counterparty, when it is an internal resource (e.g. an account)."""
  resource: NotRequired[str]
  """Resource type of the counterparty, e.g. `account`, `bitcoin_address`, `email`. Not documented as an exhaustive enumeration."""
  resource_path: NotRequired[str]
  """API path to the counterparty resource, when it is an internal resource."""
  address: NotRequired[str]
  """Blockchain address, when the counterparty is an onchain address."""
  email: NotRequired[str]
  """Email address, when the counterparty was addressed by email."""


class TransactionNetwork(TypedDict):
  """Info about the crypto network this transaction moved on, including any onchain transaction hash."""

  status: NotRequired[Literal['off_blockchain', 'confirmed', 'pending', 'unconfirmed']]
  """Network confirmation status."""
  hash: NotRequired[str]
  """Onchain transaction hash."""
  transaction_fee: NotRequired[TransactionAmountTransactionFee]
  network_name: NotRequired[str]
  """Blockchain network name."""


TransactionV2Keywords = TypedDict(
  'TransactionV2Keywords', {'from': NotRequired[TransactionCounterpartyFrom]}
)


class TransactionV2(TransactionV2Keywords):
  """A Coinbase App v2 account transaction (send, receive, buy, sell, transfer, and other transaction-log entries)."""

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
    'subscription',
    'subscription_rebate',
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
  """Transaction type."""
  status: Literal[
    'canceled',
    'completed',
    'expired',
    'failed',
    'pending',
    'waiting_for_clearing',
    'waiting_for_signature',
  ]
  """Transaction status."""
  amount: TransactionAmountAmount
  native_amount: TransactionAmountNativeAmount
  description: NotRequired[str | None]
  """User-defined description."""
  created_at: str
  """Creation time, ISO 8601."""
  updated_at: NotRequired[str]
  """Last update time, ISO 8601. Docs note this field was removed from list/show responses on 2025-02-07; kept optional since presence has varied by capture."""
  resource: Literal['transaction']
  """Resource type tag."""
  resource_path: str
  """The transaction's own API path."""
  instant_exchange: NotRequired[bool]
  """Docs note this field was removed from list/show responses on 2025-02-07; kept optional since presence has varied by capture."""
  advanced_trade_fill: NotRequired[TransactionAdvancedTradeFill]
  details: NotRequired[dict[str, Any]]
  """Detailed information about the transaction. Docs note this field was removed from list/show responses on 2025-02-07; kept optional since presence has varied by capture. Field-level shape is not enumerated in the fetched docs."""
  network: NotRequired[TransactionNetwork]
  to: NotRequired[TransactionCounterpartyTo]
  cancelable: NotRequired[bool]
  """Whether this transaction is allowed to be canceled."""
  idem: NotRequired[str]
  """Idempotency key the transaction was created with, when the caller supplied one."""
  buy: NotRequired[dict[str, Any]]
  """Related buy details. Only provided when `type` is `buy`. Field-level shape is not enumerated in the fetched docs beyond this."""
  sell: NotRequired[dict[str, Any]]
  """Related sell details. Only provided when `type` is `sell`. Field-level shape is not enumerated in the fetched docs beyond this."""
  trade: NotRequired[dict[str, Any]]
  """Related trade details. Only provided when `type` is `trade`. Field-level shape is not enumerated in the fetched docs beyond this."""


class ShowTransactionResponse(TypedDict):
  """The whole v2 wire frame — not unwrapped by the core."""

  data: TransactionV2


@dataclass(frozen=True, kw_only=True)
class Get(RpcEndpoint):
  """`GET /v2/accounts/{account_id}/transactions/{transaction_id}`."""

  async def get(self, account_id: str, transaction_id: str) -> ShowTransactionResponse:
    """Get a single transaction by id. Requires the `wallet:transactions:read` scope.

    Args:
      account_id: The account the transaction belongs to.
      transaction_id: The transaction to fetch.

    References:
      - [Official docs](https://docs.cdp.coinbase.com/coinbase-app/track-apis/transactions)
    """
    return await self.authed_request(
      'GET',
      f'/v2/accounts/{account_id}/transactions/{transaction_id}',
      validator=validator(ShowTransactionResponse),
    )
