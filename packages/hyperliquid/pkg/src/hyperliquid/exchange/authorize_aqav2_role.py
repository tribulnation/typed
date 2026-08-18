from typing_extensions import Literal
from typed_core.validation import TypedDict
import pydantic

from hyperliquid.core import timestamp
from hyperliquid.exchange.core import ExchangeMixin, ExchangeResponse, sign_l1_action


class AuthorizeAqav2roleAction(TypedDict):
  type: Literal['authorizeAqav2Role']
  token: int
  role: Literal['technical', 'treasury']


class AuthorizeAqav2roleResult(TypedDict):
  type: Literal['default']
  """Response discriminator. Hyperliquid returns the generic `default` marker for this action rather than its own action type name."""


adapter = pydantic.TypeAdapter(ExchangeResponse[AuthorizeAqav2roleResult])


class AuthorizeAqav2Role(ExchangeMixin):
  async def authorize_aqav2_role(
    self,
    *,
    token: int,
    role: Literal['technical', 'treasury'],
    expires_after: int | None = None,
  ) -> ExchangeResponse[AuthorizeAqav2roleResult]:
    """Grant a `technical` or `treasury` role for a token's Aligned Quote Asset v2 (AQAv2) governance, through Hyperliquid POST /exchange using the L1 `authorizeAqav2Role` action.

    Args:
      token: Token index the role applies to, e.g. `0` for USDC.
      role: AQAv2 governance role to grant.
      expires_after: Optional expiration timestamp for the signed action.

    References:
      - [Official docs](https://hyperliquid.gitbook.io/hyperliquid-docs/for-developers/api/exchange-endpoint)
    """
    ts = timestamp.now()
    action: AuthorizeAqav2roleAction = {
      'type': 'authorizeAqav2Role',
      'token': token,
      'role': role,
    }
    sig = sign_l1_action(
      action,
      wallet=self.wallet,
      nonce=ts,
      mainnet=self.mainnet,
      vault_address=None,
      expires_after=expires_after,
    )
    result = await self.client.request(
      {
        'action': action,
        'nonce': ts,
        'signature': sig,
        'vaultAddress': None,
        'expiresAfter': expires_after,
      }
    )
    return adapter.validate_python(result) if self.validate else result
