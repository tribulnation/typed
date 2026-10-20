"""Cached instrument and currency facts that EIP-712 signing needs, read from market data.

An order signs each leg's `instrument_hash` and its size scaled by `base_decimals`; a
transfer or withdrawal signs the currency's numeric id and an amount scaled by its
`balance_decimals`. None of that is in the request, so the trading core reads it from the
market-data gateway and caches it: a listed instrument's or currency's facts never change.

What is not cached is never assumed absent: an instrument is fetched by name the first time
it is signed for (a name the venue does not know fails that call and is not cached), and a
currency missing from the cached list refetches the list once before `BadRequest`, so a
currency listed after the first fetch is found without rebuilding the client.
"""

from dataclasses import dataclass, field
import asyncio

from typing_extensions import TYPE_CHECKING

from typed_core.exceptions import BadRequest

from .locks import LoopLock
from .owners import Owned
from .signing import CurrencyKey, InstrumentKey

if TYPE_CHECKING:
  from .transport.gateway import GatewayTransport


class CurrencySymbolKey(CurrencyKey):
  """A `/currency` entry: signing facts plus the symbol they are keyed by."""

  symbol: str


@dataclass(kw_only=True)
class Lookup(Owned):
  """Instrument and currency signing facts, fetched lazily and cached.

  Owned by the trading gateway that signs with them, it takes one ownership of the
  market-data gateway in turn (`Owned.shared`): that gateway counts its owners, so a
  market-data `async with` of the caller's own is never closed under it, nor it under the
  caller's.
  """

  market: 'GatewayTransport'
  """Market-data gateway the facts are read from."""
  instruments: dict[str, InstrumentKey] = field(
    default_factory=dict, init=False, repr=False
  )
  currencies: dict[str, CurrencyKey] | None = field(
    default=None, init=False, repr=False
  )
  lock: LoopLock = field(default_factory=LoopLock, init=False, repr=False)
  """Guards the currency-list fetches; per event loop, so a reused client never trips."""

  def shared(self) -> list[Owned]:
    """The market-data gateway, owned once more while the lookup is owned."""
    return [self.market]

  async def instrument_keys(self, names: set[str]) -> dict[str, InstrumentKey]:
    """Signing facts of the given instruments, fetching the ones not cached yet.

    Args:
      names: Instrument names, e.g. `BTC_USDT_Perp`.

    Raises:
      BadRequest: The venue does not know one of them (see `instrument_key`).
    """
    missing = sorted(names - self.instruments.keys())
    if missing:
      fetched = await asyncio.gather(*(self.instrument_key(name) for name in missing))
      self.instruments.update(zip(missing, fetched))
    return {name: self.instruments[name] for name in names}

  async def instrument_key(self, name: str) -> InstrumentKey:
    """Fetch one instrument's signing facts.

    Args:
      name: Instrument name, e.g. `BTC_USDT_Perp`.

    Raises:
      BadRequest: The venue does not know `name`. It answers an unknown instrument with a
        bare `1003` ("Request could not be processed due to malformed syntax"), so the
        error is raised again naming the instrument, keeping the venue's code and payload:
        `(code, "Unknown instrument 'X' (...): <venue message>", payload)`.
    """
    try:
      return await self.market.request(
        {'instrument': name},
        method='POST',
        path='/full/v1/instrument',
        response_type=InstrumentKey,
        validate=True,
      )
    except BadRequest as e:
      raise unknown_instrument(name, e) from e

  async def currency_key(self, symbol: str) -> CurrencyKey:
    """Signing facts of one currency, fetching the currency list on first use and once more
    when `symbol` is missing from the cached one.

    Args:
      symbol: Currency symbol, e.g. `USDT`.

    Raises:
      BadRequest: The venue lists no such currency, even after refetching the list.
    """
    async with self.lock:
      currencies = self.currencies
      if currencies is None or symbol not in currencies:
        currencies = self.currencies = await self.fetch_currencies()
    if symbol not in currencies:
      raise BadRequest(f'Unknown currency {symbol!r}')
    return currencies[symbol]

  async def fetch_currencies(self) -> dict[str, CurrencyKey]:
    """Fetch every listed currency's signing facts, by symbol."""
    listed = await self.market.request(
      {},
      method='POST',
      path='/full/v1/currency',
      response_type=list[CurrencySymbolKey],
      validate=True,
    )
    return {
      c['symbol']: {'id': c['id'], 'balance_decimals': c['balance_decimals']}
      for c in listed
    }


def unknown_instrument(name: str, error: BadRequest) -> BadRequest:
  """The error for an instrument the venue refused to look up, naming it.

  Keeps the convention of the venue's error: `(code, message, ...)` with the message now
  naming the instrument, or a single message when the venue's carried no code.

  Args:
    name: The instrument signing needed.
    error: The venue's error for its lookup.
  """
  subject = f'Unknown instrument {name!r} (its signing facts could not be looked up)'
  if len(error.args) >= 2:
    code, message, *rest = error.args
    return BadRequest(code, f'{subject}: {message}', *rest)
  reason = error.args[0] if error.args else 'no reason given'
  return BadRequest(f'{subject}: {reason}')
