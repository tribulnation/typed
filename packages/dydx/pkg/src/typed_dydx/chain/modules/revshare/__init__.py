from .market_mapper_rev_share_details import MarketMapperRevShareDetails
from .order_router_rev_share import OrderRouterRevShare

from typed_dydx.chain.core import GrpcEndpoint


class Revshare(
  MarketMapperRevShareDetails,
  OrderRouterRevShare,
  GrpcEndpoint,
):
  """Revshare endpoints."""
