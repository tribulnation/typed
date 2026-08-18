"""KuCoin Credit endpoints."""

from .get_loan_market import GetLoanMarket
from .get_loan_market_interest_rate import GetLoanMarketInterestRate
from .get_purchase_orders import GetPurchaseOrders
from .get_redeem_orders import GetRedeemOrders
from .modify_purchase import ModifyPurchase
from .purchase import Purchase
from .redeem import Redeem


class Credit(
  GetLoanMarket,
  GetLoanMarketInterestRate,
  GetPurchaseOrders,
  GetRedeemOrders,
  ModifyPurchase,
  Purchase,
  Redeem,
):
  """KuCoin Credit endpoints."""
