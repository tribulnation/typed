from typing_extensions import Literal, NotRequired
from typed_core.validation import TypedDict
import pydantic

from hyperliquid.core import timestamp
from hyperliquid.exchange.core import ExchangeMixin, ExchangeResponse, sign_l1_action


class ReserveRequestWeightAction(TypedDict):
  type: Literal['reserveRequestWeight']
  weight: int
  destination: NotRequired[str | None]


class ReserveRequestWeightActionResult(TypedDict):
  """Result of an accepted reserve-request-weight action."""

  type: Literal['default']
  """Discriminator confirming this is a reserve-request-weight result. The venue carries no further data alongside it."""


adapter = pydantic.TypeAdapter(ExchangeResponse[ReserveRequestWeightActionResult])


class ReserveRequestWeight(ExchangeMixin):
  async def reserve_request_weight(
    self,
    *,
    weight: int,
    destination: str | None | None = None,
    expires_after: int | None = None,
  ) -> ExchangeResponse[ReserveRequestWeightActionResult]:
    """Reserve additional address-based rate-limit weight for 0.0005 USDC per request, debited from the Perps balance, through Hyperliquid POST /exchange using action type `reserveRequestWeight`. An alternative to trading volume for increasing address-based rate limits.

    Args:
      weight: Additional request weight to reserve, at 0.0005 USDC per unit of weight.
      destination: Address to pay for another user's reserved weight; that user must already exist. Omit or set null to reserve weight for the caller's own address -- omitted fields are skipped in request hashing.
      expires_after: Optional expiration timestamp for the signed action.

    References:
      - [Official docs](https://hyperliquid.gitbook.io/hyperliquid-docs/for-developers/api/exchange-endpoint)
    """
    ts = timestamp.now()
    action: ReserveRequestWeightAction = {
      'type': 'reserveRequestWeight',
      'weight': weight,
    }
    if destination is not None:
      action['destination'] = destination
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
