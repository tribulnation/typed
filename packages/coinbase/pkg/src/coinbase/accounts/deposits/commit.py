from dataclasses import dataclass
from typed_core.validation import validator
from typing_extensions import TypedDict
from coinbase.core.endpoint.rpc import RpcEndpoint
from coinbase.types import V2transfer


class CommitDepositResponse(TypedDict):
  """Wrapper around the committed deposit transfer."""

  transfer: V2transfer


@dataclass(frozen=True, kw_only=True)
class Commit(RpcEndpoint):
  """`POST /v2/accounts/{account_id}/deposits/{deposit_id}/commit`."""

  async def commit(self, account_id: str, deposit_id: str) -> CommitDepositResponse:
    """Complete a deposit that was created with `commit: false`.

    Args:
      account_id: The fiat account the deposit belongs to.
      deposit_id: The deposit to commit.

    References:
      - [Official docs](https://docs.cdp.coinbase.com/coinbase-app/transfer-apis/deposit-fiat)
    """
    return await self.authed_request(
      'POST',
      f'/v2/accounts/{account_id}/deposits/{deposit_id}/commit',
      validator=validator(CommitDepositResponse),
    )
