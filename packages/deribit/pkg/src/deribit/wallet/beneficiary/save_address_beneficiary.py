"""`private/save_address_beneficiary` — `private/save_address_beneficiary`."""

from typing_extensions import Literal, NotRequired, TypedDict
from typed_core.validation import validator
from deribit.core import RpcEndpoint


class AddressBeneficiary(TypedDict):
  """The saved beneficiary record."""

  currency: str
  """The currency symbol."""
  address: str
  """Address in currency format."""
  tag: NotRequired[str | None]
  """Tag for XRP addresses, when applicable."""
  user_id: int
  """Unique user identifier this beneficiary record belongs to."""
  agreed: bool
  """Whether the user agreed to share the provided information with 3rd parties."""
  personal: bool
  """Whether the user confirmed the address belongs to them and is accessible via an un-hosted wallet."""
  unhosted: bool
  """Whether the address belongs to an unhosted wallet."""
  beneficiary_vasp_name: str
  """Name of the beneficiary VASP."""
  beneficiary_vasp_did: str
  """DID of the beneficiary VASP."""
  beneficiary_vasp_website: NotRequired[str]
  """Website of the beneficiary VASP."""
  beneficiary_first_name: NotRequired[str]
  """First name of the beneficiary (if beneficiary is a person)."""
  beneficiary_last_name: NotRequired[str]
  """Last name of the beneficiary (if beneficiary is a person)."""
  beneficiary_company_name: NotRequired[str]
  """Company name of the beneficiary (if beneficiary is a company)."""
  beneficiary_address: str
  """Geographical address of the beneficiary."""
  created: int
  """Time this record was created (milliseconds since the Unix epoch)."""
  updated: int
  """Time this record was last updated (milliseconds since the Unix epoch)."""


validate_save_address_beneficiary = validator[AddressBeneficiary](AddressBeneficiary)


class SaveAddressBeneficiary(RpcEndpoint):
  """`private/save_address_beneficiary`."""

  async def save_address_beneficiary(
    self,
    *,
    currency: Literal[
      'BTC',
      'ETH',
      'STETH',
      'ETHW',
      'USDC',
      'USDT',
      'EURR',
      'SOL',
      'XRP',
      'USYC',
      'PAXG',
      'BNB',
      'USDE',
    ],
    address: str,
    tag: str | None = None,
    agreed: bool,
    personal: bool,
    unhosted: bool,
    beneficiary_vasp_name: str,
    beneficiary_vasp_did: str,
    beneficiary_vasp_website: str | None = None,
    beneficiary_first_name: str | None = None,
    beneficiary_last_name: str | None = None,
    beneficiary_company_name: str | None = None,
    beneficiary_address: str,
    validate: bool | None = None,
  ) -> AddressBeneficiary:
    """Saves beneficiary information for an address. This method allows you to store beneficiary details required for compliance purposes, including VASP information, personal details, and wallet type classification.

    Args:
      currency: The currency symbol.
      address: Address in currency format.
      tag: Tag for XRP addresses.
      agreed: Indicates that the user agreed to share the provided information with 3rd parties.
      personal: The user confirms that the provided address belongs to them and they have access to it via an un-hosted wallet.
      unhosted: Indicates if the address belongs to an unhosted wallet.
      beneficiary_vasp_name: Name of beneficiary VASP.
      beneficiary_vasp_did: DID of beneficiary VASP.
      beneficiary_vasp_website: Website of the beneficiary VASP. Required if the address book entry is associated with a VASP that is not on the venue's known list.
      beneficiary_first_name: First name of beneficiary (if beneficiary is a person).
      beneficiary_last_name: Last name of beneficiary (if beneficiary is a person).
      beneficiary_company_name: Beneficiary company name (if beneficiary is a company).
      beneficiary_address: Geographical address of the beneficiary.
      validate: Validate the response against the generated schema.

    References:
      - [Deribit API docs](https://docs.deribit.com/api-reference/wallet/private-save_address_beneficiary)
    """
    params: dict = {
      'currency': currency,
      'address': address,
      'agreed': agreed,
      'personal': personal,
      'unhosted': unhosted,
      'beneficiary_vasp_name': beneficiary_vasp_name,
      'beneficiary_vasp_did': beneficiary_vasp_did,
      'beneficiary_address': beneficiary_address,
    }
    if tag is not None:
      params['tag'] = tag
    if beneficiary_vasp_website is not None:
      params['beneficiary_vasp_website'] = beneficiary_vasp_website
    if beneficiary_first_name is not None:
      params['beneficiary_first_name'] = beneficiary_first_name
    if beneficiary_last_name is not None:
      params['beneficiary_last_name'] = beneficiary_last_name
    if beneficiary_company_name is not None:
      params['beneficiary_company_name'] = beneficiary_company_name
    return await self.authed_request(
      'private/save_address_beneficiary',
      params=params,
      validator=validate_save_address_beneficiary,
      validate=validate,
    )
