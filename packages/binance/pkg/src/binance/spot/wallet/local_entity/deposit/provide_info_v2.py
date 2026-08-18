from typing_extensions import NotRequired, TypedDict
from typed_core.validation import validator
from binance.core.endpoint.rpc import RpcEndpoint


class DepositQuestionnaireV2submission(TypedDict):
  """Result of submitting a v2 travel rule deposit questionnaire."""

  trId: NotRequired[int]
  """Travel rule record id."""
  accepted: NotRequired[bool]
  """Whether the submitted questionnaire was accepted."""
  info: NotRequired[str]
  """Status message."""


class ProvideInfoV2(RpcEndpoint):
  """Submit a travel rule questionnaire for a pending deposit at a local entity that requires travel rule (v2, addressed by deposit id rather than wallet transaction id). Only applies to deposits from unhosted wallets or VASPs not yet onboarded with GTR (Global Travel Rule)."""

  async def provide_info_v2(
    self,
    *,
    deposit_id: int,
    questionnaire: str,
    validate: bool | None = None,
  ) -> DepositQuestionnaireV2submission:
    """Submit a travel rule questionnaire for a pending deposit at a local entity that requires travel rule (v2, addressed by deposit id rather than wallet transaction id). Only applies to deposits from unhosted wallets or VASPs not yet onboarded with GTR (Global Travel Rule).

    Args:
      deposit_id: Wallet deposit id this questionnaire is for.
      questionnaire: JSON-formatted questionnaire answers, URL-encoded. Contents differ per local entity; see the entity's own Deposit Questionnaire Content page.

    References:
      - [Official docs](https://developers.binance.com/en/docs/catalog/core-trading-wallet/api/rest-api/travel-rule#submit-deposit-questionnaire-v2)
    """
    params: dict = {
      'depositId': deposit_id,
      'questionnaire': questionnaire,
    }
    _Response = DepositQuestionnaireV2submission
    _validator = validator[_Response](_Response)
    return await self.authed_request(
      'PUT',
      '/sapi/v2/localentity/deposit/provide-info',
      params=params,
      validator=_validator,
      validate=validate,
    )
