from dataclasses import dataclass
from .create import Create
from .get import Get
from .list import List
from .transactions import Transactions


@dataclass(frozen=True, kw_only=True)
class Addresses(Create, Get, List, Transactions):
  """`addresses` endpoints."""
