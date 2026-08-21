from .account import Account
from .account_info import AccountInfo
from .accounts import Accounts

from typed_dydx.chain.core import GrpcEndpoint


class Auth(
  Account,
  AccountInfo,
  Accounts,
  GrpcEndpoint,
):
  """Auth endpoints."""
