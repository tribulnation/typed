from typing_extensions import Literal, NotRequired
from typed_core.validation import TypedDict
import pydantic

from hyperliquid.core import timestamp
from hyperliquid.exchange.core import (
  ExchangeMixin,
  ExchangeResponse,
  sign_user_signed_action,
)


class UsdClassTransferAction(TypedDict):
  type: Literal['usdClassTransfer']
  amount: str
  toPerp: bool
  signatureChainId: str
  subaccount: NotRequired[str]
  nonce: int


class UsdClassTransferResult(TypedDict):
  type: Literal['default']
  """Response discriminator. Hyperliquid returns the generic `default` marker for this action rather than its own action type name."""


adapter = pydantic.TypeAdapter(ExchangeResponse[UsdClassTransferResult])


class UsdClassTransfer(ExchangeMixin):
  async def usd_class_transfer(
    self,
    *,
    amount: str,
    to_perp: bool,
    signature_chain_id: str,
    subaccount: str | None = None,
    nonce: int | None = None,
  ) -> ExchangeResponse[UsdClassTransferResult]:
    """Transfer USDC from the user's spot wallet to their perp wallet, or vice versa, through Hyperliquid POST /exchange using the user-signed `usdClassTransfer` action.

    Args:
      amount: USDC amount to transfer, as a decimal string (e.g. "1" for 1 USDC).
      to_perp: Whether to transfer from the spot wallet to the perp wallet (`true`), or from perp to spot (`false`).
      signature_chain_id: Hex-encoded chain id used when signing the action, e.g. "0xa4b1" for Arbitrum.
      subaccount: Optional subaccount address to transfer for, instead of the caller's own account.
      nonce: Optional action nonce. Defaults to the current timestamp.

    References:
      - [Official docs](https://hyperliquid.gitbook.io/hyperliquid-docs/for-developers/api/exchange-endpoint)
    """
    ts = timestamp.now() if nonce is None else nonce
    action: UsdClassTransferAction = {
      'type': 'usdClassTransfer',
      'nonce': ts,
      'amount': amount,
      'toPerp': to_perp,
      'signatureChainId': signature_chain_id,
    }
    if subaccount is not None:
      action['subaccount'] = subaccount
    signed_action, sig = sign_user_signed_action(
      action,
      wallet=self.wallet,
      payload_types=[
        {'name': 'hyperliquidChain', 'type': 'string'},
        {'name': 'amount', 'type': 'string'},
        {'name': 'toPerp', 'type': 'string'},
        {'name': 'subaccount', 'type': 'string'},
        {'name': 'nonce', 'type': 'uint64'},
      ],
      primary_type='HyperliquidTransaction:UsdClassTransfer',
      mainnet=self.mainnet,
    )
    result = await self.client.request(
      {
        'action': signed_action,
        'nonce': ts,
        'signature': sig,
        'vaultAddress': None,
        'expiresAfter': None,
      }
    )
    return adapter.validate_python(result) if self.validate else result
