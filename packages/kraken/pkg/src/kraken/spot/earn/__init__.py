"""`earn` endpoints."""

from .allocate import Allocate
from .allocate_status import AllocateStatus
from .allocations import Allocations
from .deallocate import Deallocate
from .deallocate_status import DeallocateStatus
from .strategies import Strategies


class Earn(
  Allocate, AllocateStatus, Allocations, Deallocate, DeallocateStatus, Strategies
):
  """`earn` endpoints."""
