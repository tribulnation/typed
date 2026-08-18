from typing_extensions import NotRequired, TypedDict
from typed_core.validation import validator
from binance.core.endpoint.rpc import RpcEndpoint


class PredictionPnlRecord(TypedDict):
  """Profit and loss record for one prediction position."""

  id: NotRequired[int]
  """Profit and loss record ID."""
  walletAddress: NotRequired[str]
  """User's prediction wallet address."""
  marketTopicId: NotRequired[int]
  """Market topic ID."""
  marketId: NotRequired[int]
  """Market ID."""
  tokenId: NotRequired[str]
  """Prediction outcome token ID."""
  vendor: NotRequired[str]
  """Prediction liquidity vendor backing this position."""
  currentShares: NotRequired[str]
  """Current outcome shares held, as a decimal string."""
  avgPrice: NotRequired[str]
  """Average entry price, as a decimal string."""
  currentPrice: NotRequired[str]
  """Current market price, as a decimal string."""
  realizedPnl: NotRequired[str]
  """Realized profit and loss, as a decimal string."""
  unrealizedPnl: NotRequired[str]
  """Unrealized profit and loss, as a decimal string."""
  totalPnl: NotRequired[str]
  """Realized plus unrealized profit and loss, as a decimal string."""
  pnlPercentage: NotRequired[str]
  """Profit and loss as a percentage of cost, as a decimal string."""
  isResolved: NotRequired[bool]
  """Whether the underlying market has resolved."""


class PredictionPnlSingle(TypedDict):
  id: NotRequired[int]
  """Profit and loss record ID."""
  walletAddress: NotRequired[str]
  """User's prediction wallet address."""
  marketTopicId: NotRequired[int]
  """Market topic ID."""
  marketId: NotRequired[int]
  """Market ID."""
  tokenId: NotRequired[str]
  """Prediction outcome token ID."""
  vendor: NotRequired[str]
  """Prediction liquidity vendor backing this position."""
  currentShares: NotRequired[str]
  """Current outcome shares held, as a decimal string."""
  avgPrice: NotRequired[str]
  """Average entry price, as a decimal string."""
  currentPrice: NotRequired[str]
  """Current market price, as a decimal string."""
  realizedPnl: NotRequired[str]
  """Realized profit and loss, as a decimal string."""
  unrealizedPnl: NotRequired[str]
  """Unrealized profit and loss, as a decimal string."""
  totalPnl: NotRequired[str]
  """Realized plus unrealized profit and loss, as a decimal string."""
  pnlPercentage: NotRequired[str]
  """Profit and loss as a percentage of cost, as a decimal string."""
  isResolved: NotRequired[bool]
  """Whether the underlying market has resolved."""


class PredictionPnlQueryResult(TypedDict):
  """Profit and loss records for this user's prediction positions."""

  chainId: NotRequired[str]
  """Chain ID these records settle on."""
  walletAddress: NotRequired[str]
  """User's prediction wallet address."""
  pnl: NotRequired[PredictionPnlSingle | None]
  """Single profit and loss record, present when `tokenId` was provided; null otherwise."""
  pnlList: NotRequired[list[PredictionPnlRecord]]
  """Profit and loss records, present when `tokenId` was not provided."""
  totalCount: NotRequired[int]
  """Number of records in `pnlList` (or `1` when `pnl` is returned instead)."""
  totalRealizedPnl: NotRequired[str]
  """Total realized profit and loss across the returned records, as a decimal string."""
  totalUnrealizedPnl: NotRequired[str]
  """Total unrealized profit and loss across the returned records, as a decimal string."""
  totalPnl: NotRequired[str]
  """Total realized plus unrealized profit and loss across the returned records, as a decimal string."""


class Pnl(RpcEndpoint):
  """Query profit and loss records for the authenticated user's prediction positions. When `tokenId` is provided, returns a single record in `pnl`; otherwise returns a list in `pnlList`."""

  async def pnl(
    self,
    *,
    wallet_address: str,
    token_id: str | None = None,
    market_id: int | None = None,
    market_topic_id: int | None = None,
    active_only: bool | None = None,
    validate: bool | None = None,
  ) -> PredictionPnlQueryResult:
    """Query profit and loss records for the authenticated user's prediction positions. When `tokenId` is provided, returns a single record in `pnl`; otherwise returns a list in `pnlList`.

    Args:
      wallet_address: User's prediction wallet address.
      token_id: Filter by prediction token ID.
      market_id: Filter by market ID. Must be > 0.
      market_topic_id: Filter by market topic ID. Must be > 0.
      active_only: If `true`, return only active (unresolved) positions.

    References:
      - [Official docs](https://developers.binance.com/en/docs/catalog/web3-wallet-prediction-trading/api/rest-api/position#query-pn-l)
    """
    params: dict = {
      'walletAddress': wallet_address,
    }
    if token_id is not None:
      params['tokenId'] = token_id
    if market_id is not None:
      params['marketId'] = market_id
    if market_topic_id is not None:
      params['marketTopicId'] = market_topic_id
    if active_only is not None:
      params['activeOnly'] = active_only
    _Response = PredictionPnlQueryResult
    _validator = validator[_Response](_Response)
    return await self.authed_request(
      'GET',
      '/sapi/v1/w3w/wallet/prediction/pnl/query',
      params=params,
      validator=_validator,
      validate=validate,
    )
