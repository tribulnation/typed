from .main import MarginTrade
from .core import (
  Error,
  NetworkError,
  ValidationError,
  ApiError,
  BadRequest,
  AuthError,
  RateLimited,
  LogicError,
  Wallet,
)
from .core.auth import AgentConsent, agent_consent

__all__ = [
  'MarginTrade',
  'Error',
  'NetworkError',
  'ValidationError',
  'ApiError',
  'BadRequest',
  'AuthError',
  'RateLimited',
  'LogicError',
  'Wallet',
  'AgentConsent',
  'agent_consent',
]
