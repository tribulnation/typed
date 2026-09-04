from typing_extensions import Any
from dataclasses import dataclass

from typed_core.util import StreamManager
from typed_mexc.spot.streams.core import SpotStreamsEndpoint
from typed_mexc.spot.streams.core.proto import PrivateDealsV3Api


@dataclass(kw_only=True, frozen=True)
class Trades(SpotStreamsEndpoint):
  def trades(self) -> StreamManager[PrivateDealsV3Api, Any, Any]:
    """Subscribe to the caller's own spot trade (deal) updates. Requires a listen key
    -- authenticated over the private connection (`spot.streams.user`).

    References:
      - [MEXC API docs](https://www.mexc.com/api-docs/spot-v3/websocket-user-data-streams/spot-account-deals)
    """
    return self.subscribe('spot@private.deals.v3.api.pb', meta={'proto_field': 'private_deals'})
