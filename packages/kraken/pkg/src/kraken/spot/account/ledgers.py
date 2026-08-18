"""`spot.account.ledgers` -- private Spot endpoint."""

from typing_extensions import Literal, NotRequired
from typed_core.validation import TypedDict, validator
from ...core.endpoint.rpc import RpcEndpoint


class LedgerEntry(TypedDict):
  """One ledger entry."""

  refid: NotRequired[str]
  """Reference ID of the parent transaction (trade, deposit, withdrawal, etc.) that caused the ledger entry."""
  time: NotRequired[float]
  """Unix timestamp of the ledger entry."""
  type: NotRequired[
    Literal[
      'none',
      'trade',
      'deposit',
      'withdrawal',
      'transfer',
      'margin',
      'adjustment',
      'rollover',
      'spend',
      'receive',
      'settled',
      'credit',
      'staking',
      'reward',
      'dividend',
      'sale',
      'conversion',
      'nfttrade',
      'nftcreatorfee',
      'nftrebate',
      'custodytransfer',
    ]
  ]
  """Type of ledger entry."""
  subtype: NotRequired[str]
  """Additional info relating to the ledger entry type, where applicable."""
  aclass: NotRequired[str]
  """Asset class."""
  asset: NotRequired[str]
  """Asset."""
  amount: NotRequired[str]
  """Transaction amount."""
  fee: NotRequired[str]
  """Transaction fee."""
  balance: NotRequired[str]
  """Resulting balance."""


class LedgersInfo(TypedDict):
  """Ledger entries."""

  ledger: NotRequired[dict[str, LedgerEntry]]
  """Ledger entries, keyed by ledger ID."""
  count: NotRequired[int]
  """Amount of available ledger info matching criteria. Omitted from the response when `without_count` is `true`."""


validate_ledgers = validator(LedgersInfo)


class Ledgers(RpcEndpoint):
  """`spot.account.ledgers`."""

  async def ledgers(
    self,
    *,
    asset: str | None = None,
    aclass: str | None = None,
    type: Literal[
      'all',
      'trade',
      'deposit',
      'withdrawal',
      'transfer',
      'margin',
      'adjustment',
      'rollover',
      'credit',
      'settled',
      'staking',
      'dividend',
      'sale',
      'nft_rebate',
    ]
    | None = None,
    start: int | None = None,
    end: int | None = None,
    ofs: int | None = None,
    without_count: bool | None = None,
    rebase_multiplier: Literal['rebased', 'base'] | None = None,
  ) -> LedgersInfo:
    """Retrieve information about ledger entries. 50 results are returned at a time, the most recent by default.

    **Note on Staking/Earn assets:** assets migrated from the legacy Staking system to the new Earn system may appear with symbol extensions -- `.B` (new yield-bearing products), `.F` (auto-earning Kraken Rewards) -- these are read-only for transacting; use the base asset instead.

    **API Key Permissions Required:** `Data - Query ledger entries`

    Args:
      asset: Filter output by asset, or a comma-delimited list of assets.
      aclass: Filter output by asset class.
      type: Type of ledger entries to retrieve.
      start: Starting unix timestamp or ledger ID of results (exclusive).
      end: Ending unix timestamp or ledger ID of results (inclusive).
      ofs: Result offset for pagination.
      without_count: If true, does not retrieve the count of ledger entries. Request can be noticeably faster for users with many ledger entries, as this avoids an extra database query.
      rebase_multiplier: Optional parameter for viewing xstocks data. `rebased` displays in terms of underlying equity, `base` displays in terms of SPV tokens.

    References:
      - [Official docs](https://docs.kraken.com/api-reference/account-data/get-ledgers-info)
    """
    data = {}
    if asset is not None:
      data['asset'] = asset
    if aclass is not None:
      data['aclass'] = aclass
    if type is not None:
      data['type'] = type
    if start is not None:
      data['start'] = start
    if end is not None:
      data['end'] = end
    if ofs is not None:
      data['ofs'] = ofs
    if without_count is not None:
      data['without_count'] = without_count
    if rebase_multiplier is not None:
      data['rebase_multiplier'] = rebase_multiplier

    return await self.authed_request(
      '/0/private/Ledgers', data, validator=validate_ledgers
    )
