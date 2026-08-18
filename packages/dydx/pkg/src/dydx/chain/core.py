"""Shared dYdX Chain gRPC primitives."""

from collections.abc import Awaitable, Callable
from dataclasses import dataclass
from functools import cached_property, wraps
from types import TracebackType

from grpclib.client import Channel
from grpclib.const import Status
from grpclib.exceptions import GRPCError, ProtocolError, StreamTerminatedError
from typed_core.exceptions import NetworkError
from typing_extensions import ParamSpec, Self, TypeVar

# gRPC statuses that represent transport failures rather than API/business errors.
_NETWORK_STATUSES = frozenset({Status.UNAVAILABLE})

P = ParamSpec('P')
T = TypeVar('T')

def wrap_exceptions(fn: Callable[P, Awaitable[T]]) -> Callable[P, Awaitable[T]]:
  """Map grpclib transport failures from a gRPC call to typed_core NetworkError.

  Transport-level failures (GOAWAY, HTTP/2 protocol errors, terminated streams, and
  gRPC unavailable/502 responses) are raised as NetworkError. Business/API errors,
  which arrive either in a successful response payload or as a non-transport GRPCError,
  are left untouched.
  """
  @wraps(fn)
  async def wrapper(*args: P.args, **kwargs: P.kwargs) -> T:
    """Await the wrapped gRPC call, normalizing transport exceptions."""
    try:
      return await fn(*args, **kwargs)
    except (ProtocolError, StreamTerminatedError, ConnectionError, TimeoutError) as exc:
      raise NetworkError(str(exc)) from exc
    except GRPCError as exc:
      if exc.status in _NETWORK_STATUSES:
        raise NetworkError(str(exc)) from exc
      raise
  return wrapper

@dataclass(kw_only=True, frozen=True)
class GrpcClient:
  """Async gRPC transport that owns a lazily opened channel."""

  host: str = 'oegs.dydx.trade'
  port: int = 443
  ssl: bool = True

  @cached_property
  def channel(self) -> Channel:
    """Return the gRPC channel, creating it on first use.

    `cached_property` writes straight into `instance.__dict__`, bypassing
    `__setattr__`, so this works on a frozen dataclass -- see `client-core`'s
    `endpoint/rpc.py` reference for the same idiom applied to composed children.
    """
    return Channel(self.host, self.port, ssl=self.ssl)

  async def __aenter__(self) -> Self:
    """Open the channel for an async client context."""
    self.channel
    return self

  async def __aexit__(
    self,
    exc_type: type[BaseException] | None,
    exc: BaseException | None,
    traceback: TracebackType | None,
  ):
    """Close the channel for an async client context."""
    self.close()

  def close(self):
    """Close the open channel, if one was created.

    Mutates `self.__dict__` directly (the same trick `cached_property` itself uses)
    rather than reassigning a field -- there is no stored `_channel` field anymore,
    only the `cached_property`'s own cache slot.
    """
    if 'channel' in self.__dict__:
      self.__dict__['channel'].close()
      del self.__dict__['channel']

@dataclass(kw_only=True, frozen=True)
class GrpcEndpoint:
  """Base for every generated/hand-written gRPC module -- talks only to `client`."""

  client: GrpcClient

  @property
  def channel(self) -> Channel:
    """Return the active shared gRPC channel."""
    return self.client.channel
