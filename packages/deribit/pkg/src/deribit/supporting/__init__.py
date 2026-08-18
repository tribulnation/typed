from .get_time import GetTime
from .hello import Hello
from .status import Status
from .test import Test


class Supporting(
  GetTime,
  Hello,
  Status,
  Test,
):
  """Supporting endpoints."""
