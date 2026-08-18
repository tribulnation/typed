from functools import cached_property

from binance.core.endpoint.rpc import RpcEndpoint
from .auto_subscribe import AutoSubscribe
from .history import History
from .list import List
from .personal_left_quota import PersonalLeftQuota
from .position import Position
from .redeem import Redeem
from .subscribe import Subscribe
from .subscription_preview import SubscriptionPreview


class Flexible(RpcEndpoint):
  """Binance flexible endpoints."""

  @cached_property
  def auto_subscribe(self) -> AutoSubscribe:
    return AutoSubscribe(client=self.client)

  @cached_property
  def history(self) -> History:
    return History(client=self.client)

  @cached_property
  def list(self) -> List:
    return List(client=self.client)

  @cached_property
  def personal_left_quota(self) -> PersonalLeftQuota:
    return PersonalLeftQuota(client=self.client)

  @cached_property
  def position(self) -> Position:
    return Position(client=self.client)

  @cached_property
  def redeem(self) -> Redeem:
    return Redeem(client=self.client)

  @cached_property
  def subscribe(self) -> Subscribe:
    return Subscribe(client=self.client)

  @cached_property
  def subscription_preview(self) -> SubscriptionPreview:
    return SubscriptionPreview(client=self.client)
