"""`spot.account.open_positions` -- private Spot endpoint."""

from typing_extensions import Literal, NotRequired, TypedDict
from typed_core.validation import validator
from ...core.endpoint.rpc import RpcEndpoint


OpenPositionKeywords = TypedDict('OpenPositionKeywords', {'class': NotRequired[str]})
"""
- `class`: Asset class of the position.
"""


class OpenPosition(OpenPositionKeywords):
  """One open margin position."""

  ordertxid: NotRequired[str]
  """Order ID responsible for the position."""
  posstatus: NotRequired[Literal['open']]
  """Position status."""
  pair: NotRequired[str]
  """Asset pair."""
  time: NotRequired[float]
  """Unix timestamp of the trade."""
  type: NotRequired[Literal['buy', 'sell']]
  """Direction of the position."""
  ordertype: NotRequired[str]
  """Order type used to open the position."""
  cost: NotRequired[str]
  """Opening cost of the position (quote currency)."""
  fee: NotRequired[str]
  """Opening fee of the position (quote currency)."""
  vol: NotRequired[str]
  """Position opening size (base currency)."""
  vol_closed: NotRequired[str]
  """Quantity closed (base currency)."""
  margin: NotRequired[str]
  """Initial margin consumed (quote currency)."""
  value: NotRequired[str]
  """Current value of the remaining position. Only present if `docalcs` requested."""
  net: NotRequired[str]
  """Unrealised P&L of the remaining position. Only present if `docalcs` requested."""
  terms: NotRequired[str]
  """Funding cost and term of the position (e.g. "0.0100% per 4 hours")."""
  rollovertm: NotRequired[str]
  """Timestamp of the next margin rollover fee."""
  misc: NotRequired[str]
  """Comma-delimited list of additional info."""
  oflags: NotRequired[str]
  """Comma-delimited list of opening order flags."""


validate_open_positions = validator(dict[str, OpenPosition])


class OpenPositions(RpcEndpoint):
  """`spot.account.open_positions`."""

  async def open_positions(
    self,
    *,
    txid: str | None = None,
    docalcs: bool | None = None,
    consolidation: Literal['market'] | None = None,
    rebase_multiplier: Literal['rebased', 'base'] | None = None,
  ) -> dict[str, OpenPosition]:
    """Get information about open margin positions.

    **API Key Permissions Required:** `Orders and trades - Query open orders & trades`

    Args:
      txid: Comma-delimited list of txids to limit output to.
      docalcs: Whether to include P&L calculations.
      consolidation: Consolidate positions by market/pair.
      rebase_multiplier: Optional parameter for viewing xstocks data. `rebased` displays in terms of underlying equity, `base` displays in terms of SPV tokens.

    References:
      - [Official docs](https://docs.kraken.com/api-reference/account-data/get-open-positions)
    """
    data = {}
    if txid is not None:
      data['txid'] = txid
    if docalcs is not None:
      data['docalcs'] = docalcs
    if consolidation is not None:
      data['consolidation'] = consolidation
    if rebase_multiplier is not None:
      data['rebase_multiplier'] = rebase_multiplier

    return await self.authed_request(
      '/0/private/OpenPositions', data, validator=validate_open_positions
    )
