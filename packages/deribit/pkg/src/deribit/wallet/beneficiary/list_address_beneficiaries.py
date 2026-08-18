"""`private/list_address_beneficiaries` — `private/list_address_beneficiaries`."""

from typing_extensions import AsyncIterator, Literal, NotRequired, TypedDict
from typed_core.validation import validator
from deribit.core import RpcEndpoint


class AddressBeneficiary(TypedDict):
  """Beneficiary information stored for one address."""

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


class AddressBeneficiariesPage(TypedDict):
  """One page of beneficiary records."""

  data: list[AddressBeneficiary]
  """Beneficiary records on this page."""
  continuation: NotRequired[str]
  """Token for the next page, passed back as `continuation` -- absent once results are exhausted."""
  count: NotRequired[int]
  """Total number of matching results available."""


validate_list_address_beneficiaries = validator[AddressBeneficiariesPage](
  AddressBeneficiariesPage
)


class ListAddressBeneficiaries(RpcEndpoint):
  """`private/list_address_beneficiaries`."""

  async def list_address_beneficiaries(
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
    ]
    | None = None,
    address: str | None = None,
    tag: str | None = None,
    created_before: int | None = None,
    created_after: int | None = None,
    updated_before: int | None = None,
    updated_after: int | None = None,
    personal: bool | None = None,
    unhosted: bool | None = None,
    beneficiary_vasp_name: str | None = None,
    beneficiary_vasp_did: str | None = None,
    beneficiary_vasp_website: str | None = None,
    limit: int | None = None,
    continuation: str | None = None,
    validate: bool | None = None,
  ) -> AddressBeneficiariesPage:
    """Lists address beneficiaries with optional filtering and pagination. Returns all saved beneficiary information for addresses, with support for filtering by currency, address, wallet type, VASP details, and date ranges.

    Args:
      currency: Filter by currency symbol.
      address: Filter by address, in currency format.
      tag: Filter by tag (XRP addresses).
      created_before: Filter by creation timestamp (before), milliseconds since the Unix epoch.
      created_after: Filter by creation timestamp (after), milliseconds since the Unix epoch.
      updated_before: Filter by update timestamp (before), milliseconds since the Unix epoch.
      updated_after: Filter by update timestamp (after), milliseconds since the Unix epoch.
      personal: Filter by the personal-wallet flag.
      unhosted: Filter by the unhosted-wallet flag.
      beneficiary_vasp_name: Filter by beneficiary VASP name.
      beneficiary_vasp_did: Filter by beneficiary VASP DID.
      beneficiary_vasp_website: Filter by beneficiary VASP website.
      limit: Maximum number of results to return.
      continuation: Continuation token for pagination, from a previous page's response.
      validate: Validate the response against the generated schema.

    References:
      - [Deribit API docs](https://docs.deribit.com/api-reference/wallet/private-list_address_beneficiaries)
    """
    params = {}
    if currency is not None:
      params['currency'] = currency
    if address is not None:
      params['address'] = address
    if tag is not None:
      params['tag'] = tag
    if created_before is not None:
      params['created_before'] = created_before
    if created_after is not None:
      params['created_after'] = created_after
    if updated_before is not None:
      params['updated_before'] = updated_before
    if updated_after is not None:
      params['updated_after'] = updated_after
    if personal is not None:
      params['personal'] = personal
    if unhosted is not None:
      params['unhosted'] = unhosted
    if beneficiary_vasp_name is not None:
      params['beneficiary_vasp_name'] = beneficiary_vasp_name
    if beneficiary_vasp_did is not None:
      params['beneficiary_vasp_did'] = beneficiary_vasp_did
    if beneficiary_vasp_website is not None:
      params['beneficiary_vasp_website'] = beneficiary_vasp_website
    if limit is not None:
      params['limit'] = limit
    if continuation is not None:
      params['continuation'] = continuation
    return await self.authed_request(
      'private/list_address_beneficiaries',
      params=params,
      validator=validate_list_address_beneficiaries,
      validate=validate,
    )

  async def list_address_beneficiaries_paged(
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
    ]
    | None = None,
    address: str | None = None,
    tag: str | None = None,
    created_before: int | None = None,
    created_after: int | None = None,
    updated_before: int | None = None,
    updated_after: int | None = None,
    personal: bool | None = None,
    unhosted: bool | None = None,
    beneficiary_vasp_name: str | None = None,
    beneficiary_vasp_did: str | None = None,
    beneficiary_vasp_website: str | None = None,
    limit: int | None = None,
    max_pages: int | None = None,
    validate: bool | None = None,
  ) -> AsyncIterator[AddressBeneficiariesPage]:
    """Yield successive pages of `list_address_beneficiaries`.

    Passes each page's token back as `continuation` and stops when a response carries no
    `continuation`, or after `max_pages` pages when one is given.
    """
    continuation: str | None = None
    pages = 0
    while True:
      response = await self.list_address_beneficiaries(
        currency=currency,
        address=address,
        tag=tag,
        created_before=created_before,
        created_after=created_after,
        updated_before=updated_before,
        updated_after=updated_after,
        personal=personal,
        unhosted=unhosted,
        beneficiary_vasp_name=beneficiary_vasp_name,
        beneficiary_vasp_did=beneficiary_vasp_did,
        beneficiary_vasp_website=beneficiary_vasp_website,
        limit=limit,
        continuation=continuation,
        validate=validate,
      )
      yield response
      pages += 1
      if max_pages is not None and pages >= max_pages:
        break
      continuation = response.get('continuation') if response is not None else None
      if not continuation:
        break
