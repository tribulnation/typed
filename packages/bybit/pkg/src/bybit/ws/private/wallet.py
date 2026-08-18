"""`wallet` — Subscribe to authenticated wallet balance updates."""

from typing_extensions import Literal, NotRequired, TypedDict
from bybit.core import validator
from bybit.core.ws import Reply, WsEndpoint
from typed_core.util import StreamManager
from typed_core.ws.streams import Stream


class WalletCoinBalance(TypedDict):
  """One coin's balance within a wallet update."""

  coin: str
  """Coin symbol, for example `USDT`."""
  equity: str
  """Equity, including unrealized PnL."""
  walletBalance: str
  """Wallet balance, excluding unrealized PnL."""
  availableToWithdraw: NotRequired[str]
  """Amount currently free to withdraw."""


class WalletUpdate(TypedDict):
  """One account's wallet balance and margin state after a change."""

  accountType: Literal['UNIFIED', 'CONTRACT', 'SPOT']
  """Account type."""
  totalEquity: NotRequired[str]
  """Total equity across every coin, in USD."""
  totalWalletBalance: NotRequired[str]
  """Total wallet balance across every coin, in USD."""
  coin: list[WalletCoinBalance]
  """Per-coin balances."""


validate_message = validator[list[WalletUpdate]](list[WalletUpdate])


class Wallet(WsEndpoint):
  """Subscribe to authenticated wallet balance updates."""

  def wallet(
    self,
    *,
    validate: bool | None = None,
  ) -> StreamManager[list[WalletUpdate], Reply, Reply]:
    """Stream wallet balance and margin updates for the authenticated account.

    Args:
      validate: Whether to validate pushed payloads against the expected schema.

    Returns:
      A manager for the subscription stream.

    References:
      - [Bybit API docs](https://bybit-exchange.github.io/docs/v5/websocket/private/wallet)
    """
    return StreamManager(lambda: self._wallet_impl(validate=validate))

  async def _wallet_impl(
    self,
    *,
    validate: bool | None = None,
  ) -> Stream[list[WalletUpdate], Reply, Reply]:
    stream = await self.socket.subscribe('wallet')

    async def parsed_stream():
      async for msg in stream:
        yield validate_message(msg) if self.should_validate(validate) else msg

    return Stream(
      reply=stream.reply, stream=parsed_stream(), unsubscribe=stream.unsubscribe
    )
