from .delegator_delegations import DelegatorDelegations
from .delegator_unbonding_delegations import DelegatorUnbondingDelegations
from .pool import Pool
from .validators import Validators

from typed_dydx.chain.core import GrpcEndpoint


class Staking(
  DelegatorDelegations,
  DelegatorUnbondingDelegations,
  Pool,
  Validators,
  GrpcEndpoint,
):
  """Staking endpoints."""
