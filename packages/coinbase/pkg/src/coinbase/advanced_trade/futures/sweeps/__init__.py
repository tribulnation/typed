from dataclasses import dataclass
from .cancel import Cancel
from .list import List
from .schedule import Schedule


@dataclass(frozen=True, kw_only=True)
class Sweeps(Cancel, List, Schedule):
  """`sweeps` endpoints."""
