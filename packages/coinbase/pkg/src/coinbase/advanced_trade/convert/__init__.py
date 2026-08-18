from dataclasses import dataclass
from .commit import Commit
from .get import Get
from .quote import Quote


@dataclass(frozen=True, kw_only=True)
class Convert(Commit, Get, Quote):
  """`convert` endpoints."""
