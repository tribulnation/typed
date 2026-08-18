"""`POST /api/v2/broker/withdrawal` — Apply for Fast Withdrawal."""

from typing_extensions import Literal, NotRequired
from typed_core.validation import TypedDict, validator
from kucoin.core import RpcEndpoint


class FastWithdrawalChallenge(TypedDict):
  """Risk-validation challenge returned by the initial request of a two-step withdrawal."""

  transactionId: str
  """Id identifying this withdrawal attempt across its validation round-trip; echoed back in the second request's `validation.transactionId`."""
  allFactors: list[list[str]]
  """Every risk-factor group this withdrawal could be challenged with."""
  sentFactors: list[list[str]]
  """The risk-factor group actually sent to the end user for this attempt; answer these in the resubmitted `validation.factors`."""


class FastWithdrawalResult(TypedDict):
  """Confirmed withdrawal, returned once validation succeeds (or immediately, for a withdrawal that needed no 2FA)."""

  withdrawalId: str
  """New withdrawal id."""


class FastWithdrawalValidationFactor(TypedDict):
  """One answered risk-validation factor."""

  factorType: str
  """Factor type, for example `EMV` (email verification) or `GAV` (Google Authenticator verification). KuCoin's docs give no closed set for this field."""
  factorValue: str
  """The end user's answer for this factor, for example an OTP code."""


class FastWithdrawalValidation(TypedDict):
  """Risk-validation factors, present only on the second (resubmission) request of a two-step withdrawal."""

  factors: NotRequired[list[FastWithdrawalValidationFactor]]
  """Risk factors resubmitted from the initial response's `sentFactors`, answered by the end user."""
  transactionId: NotRequired[str]
  """The `transactionId` returned by this withdrawal's initial request."""


class FastWithdrawalApplyRequest(TypedDict):
  currency: str
  """Currency to withdraw, for example `USDT`."""
  amount: float
  """Withdrawal amount."""
  address: str
  """Destination address, when `withdrawType` is `ADDRESS`."""
  remark: str
  """Caller-supplied note for this withdrawal. KuCoin's docs give no further description; an empty string is accepted (shown in the docs' own example)."""
  memo: str
  """Destination memo/tag, for chains that require one. KuCoin's docs give no further description; an empty string is accepted (shown in the docs' own example) for chains that don't need one, despite this field being documented `required`."""
  chain: NotRequired[str]
  """Chain id for the currency's network, for example `kcc`."""
  wallet: NotRequired[str]
  """Source wallet identifier, for example `kucoin`. KuCoin's docs give no further description."""
  isInner: NotRequired[bool]
  """Whether this is an internal (KuCoin-to-KuCoin) transfer rather than an on-chain withdrawal."""
  country: NotRequired[str]
  """Receiver's country. KuCoin's docs give no further description."""
  firstName: NotRequired[str]
  """Receiver's first name, for travel-rule compliance."""
  lastName: NotRequired[str]
  """Receiver's last name, for travel-rule compliance."""
  companyName: NotRequired[str]
  """Receiver's company name, when `receiverType` is `COMPANY`."""
  identityType: NotRequired[str]
  """Receiver identity document type. KuCoin's docs give no further description or closed set."""
  identityNo: NotRequired[str]
  """Receiver identity document number."""
  receiverType: NotRequired[Literal['COMPANY', 'INDIVIDUAL']]
  """Whether the receiver is a company or an individual, for travel-rule compliance."""
  withdrawType: NotRequired[Literal['ADDRESS', 'MAIL', 'PHONE', 'UID']]
  """Destination type for this withdrawal."""
  feeDeductType: NotRequired[Literal['EXTERNAL', 'INTERNAL']]
  """Whether the network fee is deducted from the withdrawal amount or charged separately."""
  questionnaire: NotRequired[str]
  """Freeform compliance questionnaire response. KuCoin's docs give no further description."""
  reasonOfTransfer: NotRequired[str]
  """Caller-supplied reason for the transfer, for compliance."""
  tin: NotRequired[str]
  """Receiver's tax identification number. KuCoin's docs give no further description."""
  validation: NotRequired[FastWithdrawalValidation]


_Type = FastWithdrawalChallenge | FastWithdrawalResult
adapter = validator[_Type](_Type)  # type: ignore


class ApplyFastWithdrawal(RpcEndpoint):
  """`Apply for Fast Withdrawal` — mixed into `Broker`, the product exposing `broker.apply_fast_withdrawal`."""

  async def apply_fast_withdrawal(
    self,
    fast_withdrawal_apply_request: FastWithdrawalApplyRequest,
    *,
    validate: bool | None = None,
  ) -> FastWithdrawalChallenge | FastWithdrawalResult:
    """Submit a Broker Pro Fast API withdrawal request to an external address or internal account, on behalf of an end user onboarded through the Fast API OAuth flow. A withdrawal that requires 2FA is a two-step exchange: the initial request returns a `transactionId` and the risk factors still needed; a second request resubmits the same body plus `validation` carrying those factors, and only then returns the final `withdrawalId`.

    Args:
      fast_withdrawal_apply_request: Withdrawal destination, amount and currency, plus optional Fast API risk-validation and receiver-identity fields.
      validate: Validate the response against the generated schema.

    References:
      - [KuCoin API docs](https://www.kucoin.com/docs-new)
    """
    return await self.authed_request(
      'POST',
      '/api/v2/broker/withdrawal',
      json=fast_withdrawal_apply_request,
      validator=adapter,
      validate=validate,
    )
