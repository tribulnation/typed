"""The Bitget client root."""

from dataclasses import dataclass
import asyncio

from .core.auth import resolve_credentials
from .core.transport.http import HttpRpcClient
from .core.transport.ws.classic import ClassicSocketStreamClient
from .core.transport.ws.uta import UtaSocketStreamClient
from .classic.core import Classic
from .classic.streams import ClassicStreams
from .uta.core import Uta
from .uta.streams import UtaStreams


@dataclass(kw_only=True)
class Bitget:
  """Bitget client.

  Composes the Classic v2 and UTA v3 REST surfaces (sharing one `HttpRpcClient` — same
  host, envelope and signing scheme either way, see `spec/core.md` Surfaces) and their
  respective WebSocket surfaces (structurally distinct wire shapes, so each gets its own
  transport). One credential set is shared by both: a Bitget account is either
  Classic-mode or UTA-mode, never both at once, so it authenticates against whichever
  surface matches the account's actual mode — call the methods matching your account.

  Examples:
    ```python
    from typed_bitget import Bitget

    async with Bitget.new(public=True) as client:
      symbols = await client.classic.spot.symbols()
      instruments = await client.uta.market.instruments(category='SPOT')
    ```
  """

  classic: Classic
  uta: Uta
  classic_streams: ClassicStreams
  uta_streams: UtaStreams

  @classmethod
  def new(
    cls,
    *,
    access_key: str | None = None,
    secret_key: str | None = None,
    passphrase: str | None = None,
    public: bool = False,
    validate: bool = True,
  ):
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
    http = HttpRpcClient(credentials=credentials, validate=validate)
    return cls(
      classic=Classic(client=http),
      uta=Uta(client=http),
      classic_streams=ClassicStreams(
        client=ClassicSocketStreamClient.new(credentials=credentials, validate=validate)
      ),
      uta_streams=UtaStreams(
        client=UtaSocketStreamClient.new(credentials=credentials, validate=validate)
      ),
    )

  async def __aenter__(self):
    await asyncio.gather(
      self.classic.__aenter__(),
      self.uta.__aenter__(),
      self.classic_streams.__aenter__(),
      self.uta_streams.__aenter__(),
    )
    return self

  async def __aexit__(self, exc_type, exc_value, traceback):
    await asyncio.gather(
      self.classic.__aexit__(exc_type, exc_value, traceback),
      self.uta.__aexit__(exc_type, exc_value, traceback),
      self.classic_streams.__aexit__(exc_type, exc_value, traceback),
      self.uta_streams.__aexit__(exc_type, exc_value, traceback),
    )
