"""Moralis client core: transport, auth, and shared types -- re-exported here so a
generated leaf module (`from typed_moralis.core.rest import RestEndpoint`) and
`main.py` (`from typed_moralis.core.base import ClientBase`) never have to reach past
their own resolved module.
"""

from typed_core.exceptions import (
  ApiError as ApiError,
  AuthError as AuthError,
  BadRequest as BadRequest,
  Error as Error,
  LogicError as LogicError,
  NetworkError as NetworkError,
  RateLimited as RateLimited,
  ValidationError as ValidationError,
)
from .auth import env_api_key as env_api_key
from .base import ClientBase as ClientBase, MoralisTransport as MoralisTransport
from .rest import RestEndpoint as RestEndpoint
from .types import (
  Chain as Chain,
  DateIso as DateIso,
  Direction as Direction,
  Order as Order,
  TimestampIso as TimestampIso,
  TimestampMillis as TimestampMillis,
  TimestampSeconds as TimestampSeconds,
  date_iso as date_iso,
  timestamp_iso as timestamp_iso,
  timestamp_millis as timestamp_millis,
  timestamp_seconds as timestamp_seconds,
)
