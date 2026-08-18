"""KuCoin Transfer endpoints."""

from .flex_transfer import FlexTransfer
from .quotas import Quotas


class Transfer(FlexTransfer, Quotas):
  """KuCoin Transfer endpoints."""
