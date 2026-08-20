# The legacy core (`core/mixin.py`'s `Endpoint`/`PortfolioEndpoint`/`PricesEndpoint`/
# `NftEndpoint`/`RpcEndpoint`/`Router`, `core/util/paging.py`'s `PaginatedResponse`,
# `core/validation.py`'s `validator`/`Timestamp`) has been fully retired: every
# endpoint under `api/**` is now generated on the new `core/endpoint`/`core/transport`/
# `core/auth.py`/`core/envelope.py`/`core/types.py` structure `spec/core.md` proposed,
# and those legacy modules are deleted along with it (see `spec/core.md`'s Migration
# Plan). New code imports the new core's pieces directly from their own submodules
# (`.core.endpoint.rpc`, `.core.transport.http`, `.core.auth`, `.core.envelope`,
# `.core.types`) rather than through this flat namespace -- only the shared
# `typed_core.exceptions` re-export stays here, since every public entry point
# (`typed_alchemy/__init__.py`) still reaches it through `typed_alchemy.core`.
#
# `lazy_loader.attach_stub` only accepts single-dot relative imports in this file (it
# raises `ValueError` at import time otherwise).
from .exc import (
  Error,
  NetworkError,
  ValidationError,
  ApiError,
  BadRequest,
  AuthError,
  RateLimited,
  LogicError,
)

__all__ = [
  'Error',
  'NetworkError',
  'ValidationError',
  'ApiError',
  'BadRequest',
  'AuthError',
  'RateLimited',
  'LogicError',
]
