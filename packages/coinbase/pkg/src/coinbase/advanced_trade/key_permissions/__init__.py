from dataclasses import dataclass
from .get import Get


@dataclass(frozen=True, kw_only=True)
class KeyPermissions(Get):
  """`key_permissions` endpoints."""
