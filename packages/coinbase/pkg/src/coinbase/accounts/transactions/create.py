from dataclasses import dataclass
from typed_core.validation import validator
from typing_extensions import Literal, NotRequired, TypedDict
from coinbase.core.endpoint.rpc import RpcEndpoint


class TransactionAmountAmount(TypedDict):
  """Amount sent. Negative, since this is a debit."""

  amount: str
  """Signed amount, as a decimal string."""
  currency: str
  """Currency code of `amount`."""


class TransactionAmountNativeAmount(TypedDict):
  """Amount sent, in the user's native currency. Negative, since this is a debit."""

  amount: str
  """Signed amount, as a decimal string."""
  currency: str
  """Currency code of `amount`."""


class TransactionAmountTransactionFee(TypedDict):
  """Network fee charged for this send."""

  amount: str
  """Fee amount, as a decimal string."""
  currency: str
  """Currency code of `amount`."""


class TransactionCounterparty(TypedDict):
  """The send's destination."""

  resource: NotRequired[str]
  """Resource type of the destination, e.g. `bitcoin_address`, `ethereum_address`, `email`. Not documented as an exhaustive enumeration."""
  address: NotRequired[str]
  """Blockchain address, when the destination is an onchain address."""
  email: NotRequired[str]
  """Email address, when the destination was addressed by email."""


class TravelRuleBeneficiaryAddress(TypedDict):
  """The beneficiary's physical address."""

  address1: NotRequired[str]
  """Address line 1."""
  address2: NotRequired[str]
  """Address line 2."""
  address3: NotRequired[str]
  """Address line 3."""
  city: NotRequired[str]
  """City."""
  state: NotRequired[str]
  """State or province."""
  country: NotRequired[str]
  """Country, ISO 3166-1 alpha-2."""
  postal_code: NotRequired[str]
  """Postal code."""


class TransactionNetwork(TypedDict):
  """Info about the crypto network this send is moving on."""

  status: NotRequired[Literal['off_blockchain', 'confirmed', 'pending', 'unconfirmed']]
  """Network confirmation status."""
  hash: NotRequired[str]
  """Onchain transaction hash, once broadcast."""
  transaction_fee: NotRequired[TransactionAmountTransactionFee]
  network_name: NotRequired[str]
  """Blockchain network name."""


class TravelRuleData(TypedDict):
  """Travel Rule compliance information for the beneficiary. Required in some jurisdictions depending on wallet type and amount; not required in the US at time of writing."""

  beneficiary_wallet_type: NotRequired[
    Literal['WALLET_TYPE_SELF_HOSTED', 'WALLET_TYPE_EXCHANGE']
  ]
  """Whether the beneficiary wallet is self-hosted or held at another exchange."""
  is_self: NotRequired[Literal['IS_SELF_TRUE', 'IS_SELF_FALSE']]
  """Whether the beneficiary is the sender themself."""
  beneficiary_name: NotRequired[str]
  """The beneficiary's name."""
  beneficiary_address: NotRequired[TravelRuleBeneficiaryAddress]
  beneficiary_financial_institution: NotRequired[str]
  """UUID of the beneficiary's financial institution. Required when `beneficiary_wallet_type` is `WALLET_TYPE_EXCHANGE`."""
  transfer_purpose: NotRequired[str]
  """Free-text reason for the transfer, e.g. "Rent"."""


class CreateSendTransactionRequest(TypedDict):
  """Send funds for any Coinbase-supported asset to a blockchain address or an email address."""

  type: Literal['send']
  """Transaction type. `send` is the only type this endpoint's docs page documents as creatable."""
  to: str
  """A blockchain address, or the email address of the recipient. Phone number sends are documented as temporarily disabled."""
  amount: str
  """Amount to send, as a decimal string."""
  currency: str
  """Currency code of `amount`."""
  description: NotRequired[str]
  """Notes included in the recipient's notification."""
  skip_notifications: NotRequired[bool]
  """Suppress email/push notifications for this send."""
  idem: NotRequired[str]
  """A UUIDv4 token to ensure idempotence. Recommended."""
  destination_tag: NotRequired[str]
  """For select currencies, the beneficiary/destination tag or memo."""
  network: NotRequired[str]
  """Blockchain network to send on. Defaults to the currency's standard network when omitted."""
  travel_rule_data: NotRequired[TravelRuleData]


class TransactionV2(TypedDict):
  """The newly created send transaction."""

  id: str
  """Transaction id."""
  type: Literal['send']
  """Transaction type — always `send` for a transaction created by this endpoint."""
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
  """User-defined description, echoing the request's `description`, or null."""
  created_at: str
  """Creation time, ISO 8601."""
  updated_at: NotRequired[str]
  """Last update time, ISO 8601. Present in the docs' worked create-send example."""
  resource: Literal['transaction']
  """Resource type tag."""
  resource_path: str
  """The transaction's own API path."""
  network: NotRequired[TransactionNetwork]
  to: NotRequired[TransactionCounterparty]
  cancelable: NotRequired[bool]
  """Whether this send can still be canceled."""
  idem: NotRequired[str]
  """Echo of the request's `idem`, when supplied."""


class CreateTransactionResponse(TypedDict):
  """The whole v2 wire frame — not unwrapped by the core."""

  data: TransactionV2


@dataclass(frozen=True, kw_only=True)
class Create(RpcEndpoint):
  """`POST /v2/accounts/{account_id}/transactions`."""

  async def create(
    self,
    account_id: str,
    create_send_transaction_request: CreateSendTransactionRequest,
  ) -> CreateTransactionResponse:
    """Send funds from an account to a blockchain address or the email address of the recipient. This is the only documented `type` this endpoint accepts (`send`) — the docs page enumerates no other creatable transaction type, though `type` can hold other values (`request`, `transfer`, `buy`, ...) on transactions returned by `accounts.transactions.list`/`accounts.transactions.get`. Requires the `wallet:transactions:send` scope, and (for some jurisdictions/amounts) 2FA.

    Args:
      account_id: The account to send from.
      create_send_transaction_request: The send to create.

    References:
      - [Official docs](https://docs.cdp.coinbase.com/coinbase-app/transfer-apis/send-crypto)
    """
    return await self.authed_request(
      'POST',
      f'/v2/accounts/{account_id}/transactions',
      json=create_send_transaction_request,
      validator=validator(CreateTransactionResponse),
    )
