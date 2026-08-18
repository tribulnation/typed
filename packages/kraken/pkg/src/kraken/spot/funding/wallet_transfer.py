"""`spot.funding.wallet_transfer` -- private Spot endpoint."""

from typing_extensions import Literal
from typed_core.validation import TypedDict, validator
from ...core.endpoint.rpc import RpcEndpoint


class WalletTransferReceipt(TypedDict):
  """Reference to the created wallet transfer."""

  refid: str
  """Reference ID."""


validate_wallet_transfer = validator(WalletTransferReceipt)


class WalletTransfer(RpcEndpoint):
  """`spot.funding.wallet_transfer`."""

  async def wallet_transfer(
    self,
    *,
    asset: str,
    from_: Literal['Spot Wallet'],
    to: Literal['Futures Wallet'],
    amount: str,
  ) -> WalletTransferReceipt:
    """Transfer from a Kraken Spot wallet to a Kraken Futures wallet. A transfer in the other direction must be requested via the Kraken Futures API withdrawal-to-Spot-wallet endpoint instead. Requires the `Funds permissions - Query` API key permission.

    Args:
      asset: Asset to transfer (asset ID or `altname`).
      from_: Source wallet.
      to: Destination wallet.
      amount: Amount to transfer.

    References:
      - [Official docs](https://docs.kraken.com/api-reference/funding/request-wallet-transfer)
    """
    data: dict = {
      'asset': asset,
      'from': from_,
      'to': to,
      'amount': amount,
    }

    return await self.authed_request(
      '/0/private/WalletTransfer', data, validator=validate_wallet_transfer
    )
