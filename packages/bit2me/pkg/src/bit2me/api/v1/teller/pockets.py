from typing_extensions import TypedDict
from bit2me.core.endpoint import RpcEndpoint
from typed_core.validation import validator


class Pocket(TypedDict):
  """Pocket the reference was generated for."""

  userId: str
  """Identifier of the pocket's owner."""
  pocketId: str
  """Identifier of the pocket."""
  reference: str
  """Bank transfer reference to use when depositing into this pocket."""


class TellerBankAccount(TypedDict):
  """A bank account the caller can transfer funds to in order to fund the pocket."""

  bankId: str
  """Identifier of the beneficiary bank."""
  beneficiary: str
  """Name of the account beneficiary."""
  bankName: str
  """Name of the beneficiary bank."""
  address: str
  """Address of the beneficiary bank."""
  swift: str
  """SWIFT/BIC code of the beneficiary bank."""
  account: str
  """IBAN or account number to transfer funds to."""
  public: bool
  """Whether this bank account is shown to all users or restricted."""
  currency: str
  """Currency accepted by this bank account."""
  country: str
  """ISO country code of the beneficiary bank."""


class TellerPocketReferenceResponse(TypedDict):
  pocket: Pocket
  bankAccounts: dict[str, TellerBankAccount]
  """Bank accounts available to fund this pocket, keyed by an internal account identifier."""


validate_response = validator(TellerPocketReferenceResponse)


class Pockets(RpcEndpoint):
  async def __call__(
    self,
    *,
    pocket_id: str,
    validate: bool | None = None,
  ) -> TellerPocketReferenceResponse:
    """Returns a reference for the specified pocket. Reference is generated if it doesn't exist.

    Args:
      pocket_id: Id of the pocket to retrieve the reference from
      validate: Whether to validate the response against the expected schema.

    References:
      - [Bit2Me API docs](https://api.bit2me.com/doc#tag/funding/GET/v1/teller/pocket/reference)
    """
    params: dict = {
      'pocketId': pocket_id,
    }
    return await self.authed_request(
      'GET',
      '/v1/teller/pocket/reference',
      params=params,
      validator=validate_response,
      validate=validate,
    )
