"""Shared gRPC transport primitives -- promoted from dYdX's chain/core.py (design doc §9,
2026-08-31 codegen mechanization)."""

from collections.abc import Awaitable, Callable
from dataclasses import dataclass, field
from functools import wraps
from types import TracebackType

from grpclib.client import Channel
from grpclib.const import Status
from grpclib.exceptions import GRPCError, ProtocolError, StreamTerminatedError
from typing_extensions import ParamSpec, Self, TypeVar

from .exceptions import NetworkError

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

@dataclass(kw_only=True)
class GrpcClient:
  """Async gRPC transport that owns a lazily opened channel.

  Not frozen, unlike `GrpcEndpoint` below -- it needs a real mutable `_channel` slot
  to cache into, the same shape `HttpClient._client` already uses for the identical
  lazy-open/close contract on the HTTP side. `GrpcEndpoint`'s own freeze is a separate
  concern (matching every other `Endpoint` composition base) and doesn't require the
  `Client` object it merely holds a reference to to be frozen too.
  """

  host: str
  port: int = 443
  ssl: bool = True
  _channel: Channel | None = field(default=None, init=False, repr=False)

  @property
  def channel(self) -> Channel:
    """Return the gRPC channel, creating it on first use."""
    if self._channel is None:
      self._channel = Channel(self.host, self.port, ssl=self.ssl)
    return self._channel

  async def __aenter__(self) -> Self:
    """Take ownership without connecting -- the channel opens lazily on first use,
    matching `HttpClient.__aenter__`'s own contract."""
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
    """Close the open channel, if one was created."""
    if self._channel is not None:
      self._channel.close()
      self._channel = None

@dataclass(kw_only=True, frozen=True)
class GrpcEndpoint:
  """Base for every generated/hand-written gRPC module -- talks only to `client`."""

  client: GrpcClient

  @property
  def channel(self) -> Channel:
    """Return the active shared gRPC channel."""
    return self.client.channel
