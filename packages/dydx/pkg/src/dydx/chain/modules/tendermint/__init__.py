from .get_block_by_height import GetBlockByHeight
from .get_latest_block import GetLatestBlock
from .get_latest_validator_set import GetLatestValidatorSet
from .get_node_info import GetNodeInfo
from .get_validator_set_by_height import GetValidatorSetByHeight

from dydx.chain.core import GrpcEndpoint


class Tendermint(
  GetBlockByHeight,
  GetLatestBlock,
  GetLatestValidatorSet,
  GetNodeInfo,
  GetValidatorSetByHeight,
  GrpcEndpoint,
):
  """Tendermint endpoints."""
