from typing_extensions import NotRequired, TypedDict
from bit2me.types import UserAddress
from bit2me.core.endpoint import RpcEndpoint
from typed_core.validation import validator


class UserAddressBody(TypedDict):
  id: NotRequired[str]
  userId: NotRequired[str]
  alias: NotRequired[str]
  streetAddress: str
  city: str
  stateCode: str
  """Value obtained from 'fips' (Federal Information Processing Standard  (https://en.wikipedia.org/wiki/Federal_Information_Processing_Standards)) field in /v1/misc/country/{countryISOCode}/region response.

  Additional information of this endpoint is available in misc section"""
  zip: str
  countryCode: str
  isResidence: NotRequired[bool]
  isDefaultAddress: NotRequired[bool]
  nationalityCountryCode: str


validate_response = validator(list[UserAddress])


class Update(RpcEndpoint):
  async def update(
    self,
    user_address_body: UserAddressBody,
    *,
    address_id: str,
    validate: bool | None = None,
  ) -> list[UserAddress]:
    """Update user address

    Args:
      address_id: The address id
      user_address_body: Address params
      validate: Whether to validate the response against the expected schema.

    References:
      - [Bit2Me API docs](https://api.bit2me.com/doc#tag/account/PUT/v1/account/address)
    """
    params: dict = {
      'addressId': address_id,
    }
    return await self.authed_request(
      'put',
      '/v1/account/address',
      params=params,
      json=user_address_body,
      validator=validate_response,
      validate=validate,
    )
