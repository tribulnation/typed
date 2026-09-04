from typing_extensions import Any
from dataclasses import dataclass

from typed_core.util import StreamManager
from typed_mexc.spot.streams.core import SpotStreamsEndpoint
from typed_mexc.spot.streams.core.proto import PrivateAccountV3Api


@dataclass(kw_only=True, frozen=True)
class Account(SpotStreamsEndpoint):
  def account(self) -> StreamManager[PrivateAccountV3Api, Any, Any]:
    """Subscribe to the caller's own spot account balance updates. Requires a listen
    key -- authenticated over the private connection (`spot.streams.user`).

    References:
      - [MEXC API docs](https://www.mexc.com/api-docs/spot-v3/websocket-user-data-streams/spot-account-update)
    """
    return self.subscribe('spot@private.account.v3.api.pb', meta={'proto_field': 'private_account'})
