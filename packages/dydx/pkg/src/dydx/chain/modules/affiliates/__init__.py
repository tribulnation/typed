from .affiliate_info import AffiliateInfo
from .referred_by import ReferredBy

from dydx.chain.core import GrpcEndpoint


class Affiliates(
  AffiliateInfo,
  ReferredBy,
  GrpcEndpoint,
):
  """Affiliates endpoints."""
