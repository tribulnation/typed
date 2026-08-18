from typing_extensions import Literal
from bit2me.core.endpoint import RpcEndpoint
from typed_core.validation import validator

validate_response = validator(str)


class Subaccounts(RpcEndpoint):
  async def subaccounts(
    self,
    *,
    identity_file_type: Literal[
      'backDocument',
      'frontDocument',
      'selfie',
      'livenessFrontDocument',
      'livenessBackDocument',
      'livenessSelfie',
    ],
    sub_account_id: str,
    validate: bool | None = None,
  ) -> str:
    """Download an identity file of a subaccount

    Args:
      identity_file_type: The identity file type to download
      sub_account_id: The identifier of the subaccount
      validate: Whether to validate the response against the expected schema.

    References:
      - [Bit2Me API docs](https://api.bit2me.com/doc#tag/kyc/GET/v1/verifier/subaccount/file)
    """
    params: dict = {
      'identityFileType': identity_file_type,
      'subAccountId': sub_account_id,
    }
    return await self.authed_request(
      'GET',
      '/v1/verifier/subaccount/file',
      params=params,
      validator=validate_response,
      validate=validate,
    )
