from decimal import Decimal
from datetime import datetime
from typing_extensions import Any, Literal, NotRequired, TypedDict
from bit2me.core.endpoint import RpcEndpoint
from typed_core.validation import validator


class Entry(TypedDict):
  id: NotRequired[str]
  """Funding movement identifier"""
  movementType: NotRequired[Literal['deposit', 'withdrawal']]
  """Direction of the funding movement"""
  amount: NotRequired[Decimal]
  """Movement amount, in terms of `currency`"""
  createdAt: NotRequired[datetime]
  """Date time in ISO 8601 string format"""
  walletId: NotRequired[str]
  """Identifier of the wallet the movement was applied to"""
  currency: NotRequired[str]
  """Valid currency symbol"""
  status: NotRequired[Literal['pending', 'completed', 'canceled']]
  """Current status of the funding movement"""
  serviceOrderName: NotRequired[Literal['wallet', 'admin', 'working-capital']]
  """Service that issued the movement"""


validate_response = validator(list[Entry])


class FundingMovements(RpcEndpoint):
  async def __call__(
    self,
    *,
    wallet_id: Any | None = None,
    currency: Any | None = None,
    from_: Any | None = None,
    to: Any | None = None,
    service_order_name: Any | None = None,
    movement_type: Any | None = None,
    limit: Any | None = None,
    validate: bool | None = None,
  ) -> list[Entry]:
    """Get funding movements

    Args:
      wallet_id: Wallet id
      currency: Currency
      from_: The initial date with time
      to: The end date with time
      service_order_name: Service order name (issuer)
      movement_type: Movement type
      limit: The maximum number of movements returned
      validate: Whether to validate the response against the expected schema.

    References:
      - [Bit2Me API docs](https://api.bit2me.com/trading-spot-rest#tag/funding/GET/v1/trading/movement)
    """
    params = {}
    if wallet_id is not None:
      params['walletId'] = wallet_id
    if currency is not None:
      params['currency'] = currency
    if from_ is not None:
      params['from'] = from_
    if to is not None:
      params['to'] = to
    if service_order_name is not None:
      params['serviceOrderName'] = service_order_name
    if movement_type is not None:
      params['movementType'] = movement_type
    if limit is not None:
      params['limit'] = limit
    return await self.authed_request(
      'GET',
      '/v1/trading/movement',
      params=params,
      validator=validate_response,
      validate=validate,
    )
