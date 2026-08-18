from typing_extensions import TypedDict
from typed_core.validation import validator
from binance.core import Timestamp
from binance.core.endpoint.rpc import RpcEndpoint


class CoinMBalance(TypedDict):
  """Balance detail for one settlement asset (e.g. BTC, ETH). All monetary fields are denominated in this asset, not USDT."""

  accountAlias: str
  """Unique account code."""
  asset: str
  """Asset symbol."""
  balance: str
  """Account balance, in this asset."""
  withdrawAvailable: str
  """Amount available for withdrawal, in this asset."""
  crossWalletBalance: str
  """Wallet balance for crossed margin, in this asset."""
  crossUnPnl: str
  """Total unrealized profit or loss of crossed positions, in this asset."""
  availableBalance: str
  """Available margin balance, in this asset."""
  updateTime: Timestamp
  """Time this balance was last updated."""


class Balance(RpcEndpoint):
  """Check COIN-M Futures account balance, one entry per settlement asset held by this account."""

  async def balance(self, *, validate: bool | None = None) -> list[CoinMBalance]:
    """Check COIN-M Futures account balance, one entry per settlement asset held by this account.

    References:
      - [Official docs](https://developers.binance.com/en/docs/catalog/core-trading-derivatives-trading-coin-m-futures/api/rest-api/account#futures-account-balance)
    """
    _Response = list[CoinMBalance]
    _validator = validator[_Response](_Response)
    return await self.authed_request(
      'GET', '/dapi/v1/balance', validator=_validator, validate=validate
    )
