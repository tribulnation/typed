"""`GET /api/v1/hf/orders/dead-cancel-all/query` — Get DCP."""

from typed_core.validation import TypedDict, validator
from kucoin.core import RpcEndpoint, Timestamp


class HfDcpConfig(TypedDict):
  """Disconnection Protect configuration."""

  timeout: int
  """Seconds of silence before every order on the protected symbols is auto-cancelled."""
  symbols: str
  """Comma-separated trading pair symbols protected by this setting."""
  currentTime: Timestamp
  """Server time at query."""
  triggerTime: Timestamp
  """Time at which the auto-cancellation would trigger, absent another Set DCP call resetting it."""


_Type = HfDcpConfig | None
adapter = validator[_Type](_Type)  # type: ignore


class GetDcp(RpcEndpoint):
  """`Get DCP` — mixed into `OrdersHf`, the product exposing `spot.orders_hf.get_dcp`."""

  async def get_dcp(self, *, validate: bool | None = None) -> HfDcpConfig | None:
    """Get the authenticated account's current Disconnection Protect (DCP, a.k.a. dead-cancel-all / deadman switch) configuration -- the venue's own automatic-cancel-on-disconnect safety setting.

    Args:
      validate: Validate the response against the generated schema.

    References:
      - [KuCoin API docs](https://www.kucoin.com/docs-new)
    """
    return await self.authed_request(
      'GET',
      '/api/v1/hf/orders/dead-cancel-all/query',
      validator=adapter,
      validate=validate,
    )
