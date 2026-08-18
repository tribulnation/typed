"""`private/get_positions` — `private/get_positions`."""

from typing_extensions import Literal, NotRequired, TypedDict
from typed_core.validation import validator
from deribit.core import RpcEndpoint


class PositionsEntry(TypedDict):
  instrument_name: str
  """Unique instrument identifier."""
  kind: Literal['future', 'option', 'spot', 'future_combo', 'option_combo']
  """Instrument kind."""
  average_price: float
  """Average price of trades that built this position."""
  direction: Literal['buy', 'sell', 'zero']
  """Position direction."""
  mark_price: float
  """Current mark price for the position's instrument."""
  delta: float
  """Delta parameter."""
  gamma: NotRequired[float]
  """Only for options: gamma parameter."""
  vega: NotRequired[float]
  """Only for options: vega parameter."""
  theta: NotRequired[float]
  """Only for options: theta parameter."""
  index_price: float
  """Current index price."""
  initial_margin: float
  """Initial margin."""
  maintenance_margin: float
  """Maintenance margin."""
  settlement_price: NotRequired[float]
  """Optional (not present for spot). Last settlement price for the position's instrument; 0 if the instrument was not yet settled."""
  total_profit_loss: float
  """Total profit or loss from the position."""
  floating_profit_loss: float
  """Floating (unrealized) profit or loss."""
  realized_profit_loss: float
  """Realized profit or loss."""
  size: float
  """Position size: for futures, in quote currency (e.g. USD); for options, in base currency (e.g. BTC)."""
  size_currency: NotRequired[float]
  """Only for futures: position size in base currency."""
  average_price_usd: NotRequired[float]
  """Only for options: average price in USD."""
  floating_profit_loss_usd: NotRequired[float]
  """Only for options: floating profit or loss in USD."""
  leverage: NotRequired[int]
  """Current available leverage for a future position."""
  realized_funding: NotRequired[float]
  """Realized funding in the current session, included in session realized profit or loss; only for perpetual positions."""
  interest_value: NotRequired[float]
  """Value used to calculate `realized_funding` (perpetual only)."""
  estimated_liquidation_price: NotRequired[float]
  """Estimated liquidation price; added only for futures, for users on the `segregated_sm` margin model."""
  open_orders_margin: NotRequired[float]
  """Margin reserved by open orders on this instrument."""
  user_id: NotRequired[int]
  """Id of the account this position belongs to."""


validate_get_positions = validator[list[PositionsEntry]](list[PositionsEntry])


class GetPositions(RpcEndpoint):
  """`private/get_positions`."""

  async def get_positions(
    self,
    *,
    currency: Literal['BTC', 'ETH', 'USDC', 'USDT', 'EURR', 'any'] | None = None,
    kind: Literal['future', 'option', 'future_combo', 'option_combo'] | None = None,
    subaccount_id: int | None = None,
    validate: bool | None = None,
  ) -> list[PositionsEntry]:
    """Retrieves all open positions for the authenticated account, optionally filtered by currency and instrument kind. To retrieve positions for a specific subaccount, use the `subaccount_id` parameter.

    Args:
      currency: Currency name, or `"any"` if it does not matter.
      kind: Instrument kind filter (spot is excluded -- spot trades settle immediately and have no open positions).
      subaccount_id: The user id for the subaccount.
      validate: Validate the response against the generated schema.

    References:
      - [Deribit API docs](https://docs.deribit.com/api-reference/account-management/private-get_positions)
    """
    params = {}
    if currency is not None:
      params['currency'] = currency
    if kind is not None:
      params['kind'] = kind
    if subaccount_id is not None:
      params['subaccount_id'] = subaccount_id
    return await self.authed_request(
      'private/get_positions',
      params=params,
      validator=validate_get_positions,
      validate=validate,
    )
