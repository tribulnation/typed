from dataclasses import dataclass
from .account import Account
from .trades import Trades
from .orders import Orders

@dataclass
class UserStreams(Account, Trades, Orders):
  ...
