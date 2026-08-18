"""KuCoin TradeFee endpoints."""

from .actual_fee import ActualFeeEndpoint
from .actual_fee_futures import ActualFeeFutures
from .basic_fee import BasicFeeEndpoint


class TradeFee(ActualFeeEndpoint, ActualFeeFutures, BasicFeeEndpoint):
  """KuCoin TradeFee endpoints."""
