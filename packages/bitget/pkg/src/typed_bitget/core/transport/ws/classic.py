"""Classic v2 WebSocket transport: `{"channel", "instId"}` subscription args, uppercase
`instType` (the value is supplied by the caller, e.g. `"SPOT"` — this transport doesn't
case-convert anything, see `spec/core.md` WebSocket).
"""

from typing_extensions import Any, ClassVar, Mapping
from dataclasses import dataclass
from datetime import timedelta

from .common import BaseSocketConnection, BaseSocketStreamClient
from ...auth import Credentials

CLASSIC_WS_PUBLIC_URL = 'wss://ws.bitget.com/v2/ws/public'
CLASSIC_WS_PRIVATE_URL = 'wss://ws.bitget.com/v2/ws/private'


@dataclass
class ClassicSocketConnection(BaseSocketConnection):
  url: str = CLASSIC_WS_PUBLIC_URL

  def build_arg(self, channel: str, params: Mapping[str, Any]) -> dict[str, Any]:
    return {'channel': channel, **params}

  def channel_of(self, arg: Mapping[str, Any]) -> str:
    return arg.get('channel', '')


@dataclass(kw_only=True)
class ClassicSocketStreamClient(BaseSocketStreamClient):
  """`public_conn`/`private_conn` hold `ClassicSocketConnection` instances at runtime —
  typed as the base `BaseSocketConnection` (inherited, not redeclared) since a mutable
  dataclass field can't be narrowed in a subclass without breaking pyright's invariance check.
  """

  symbol_key: ClassVar[str] = 'instId'

  @classmethod
  def new(
    cls,
    *,
    public_url: str = CLASSIC_WS_PUBLIC_URL,
    private_url: str = CLASSIC_WS_PRIVATE_URL,
    credentials: Credentials | None = None,
    validate: bool = True,
    timeout: timedelta = timedelta(seconds=10),
    ping_interval: timedelta = timedelta(seconds=30),
  ):
    """Build both connections. Thin: no environment lookup, no region resolution — the
    root's `.new()` owns that, see `main.py`.
    """
    return cls(
      public_conn=ClassicSocketConnection(
        url=public_url, timeout=timeout, ping_interval=ping_interval
      ),
      private_conn=ClassicSocketConnection(
        url=private_url, timeout=timeout, ping_interval=ping_interval
      ),
      credentials=credentials,
      validate=validate,
    )
