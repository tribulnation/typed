from typing_extensions import NotRequired, TypedDict
from bit2me.types import CreatedResourceIdResponse
from bit2me.core.endpoint import RpcEndpoint
from typed_core.validation import validator


class ExecuteWalletTransactionRequest(TypedDict):
  proforma: str
  concept: NotRequired[str]
  note: NotRequired[str]


validate_response = validator(CreatedResourceIdResponse)


class Execute(RpcEndpoint):
  async def execute(
    self,
    execute_wallet_transaction_request: ExecuteWalletTransactionRequest,
    *,
    validate: bool | None = None,
  ) -> CreatedResourceIdResponse:
    """Executes a previuosly created transaction

    Args:
      execute_wallet_transaction_request: The proforma transaction id to execute, plus optional concept/note overrides.
      validate: Whether to validate the response against the expected schema.

    References:
      - [Bit2Me API docs](https://api.bit2me.com/doc#tag/wallet/POST/v1/wallet/transaction)
    """
    return await self.authed_request(
      'POST',
      '/v1/wallet/transaction',
      json=execute_wallet_transaction_request,
      validator=validate_response,
      validate=validate,
    )
