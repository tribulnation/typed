"""Typed async client for the Moralis API."""

from typed_core import (
  ApiError as ApiError,
  AuthError as AuthError,
  BadRequest as BadRequest,
  Error as Error,
  LogicError as LogicError,
  NetworkError as NetworkError,
  RateLimited as RateLimited,
  ValidationError as ValidationError,
)

from .main import Moralis as Moralis
