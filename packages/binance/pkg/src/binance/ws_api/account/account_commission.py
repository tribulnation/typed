from typing_extensions import TypedDict
from typed_core.validation import validator
from binance.core.endpoint.ws_rpc import WsRpcEndpoint


class CommissionDiscount(TypedDict):
  """Discount on standard commissions when paying in BNB."""

  enabledForAccount: bool
  """Whether the BNB commission discount is enabled for this account."""
  enabledForSymbol: bool
  """Whether the BNB commission discount is enabled for this symbol."""
  discountAsset: str
  """Asset the discount is paid in."""
  discount: str
  """Rate by which standard commission is reduced when paying in `discountAsset`, as a decimal string."""


class SpecialCommission(TypedDict):
  """Special commission rates from the order."""

  maker: str
  """Maker commission rate, as a decimal string."""
  taker: str
  """Taker commission rate, as a decimal string."""
  buyer: str
  """Buyer commission rate, as a decimal string."""
  seller: str
  """Seller commission rate, as a decimal string."""


class StandardCommission(TypedDict):
  """Standard commission rates on trades from the order."""

  maker: str
  """Maker commission rate, as a decimal string."""
  taker: str
  """Taker commission rate, as a decimal string."""
  buyer: str
  """Buyer commission rate, as a decimal string."""
  seller: str
  """Seller commission rate, as a decimal string."""


class TaxCommission(TypedDict):
  """Tax commission rates on trades from the order."""

  maker: str
  """Maker commission rate, as a decimal string."""
  taker: str
  """Taker commission rate, as a decimal string."""
  buyer: str
  """Buyer commission rate, as a decimal string."""
  seller: str
  """Seller commission rate, as a decimal string."""


class CommissionRates(TypedDict):
  """This account's commission rates for a symbol."""

  symbol: str
  """Symbol these commission rates apply to."""
  standardCommission: StandardCommission
  specialCommission: SpecialCommission
  taxCommission: TaxCommission
  discount: CommissionDiscount


class AccountCommission(WsRpcEndpoint):
  """Query commission rates"""

  async def account_commission(
    self,
    *,
    symbol: str,
    validate: bool | None = None,
  ) -> CommissionRates:
    """Get current account commission rates for a symbol.

    Args:
      symbol: Symbol to query.

    References:
      - [Official docs](https://github.com/binance/binance-spot-api-docs/blob/master/web-socket-api.md#account-commission-rates-user_data)
    """
    params: dict = {
      'symbol': symbol,
    }
    _Response = CommissionRates
    _validator = validator[_Response](_Response)
    return await self.authed_request(
      'account.commission', params=params, validator=_validator, validate=validate
    )
