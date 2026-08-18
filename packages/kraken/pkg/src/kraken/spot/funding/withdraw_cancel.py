"""`spot.funding.withdraw_cancel` -- private Spot endpoint."""

from typed_core.validation import validator
from ...core.endpoint.rpc import RpcEndpoint


validate_withdraw_cancel = validator(bool)


class WithdrawCancel(RpcEndpoint):
  """`spot.funding.withdraw_cancel`."""

  async def withdraw_cancel(self, *, asset: str, refid: str) -> bool:
    """Cancel a recently requested withdrawal, if it has not already been successfully processed. Requires the `Funds permissions - Withdraw` API key permission, unless the withdrawal is a `WalletTransfer`, in which case no permissions are required.

    Args:
      asset: Asset being withdrawn.
      refid: Withdrawal reference ID.

    References:
      - [Official docs](https://docs.kraken.com/api-reference/funding/request-withdrawal-cancellation)
    """
    data: dict = {
      'asset': asset,
      'refid': refid,
    }

    return await self.authed_request(
      '/0/private/WithdrawCancel', data, validator=validate_withdraw_cancel
    )
