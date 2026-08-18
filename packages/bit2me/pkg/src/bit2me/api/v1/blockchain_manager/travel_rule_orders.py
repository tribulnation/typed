from typing_extensions import Literal, NotRequired, TypedDict
from bit2me.types import BooleanResultResponse
from bit2me.core.endpoint import RpcEndpoint
from typed_core.validation import validator


class TravelRuleInformationRequest(TypedDict):
  walletType: Literal['exchange', 'unhosted']
  """Wallet type where the user is sending the information. It coud be an exchange or selfhosted wallet."""
  exchangeName: NotRequired[str]
  """Exchange name if the operation is send to it."""
  walletOwnership: Literal['own', 'other']
  """If sending to a own or others address."""
  personType: Literal['person', 'company']
  """If sending to a person or company."""
  name: str
  """Beneficiary person name or company name."""
  surname: NotRequired[str]
  """Beneficiary person surname."""


validate_response = validator(BooleanResultResponse)


class TravelRuleOrders(RpcEndpoint):
  async def travel_rule_orders(
    self,
    order_id: str,
    travel_rule_information_request: TravelRuleInformationRequest,
    *,
    validate: bool | None = None,
  ) -> BooleanResultResponse:
    """The Travel Rule is a regulation that requires transfers of funds, including crypto assets, to include information about the originator and the beneficiary to prevent money laundering and terrorist financing. [More information](https://support.bit2me.com/en/support/solutions/articles/35000278021-travel-rule-frequently-asked-questions)

    When you create a blockchain withdrawal, its status will be set to `waiting-user-information`. To proceed with the transaction, you must send the required Travel Rule parameters. If this information is not provided, the operation will remain in this status and will be automatically canceled within a few hours.

    Args:
      order_id: The order ID
      travel_rule_information_request: The originator/beneficiary Travel Rule information for this withdrawal order.
      validate: Whether to validate the response against the expected schema.

    References:
      - [Bit2Me API docs](https://api.bit2me.com/doc#tag/funding/POST/v1/blockchain-manager/travel-rule-order/{orderId})
    """
    return await self.authed_request(
      'POST',
      f'/v1/blockchain-manager/travel-rule-order/{order_id}',
      json=travel_rule_information_request,
      validator=validate_response,
      validate=validate,
    )
