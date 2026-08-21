from .spot import Spot
from .futures import Futures
from .core.exc import ApiError, AuthError, BadRequest, Error, LogicError, NetworkError, RateLimited, ValidationError
from .main import MEXC
from . import spot, futures, core

__all__ = [
  'ApiError',
  'AuthError',
  'BadRequest',
  'Error',
  'Futures',
  'LogicError',
  'MEXC',
  'NetworkError',
  'RateLimited',
  'Spot',
  'ValidationError',
  'core',
  'futures',
  'spot',
]
