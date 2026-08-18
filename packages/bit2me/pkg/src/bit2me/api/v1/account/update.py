from datetime import datetime
from typing_extensions import Literal, NotRequired, TypedDict
from bit2me.types import BooleanResultResponse, DepositEstimation, FundsOrigin, UserType
from bit2me.core.endpoint import RpcEndpoint
from typed_core.validation import validator


class Address(TypedDict):
  country: str
  """The 2-letter country code"""
  state: str
  """State or region name."""
  city: str
  street: str
  zip: str


class Identity(TypedDict):
  type: NotRequired[Literal['idcard', 'passport', 'drivinglicense', 'visa']]
  number: NotRequired[str]
  expiryDate: NotRequired[datetime]
  countryCode: NotRequired[str]


class Profile(TypedDict):
  langCode: NotRequired[str]
  currencyCode: NotRequired[str]
  timeZone: NotRequired[str]


class Person(TypedDict):
  name: NotRequired[str]
  surname: NotRequired[str]
  gender: NotRequired[Literal['male', 'female', 'N/D']]
  birthDate: NotRequired[datetime]
  nationalityCountryCode: NotRequired[str]
  employmentStatus: NotRequired[
    Literal['employed', 'student', 'selfEmployed', 'retired', 'unemployed']
  ]
  profession: NotRequired[str]
  identity: NotRequired[Identity]


class UpdateAccountRequest(TypedDict):
  alias: NotRequired[str]
  person: NotRequired[Person]
  profile: NotRequired[Profile]
  address: NotRequired[Address]
  depositEstimation: NotRequired[DepositEstimation]
  selfInvoiceIdentityNumber: NotRequired[str]
  fundsOrigin: NotRequired[FundsOrigin]
  type: NotRequired[UserType]
  so: NotRequired[str]
  version: NotRequired[str]


validate_response = validator(BooleanResultResponse)


class Update(RpcEndpoint):
  async def __call__(
    self,
    update_account_request: UpdateAccountRequest,
    *,
    validate: bool | None = None,
  ) -> BooleanResultResponse:
    """Update account information.

    Args:
      update_account_request: The account details to be updated
      validate: Whether to validate the response against the expected schema.

    References:
      - [Bit2Me API docs](https://api.bit2me.com/doc#tag/account/PUT/v1/account/update)
    """
    return await self.authed_request(
      'put',
      '/v1/account/update',
      json=update_account_request,
      validator=validate_response,
      validate=validate,
    )
