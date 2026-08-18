from typing_extensions import TypedDict
from bit2me.types import BooleanResultResponse
from bit2me.core.endpoint import RpcEndpoint
from typed_core.validation import validator


class UpdateTransactionRequest(TypedDict):
  note: str


validate_response = validator(BooleanResultResponse)


class Update(RpcEndpoint):
  async def update(
    self,
    id: str,
    update_transaction_request: UpdateTransactionRequest,
    *,
    validate: bool | None = None,
  ) -> BooleanResultResponse:
    """Updates some data of the specified transaction

    Args:
      id: The transaction id
      update_transaction_request: The new personal note to set on the transaction.
      validate: Whether to validate the response against the expected schema.

    References:
      - [Bit2Me API docs](https://api.bit2me.com/doc#tag/wallet/PUT/v1/wallet/transaction/{id})
    """
    return await self.authed_request(
      'put',
      f'/v1/wallet/transaction/{id}',
      json=update_transaction_request,
      validator=validate_response,
      validate=validate,
    )
