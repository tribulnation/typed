# `core/base.py` (`ClientBase`/`AlchemyTransport`), `core/rest.py` (`RestEndpoint` and its
# three resolved subclasses), and `core/rpc.py` (`ChainRpc`) are this client's real,
# hand-written core (codegen-mechanization migration, design §4/§5/§5a). Generated code
# imports a resolved `core` class directly from its own submodule -- `codegen/config.toml`'s
# `[python.cores]` `base` is always a real `module.path:ClassName`, never routed through
# this flat namespace. Only two things are re-exported here: the shared `typed_core.
# exceptions`, since every public entry point (`typed_alchemy/__init__.py`) still reaches
# them through `typed_alchemy.core`, and `core/types.py`'s timestamp aliases
# (`TimestampSeconds`/`TimestampMillis`/`TimestampIso`), since the CLI always resolves a
# declared timestamp `format` (`docs/spec/authoring.md` rule 3) against this flat
# `<pkg>.core` namespace (`generator.core_package`), not a client-chosen submodule.
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
from .types import TimestampSeconds, TimestampMillis, TimestampIso

__all__ = [
  'Error',
  'NetworkError',
  'ValidationError',
  'ApiError',
  'BadRequest',
  'AuthError',
  'RateLimited',
  'LogicError',
  'TimestampSeconds',
  'TimestampMillis',
  'TimestampIso',
]
