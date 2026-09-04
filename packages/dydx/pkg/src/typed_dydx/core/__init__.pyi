from datetime import datetime
from typing_extensions import Annotated

from typed_core.exceptions import (
  ApiError,
  AuthError,
  BadRequest,
  Error,
  LogicError,
  NetworkError,
  RateLimited,
  ValidationError,
)
from typed_core.times import IsoConverter

timestamp_iso: IsoConverter
TimestampIso = Annotated[datetime, ...]

__all__ = [
  'ApiError',
  'AuthError',
  'BadRequest',
  'Error',
  'LogicError',
  'NetworkError',
  'RateLimited',
  'ValidationError',
  'TimestampIso',
  'timestamp_iso',
]
