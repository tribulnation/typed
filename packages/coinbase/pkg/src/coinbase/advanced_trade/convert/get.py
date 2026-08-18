from dataclasses import dataclass
from typed_core.validation import validator
from typing_extensions import Any, Literal, NotRequired, TypedDict
from coinbase.core.endpoint.rpc import RpcEndpoint


class AmountExchangeRate(TypedDict):
  """The exchange rate applied to this trade."""

  value: str
  """Amount, as a decimal string."""
  currency: str
  """Currency code."""


class AmountItemAmount(TypedDict):
  """The fee amount."""

  value: str
  """Amount, as a decimal string."""
  currency: str
  """Currency code."""


class AmountSubtotal(TypedDict):
  """Subtotal before fees."""

  value: str
  """Amount, as a decimal string."""
  currency: str
  """Currency code."""


class AmountTotal(TypedDict):
  """Total after fees."""

  value: str
  """Amount, as a decimal string."""
  currency: str
  """Currency code."""


class AmountTotalFeeAmount(TypedDict):
  """The total fee amount."""

  value: str
  """Amount, as a decimal string."""
  currency: str
  """Currency code."""


class AmountTradeAmount(TypedDict):
  """The conversion amount."""

  value: str
  """Amount, as a decimal string."""
  currency: str
  """Currency code."""


class ConvertAmount(TypedDict):
  """The amount as entered by the caller."""

  value: str
  """Amount, as a decimal string."""
  currency: str
  """Currency code."""
  cbrn: NotRequired[str]
  """CBRN identifier, when applicable."""


class ConvertPaymentMethodSource(TypedDict):
  """The source payment method. A large, mostly-conditional type gated by `type`; only the fields confirmed across doc pages are specced (see `convert.quote`'s `notes`)."""

  type: NotRequired[str]
  """Payment method kind, e.g. `COINBASE_ACCOUNT`."""
  network: NotRequired[str]
  """Network the payment method operates on, when applicable."""
  payment_method_id: NotRequired[str]
  """Id of the payment method."""


class ConvertPaymentMethodTarget(TypedDict):
  """The target payment method. A large, mostly-conditional type gated by `type`; only the fields confirmed across doc pages are specced (see `convert.quote`'s `notes`)."""

  type: NotRequired[str]
  """Payment method kind, e.g. `COINBASE_ACCOUNT`."""
  network: NotRequired[str]
  """Network the payment method operates on, when applicable."""
  payment_method_id: NotRequired[str]
  """Id of the payment method."""


class ConvertUnitPrice(TypedDict):
  """Unit-price information for this trade. Field-level breakdown undocumented (see `convert.quote`'s `notes`)."""

  target_to_fiat: NotRequired[dict[str, Any]]
  """Target currency price expressed in fiat, e.g. for a BTC-ETH trade, $3K / ETH. Field-level breakdown undocumented."""
  target_to_source: NotRequired[dict[str, Any]]
  """Target currency price expressed in the source currency, e.g. for a BTC-ETH trade, 25 ETH / BTC. Only set for crypto-to-crypto trades. Field-level breakdown undocumented."""
  source_to_fiat: NotRequired[dict[str, Any]]
  """Source currency price expressed in fiat, e.g. for a BTC-ETH trade, $6K / BTC. Only set for crypto-to-crypto trades. Field-level breakdown undocumented."""


class ConvertUserWarning(TypedDict):
  """One warning surfaced to the user."""

  id: NotRequired[str]
  """Warning id."""
  code: NotRequired[str]
  """Warning code."""
  message: NotRequired[str]
  """Human-readable warning message."""


class ConvertFee(TypedDict):
  """One fee line item."""

  title: NotRequired[str]
  """Display title of this fee."""
  description: NotRequired[str]
  """Human-readable description of this fee."""
  amount: NotRequired[AmountItemAmount]
  label: NotRequired[str]
  """Short display label for this fee."""


class ConvertTotalFee(TypedDict):
  """The total fee across all line items."""

  title: NotRequired[str]
  """Display title of the total fee."""
  amount: NotRequired[AmountTotalFeeAmount]


class ConvertTrade(TypedDict):
  """The convert trade."""

  id: str
  """The trade id."""
  status: Literal[
    'TRADE_STATUS_UNSPECIFIED',
    'TRADE_STATUS_CREATED',
    'TRADE_STATUS_STARTED',
    'TRADE_STATUS_COMPLETED',
    'TRADE_STATUS_CANCELED',
  ]
  """The trade's lifecycle state."""
  user_entered_amount: NotRequired[ConvertAmount]
  amount: NotRequired[AmountTradeAmount]
  subtotal: NotRequired[AmountSubtotal]
  total: NotRequired[AmountTotal]
  fees: NotRequired[list[ConvertFee]]
  """Fees charged on this trade."""
  total_fee: NotRequired[ConvertTotalFee]
  source: NotRequired[ConvertPaymentMethodSource]
  target: NotRequired[ConvertPaymentMethodTarget]
  unit_price: NotRequired[ConvertUnitPrice]
  user_warnings: NotRequired[list[ConvertUserWarning]]
  """Warnings applicable to this trade."""
  user_reference: NotRequired[str]
  """User-facing reference identifier for this trade."""
  source_currency: NotRequired[str]
  """Currency of the source account."""
  target_currency: NotRequired[str]
  """Currency of the target account."""
  source_id: NotRequired[str]
  """Id of the source account/payment method."""
  target_id: NotRequired[str]
  """Id of the target account/payment method."""
  exchange_rate: NotRequired[AmountExchangeRate]


class GetConvertTradeResponse(TypedDict):
  trade: NotRequired[ConvertTrade]


@dataclass(frozen=True, kw_only=True)
class Get(RpcEndpoint):
  """`GET /api/v3/brokerage/convert/trade/{trade_id}`."""

  async def get(
    self,
    trade_id: str,
    *,
    from_account: str,
    to_account: str,
  ) -> GetConvertTradeResponse:
    """Get a previously created or committed convert trade by id.

    Args:
      trade_id: The id of the trade to fetch.
      from_account: Currency of the account the trade converts from, e.g. `USD`.
      to_account: Currency of the account the trade converts to, e.g. `USDC`.

    References:
      - [Official docs](https://docs.cdp.coinbase.com/api-reference/advanced-trade-api/rest-api/convert/get-convert-trade)
    """
    params: dict = {
      'from_account': from_account,
      'to_account': to_account,
    }
    return await self.authed_request(
      'GET',
      f'/api/v3/brokerage/convert/trade/{trade_id}',
      params=params,
      validator=validator(GetConvertTradeResponse),
    )
