from typing_extensions import Literal
from typed_core.validation import TypedDict
import pydantic

from hyperliquid.core import timestamp
from hyperliquid.exchange.core import (
  ExchangeMixin,
  ExchangeResponse,
  sign_user_signed_action,
)


class TokenDelegateAction(TypedDict):
  type: Literal['tokenDelegate']
  validator: str
  isUndelegate: bool
  wei: int
  signatureChainId: str
  nonce: int


class TokenDelegateResult(TypedDict):
  type: Literal['default']
  """Response discriminator. Hyperliquid returns the generic `default` marker for this action rather than its own action type name."""


adapter = pydantic.TypeAdapter(ExchangeResponse[TokenDelegateResult])


class TokenDelegate(ExchangeMixin):
  async def token_delegate(
    self,
    *,
    validator: str,
    is_undelegate: bool,
    wei: int,
    signature_chain_id: str,
    nonce: int | None = None,
  ) -> ExchangeResponse[TokenDelegateResult]:
    """Delegate or undelegate native tokens to or from a validator through Hyperliquid POST /exchange using the user-signed `tokenDelegate` action. Delegations to a particular validator carry a 1-day lockup.

    Args:
      validator: Validator address, 42-character hexadecimal.
      is_undelegate: Whether to undelegate from the validator (`true`) instead of delegating to it (`false`).
      wei: Stake amount to delegate or undelegate, in wei.
      signature_chain_id: Hex-encoded chain id used when signing the action, e.g. "0xa4b1" for Arbitrum.
      nonce: Optional action nonce. Defaults to the current timestamp.

    References:
      - [Official docs](https://hyperliquid.gitbook.io/hyperliquid-docs/for-developers/api/exchange-endpoint)
    """
    ts = timestamp.now() if nonce is None else nonce
    action: TokenDelegateAction = {
      'type': 'tokenDelegate',
      'nonce': ts,
      'validator': validator,
      'isUndelegate': is_undelegate,
      'wei': wei,
      'signatureChainId': signature_chain_id,
    }
    signed_action, sig = sign_user_signed_action(
      action,
      wallet=self.wallet,
      payload_types=[
        {'name': 'hyperliquidChain', 'type': 'string'},
        {'name': 'validator', 'type': 'string'},
        {'name': 'isUndelegate', 'type': 'string'},
        {'name': 'wei', 'type': 'string'},
        {'name': 'nonce', 'type': 'uint64'},
      ],
      primary_type='HyperliquidTransaction:TokenDelegate',
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
