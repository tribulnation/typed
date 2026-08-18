from .disable_cancel_on_disconnect import DisableCancelOnDisconnect
from .disable_heartbeat import DisableHeartbeat
from .enable_cancel_on_disconnect import EnableCancelOnDisconnect
from .get_cancel_on_disconnect import GetCancelOnDisconnect
from .set_heartbeat import SetHeartbeat


class Session(
  DisableCancelOnDisconnect,
  DisableHeartbeat,
  EnableCancelOnDisconnect,
  GetCancelOnDisconnect,
  SetHeartbeat,
):
  """Session endpoints."""
