from dataclasses import dataclass
from .crypto import Crypto
from .list import List


@dataclass(frozen=True, kw_only=True)
class Currencies(Crypto, List):
  """`currencies` endpoints."""
