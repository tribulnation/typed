from .authed_unsubscribe_all import AuthedUnsubscribeAll
from .unsubscribe_all import UnsubscribeAll


class SubscriptionManagement(
  AuthedUnsubscribeAll,
  UnsubscribeAll,
):
  """SubscriptionManagement endpoints."""
