from mexc.core import Timestamp, timestamp as ts, validator
from typing_extensions import TypedDict
from mexc.spot.core import AuthSpotMixin, ErrorResponse

class WithdrawResponse(TypedDict):
  """Withdrawal creation response."""
  id: str | None
  """Withdrawal id."""

Response: type[WithdrawResponse | ErrorResponse] = WithdrawResponse | ErrorResponse # type: ignore
adapter = validator(Response)

class Withdraw(AuthSpotMixin):
  async def withdraw(
    self, *,
    coin: str, withdraw_order_id: str | None = None, net_work: str | None = None,
    contract_address: str | None = None, address: str, memo: str | None = None,
    amount: str, remark: str | None = None, timestamp: Timestamp | None = None,
    validate: bool | None = None,
  ) -> WithdrawResponse:
    """Submits a live asset withdrawal request from the signed spot account.

    Args:
      coin: Asset to withdraw.
      withdraw_order_id: Optional client withdrawal order id.
      net_work: Withdrawal network identifier from currency configuration.
      contract_address: Token contract address, when required.
      address: Destination withdrawal address.
      memo: Destination memo or tag when required by the network.
      amount: Withdrawal amount.
      remark: Optional withdrawal remark.
      timestamp: Signed request timestamp in milliseconds.
      validate: Validation override for this request.

    Returns:
      The validated endpoint response.

    References:
      - [MEXC API docs](https://mexcdevelop.github.io/apidocs/spot_v3_en/#withdraw-new)
    """
    if timestamp is None:
      timestamp = ts.parse(ts.now())
    params = {}
    if coin is not None:
      params['coin'] = coin
    if withdraw_order_id is not None:
      params['withdrawOrderId'] = withdraw_order_id
    if net_work is not None:
      params['netWork'] = net_work
    if contract_address is not None:
      params['contractAddress'] = contract_address
    if address is not None:
      params['address'] = address
    if memo is not None:
      params['memo'] = memo
    if amount is not None:
      params['amount'] = amount
    if remark is not None:
      params['remark'] = remark
    if timestamp is not None:
      params['timestamp'] = ts.dump(timestamp)
    r = await self.signed_request('POST', '/api/v3/capital/withdraw', params=params)
    return self.output(r.text, adapter, validate)
