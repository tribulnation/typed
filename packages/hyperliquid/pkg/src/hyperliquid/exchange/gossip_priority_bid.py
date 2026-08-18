from typing_extensions import Literal
from typed_core.validation import TypedDict
import pydantic

from hyperliquid.core import timestamp
from hyperliquid.exchange.core import ExchangeMixin, ExchangeResponse, sign_l1_action


class DefaultActionResult(TypedDict):
  """Success result, following the generic `default` marker every other `/exchange` action documents on success -- not itself shown for `gossipPriorityBid` in the source doc."""

  type: Literal['default']
  """Result discriminator; assumed `default` by analogy to sibling exchange actions."""


class GossipPriorityBidAction(TypedDict):
  type: Literal['gossipPriorityBid']
  slotId: int
  ip: str
  maxGas: int


adapter = pydantic.TypeAdapter(ExchangeResponse[DefaultActionResult])


class GossipPriorityBid(ExchangeMixin):
  async def gossip_priority_bid(
    self,
    *,
    slot_id: int,
    ip: str,
    max_gas: int,
    expires_after: int | None = None,
  ) -> ExchangeResponse[DefaultActionResult]:
    """Bid for a priority-gossip read slot through Hyperliquid POST /exchange using action type `gossipPriorityBid`. Priority gossip slots are auctioned via independent Dutch auctions; `maxGas` is burned from the signer's spot balance in HYPE regardless of whether the bid wins. Current auction winners can be read via the `gossipPriorityAuctionStatus` info request.

    Args:
      slot_id: Priority gossip slot being bid for. The doc's own example shows slot `0`; the total slot count is not documented, and current winners can be read via the `gossipPriorityAuctionStatus` info request.
      ip: IP address to associate with this priority slot if the bid wins, in dotted-quad IPv4 format (e.g. `"1.2.3.4"`).
      max_gas: Maximum gas to bid, in wei (units of `0.00000001` HYPE) charged from the signer's spot balance. Burned regardless of whether the bid wins.
      expires_after: Optional expiration timestamp for the signed action.

    References:
      - [Official docs](https://hyperliquid.gitbook.io/hyperliquid-docs/for-developers/api/priority-fees)
    """
    ts = timestamp.now()
    action: GossipPriorityBidAction = {
      'type': 'gossipPriorityBid',
      'slotId': slot_id,
      'ip': ip,
      'maxGas': max_gas,
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
