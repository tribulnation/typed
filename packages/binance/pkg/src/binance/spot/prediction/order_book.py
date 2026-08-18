from typing_extensions import NotRequired, TypedDict
from typed_core.validation import validator
from binance.core import Timestamp
from binance.core.endpoint.rpc import RpcEndpoint


class PredictionOrderBookAskLevel(TypedDict):
  """One ask price level."""

  price: NotRequired[str]
  """Ask price, as a decimal string."""
  size: NotRequired[str]
  """Size available at this price, as a decimal string."""


class PredictionOrderBookBidLevel(TypedDict):
  """One bid price level."""

  price: NotRequired[str]
  """Bid price, as a decimal string."""
  size: NotRequired[str]
  """Size available at this price, as a decimal string."""


class PredictionOrderBook(TypedDict):
  """Current order book for a prediction outcome token."""

  outcome: NotRequired[str]
  """Outcome name this order book is for."""
  tokenId: NotRequired[str]
  """Prediction outcome token ID."""
  timestamp: NotRequired[Timestamp]
  """Time this order book snapshot was taken."""
  bids: NotRequired[list[PredictionOrderBookBidLevel]]
  """Bid levels, best first."""
  asks: NotRequired[list[PredictionOrderBookAskLevel]]
  """Ask levels, best first."""


class OrderBook(RpcEndpoint):
  """Get the current order book (bids and asks) for a specific prediction market outcome token."""

  async def order_book(
    self,
    *,
    vendor: str,
    market_id: int,
    token_id: str,
    validate: bool | None = None,
  ) -> PredictionOrderBook:
    """Get the current order book (bids and asks) for a specific prediction market outcome token.

    Args:
      vendor: Vendor identifier (e.g. `predict_fun`).
      market_id: Market ID. Must be > 0.
      token_id: Prediction outcome token ID.

    References:
      - [Official docs](https://developers.binance.com/en/docs/catalog/web3-wallet-prediction-trading/api/rest-api/market-data#query-order-book)
    """
    params: dict = {
      'vendor': vendor,
      'marketId': market_id,
      'tokenId': token_id,
    }
    _Response = PredictionOrderBook
    _validator = validator[_Response](_Response)
    return await self.authed_request(
      'GET',
      '/sapi/v1/w3w/wallet/prediction/order-book',
      params=params,
      validator=_validator,
      validate=validate,
    )
