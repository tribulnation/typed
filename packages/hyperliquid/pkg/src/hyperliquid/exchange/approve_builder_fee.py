from typing_extensions import Literal
from typed_core.validation import TypedDict
import pydantic

from hyperliquid.core import timestamp
from hyperliquid.exchange.core import (
  ExchangeMixin,
  ExchangeResponse,
  sign_user_signed_action,
)


class ApproveBuilderFeeAction(TypedDict):
  type: Literal['approveBuilderFee']
  maxFeeRate: str
  builder: str
  signatureChainId: str
  nonce: int


class ApproveBuilderFeeResult(TypedDict):
  type: Literal['default']
  """Response discriminator. Hyperliquid returns the generic `default` marker for this action rather than its own action type name."""


adapter = pydantic.TypeAdapter(ExchangeResponse[ApproveBuilderFeeResult])


class ApproveBuilderFee(ExchangeMixin):
  async def approve_builder_fee(
    self,
    *,
    max_fee_rate: str,
    builder: str,
    signature_chain_id: str,
    nonce: int | None = None,
  ) -> ExchangeResponse[ApproveBuilderFeeResult]:
    """Approve a maximum fee rate for a builder through Hyperliquid POST /exchange using the user-signed `approveBuilderFee` action.

    Args:
      max_fee_rate: Maximum builder fee rate to approve, as a percent string (e.g. "0.001%").
      builder: Builder address, 42-character hexadecimal.
      signature_chain_id: Hex-encoded chain id used when signing the action, e.g. "0xa4b1" for Arbitrum.
      nonce: Optional action nonce. Defaults to the current timestamp.

    References:
      - [Official docs](https://hyperliquid.gitbook.io/hyperliquid-docs/for-developers/api/exchange-endpoint)
    """
    ts = timestamp.now() if nonce is None else nonce
    action: ApproveBuilderFeeAction = {
      'type': 'approveBuilderFee',
      'nonce': ts,
      'maxFeeRate': max_fee_rate,
      'builder': builder,
      'signatureChainId': signature_chain_id,
    }
    signed_action, sig = sign_user_signed_action(
      action,
      wallet=self.wallet,
      payload_types=[
        {'name': 'hyperliquidChain', 'type': 'string'},
        {'name': 'maxFeeRate', 'type': 'string'},
        {'name': 'builder', 'type': 'string'},
        {'name': 'nonce', 'type': 'uint64'},
      ],
      primary_type='HyperliquidTransaction:ApproveBuilderFee',
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
