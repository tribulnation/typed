from .get_deposits import GetDeposits
from .set_clearance_originator import SetClearanceOriginator


class Deposits(
  GetDeposits,
  SetClearanceOriginator,
):
  """Deposits endpoints."""
