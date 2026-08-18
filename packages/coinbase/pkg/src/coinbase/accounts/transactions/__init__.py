from dataclasses import dataclass
from .create import Create
from .get import Get
from .list import List


@dataclass(frozen=True, kw_only=True)
class Transactions(Create, Get, List):
  """`transactions` endpoints."""
