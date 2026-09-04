"""Bitget client root composition base (design §5c): a hand-written class holding each
heterogeneous child's already-built transport, wrapped by the generated `Bitget`
composite.

`Bitget` composes four genuinely different children -- `classic`/`uta` (REST, sharing
one `HttpRpcClient` -- same host, envelope and signing scheme either way, see
`spec/core.md` Surfaces) and `classic_streams`/`uta_streams` (two structurally distinct
WebSocket wire dialects, each its own physical connection pair) -- so its own resolved
`core` (`BitgetBase`) is a *Base* holding one field per child, built once in `.new()`,
never a single shared transport every child forwards unchanged (design §5c).
"""

from typing_extensions import Self
from dataclasses import dataclass
import asyncio

from .auth import resolve_credentials
from .transport.http import HttpRpcClient
from .transport.ws.classic import ClassicSocketStreamClient
from .transport.ws.uta import UtaSocketStreamClient


@dataclass(kw_only=True)
class BitgetBase:
  """Bitget client root: builds and owns the three physical transports every generated
  composite (`Classic`, `Uta`, `ClassicStreams`, `UtaStreams`) forwards unchanged -- one
  HTTP client shared by `classic`/`uta`, and two WebSocket connection pairs, one per
  generation. One credential set is shared by all of them: a Bitget account is either
  Classic-mode or UTA-mode, never both at once, so it authenticates against whichever
  surface matches the account's actual mode -- call the methods matching your account.
  """

  http_client: HttpRpcClient
  classic_streams_client: ClassicSocketStreamClient
  uta_streams_client: UtaSocketStreamClient

  @classmethod
  def new(
    cls,
    *,
    access_key: str | None = None,
    secret_key: str | None = None,
    passphrase: str | None = None,
    public: bool = False,
    validate: bool = True,
  ) -> Self:
    """Build a Bitget client.

    Args:
      access_key: Bitget access key; read from `BITGET_ACCESS_KEY` when omitted.
      secret_key: Bitget secret key; read from `BITGET_SECRET_KEY` when omitted.
      passphrase: Bitget API passphrase; read from `BITGET_PASSPHRASE` when omitted.
      public: Skip credential resolution for a credential-free client that can only call
        public endpoints.
      validate: Validate responses by default.
    """
    credentials = resolve_credentials(access_key, secret_key, passphrase, public=public)
    return cls(
      http_client=HttpRpcClient(credentials=credentials, validate=validate),
      classic_streams_client=ClassicSocketStreamClient.new(
        credentials=credentials, validate=validate,
      ),
      uta_streams_client=UtaSocketStreamClient.new(credentials=credentials, validate=validate),
    )

  async def __aenter__(self) -> Self:
    await asyncio.gather(
      self.http_client.__aenter__(),
      self.classic_streams_client.__aenter__(),
      self.uta_streams_client.__aenter__(),
    )
    return self

  async def __aexit__(self, exc_type, exc_value, traceback):
    await asyncio.gather(
      self.http_client.__aexit__(exc_type, exc_value, traceback),
      self.classic_streams_client.__aexit__(exc_type, exc_value, traceback),
      self.uta_streams_client.__aexit__(exc_type, exc_value, traceback),
    )
