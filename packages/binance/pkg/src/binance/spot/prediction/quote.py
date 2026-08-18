from typing_extensions import Literal, NotRequired, TypedDict
from typed_core.validation import validator
from binance.core import Timestamp
from binance.core.endpoint.rpc import RpcEndpoint


class PredictionQuote(TypedDict):
  """Price quote for a prediction order."""

  quoteId: NotRequired[str]
  """Quote ID. Pass this to `spot.prediction.place_order` to execute the quoted trade."""
  tokenId: NotRequired[str]
  """Prediction outcome token ID."""
  chance: NotRequired[str]
  """Implied probability for this outcome at quote time, as a decimal string."""
  vendor: NotRequired[str]
  """Prediction liquidity vendor backing this quote."""
  marketTitle: NotRequired[str]
  """Market title."""
  marketExtId: NotRequired[str]
  """Vendor-side identifier for this market."""
  side: NotRequired[Literal['BUY', 'SELL']]
  """Trade direction."""
  amountIn: NotRequired[str]
  """Input amount, in wei, as quoted."""
  amountOut: NotRequired[str]
  """Expected output amount, in wei, at the quoted price."""
  isMinAmountOut: NotRequired[bool]
  """Whether `amountOut` reflects the slippage-adjusted minimum rather than the expected fill amount."""
  feeAmount: NotRequired[str]
  """Fee amount, in wei (18 decimals), as a decimal string -- kept as a string since it may exceed a 64-bit integer's safe range."""
  feeDiscountBps: NotRequired[str]
  """Fee discount applied, in basis points, as a decimal string -- kept as a string to allow fractional basis-point values."""
  averagePrice: NotRequired[float]
  """Average execution price implied by this quote."""
  lastPrice: NotRequired[float]
  """Last traded price for this outcome at quote time."""
  priceImpact: NotRequired[float]
  """Estimated price impact of this trade."""
  timestamp: NotRequired[Timestamp]
  """Time this quote was generated."""
  chainId: NotRequired[str]
  """Chain ID this quote settles on."""
  userId: NotRequired[int]
  """Binance user ID this quote was issued to."""
  walletAddress: NotRequired[str]
  """User's prediction wallet address."""
  orderType: NotRequired[Literal['MARKET', 'LIMIT']]
  """Order type."""
  slippageBps: NotRequired[int]
  """Slippage tolerance in basis points, as quoted."""
  feeRateBps: NotRequired[int]
  """Fee rate in basis points, as quoted."""
  minReceive: NotRequired[str]
  """Minimum output amount this quote guarantees, in wei, given `slippageBps`."""
  expireAt: NotRequired[Timestamp]
  """Time this quote expires and can no longer be used to place an order."""
  priceLimit: NotRequired[str | None]
  """Limit price this quote was generated for, as a decimal string, or null for `MARKET` orders."""


class Quote(RpcEndpoint):
  """Get a price quote for a prediction order. The returned `quoteId` must be used in the subsequent `spot.prediction.place_order` request."""

  async def quote(
    self,
    *,
    wallet_address: str,
    token_id: str,
    side: Literal['BUY', 'SELL'],
    amount_in: str,
    order_type: Literal['MARKET', 'LIMIT'],
    slippage_bps: int,
    price_limit: str | None = None,
    chain_id: str | None = None,
    fee_rate_bps: int | None = None,
    funding_source: Literal['MPC', 'CEX'] | None = None,
    fund_transfer_amount: str | None = None,
    validate: bool | None = None,
  ) -> PredictionQuote:
    """Get a price quote for a prediction order. The returned `quoteId` must be used in the subsequent `spot.prediction.place_order` request.

    Args:
      wallet_address: User's prediction wallet address.
      token_id: Prediction outcome token ID.
      side: Trade direction.
      amount_in: Input amount in wei (18 decimals). Must be > 0. For `MARKET` orders, the minimum is approximately 1.5 USDT (varies by market depth); a smaller amount is rejected with `-9000 Your order amount is too small`. This minimum does not apply to `LIMIT` orders. Example: `1000000000000000000` = 1 USDT.
      order_type: Order type.
      slippage_bps: Slippage tolerance in basis points. Range 1-10000.
      price_limit: Limit price. Required when `orderType` is `LIMIT`. Must be > 0.
      chain_id: Chain ID. Default `56` (BSC).
      fee_rate_bps: Fee rate in basis points. Default `200`, range 1-10000.
      funding_source: Funding source.
      fund_transfer_amount: Amount to auto-transfer into the prediction wallet before quoting, in wei. Must be > 0 if provided.

    References:
      - [Official docs](https://developers.binance.com/en/docs/catalog/web3-wallet-prediction-trading/api/rest-api/trade#get-quote)
    """
    params: dict = {
      'walletAddress': wallet_address,
      'tokenId': token_id,
      'side': side,
      'amountIn': amount_in,
      'orderType': order_type,
      'slippageBps': slippage_bps,
    }
    if price_limit is not None:
      params['priceLimit'] = price_limit
    if chain_id is not None:
      params['chainId'] = chain_id
    if fee_rate_bps is not None:
      params['feeRateBps'] = fee_rate_bps
    if funding_source is not None:
      params['fundingSource'] = funding_source
    if fund_transfer_amount is not None:
      params['fundTransferAmount'] = fund_transfer_amount
    _Response = PredictionQuote
    _validator = validator[_Response](_Response)
    return await self.authed_request(
      'POST',
      '/sapi/v1/w3w/wallet/prediction/trade/get-quote',
      params=params,
      validator=_validator,
      validate=validate,
    )
