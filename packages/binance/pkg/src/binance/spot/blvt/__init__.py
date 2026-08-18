from .redeem import Redeem
from .redeem_record import RedeemRecord
from .subscribe import Subscribe
from .subscribe_record import SubscribeRecord
from .token_info import TokenInfo
from .user_limit import UserLimit


class Blvt(Redeem, RedeemRecord, Subscribe, SubscribeRecord, TokenInfo, UserLimit):
  """Binance blvt endpoints."""
