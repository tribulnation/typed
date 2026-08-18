from dataclasses import dataclass
from .get import Get
from .list import List


@dataclass(frozen=True, kw_only=True)
class Positions(Get, List):
  """`positions` endpoints."""
