"""`private/verify_block_trade` — `private/verify_block_trade`."""

from typing_extensions import Literal, NotRequired, TypedDict
from typed_core.validation import validator
from deribit.core import RpcEndpoint


class VerifyBlockTradeLeg(TypedDict):
  instrument_name: str
  """Unique instrument identifier"""
  price: float
  """Price for the trade"""
  amount: float
  """It represents the requested trade size. For perpetual and inverse futures the amount is in USD units. For options and linear futures it is the underlying base currency coin."""
  direction: Literal['buy', 'sell']
  """Direction of the trade, from the maker's perspective"""


class VerifyBlockTradeResult(TypedDict):
  signature: str
  """Signature of the block trade, to be shared with the counterparty and submitted to `private/execute_block_trade`. Valid only for 5 minutes around the given `timestamp`."""
  expires_at: NotRequired[int]
  """The timestamp (milliseconds since the Unix epoch) at which the signature expires. Not documented in the upstream OpenAPI spec but present on every live response captured."""


validate_verify_block_trade = validator[VerifyBlockTradeResult](VerifyBlockTradeResult)


class VerifyBlockTrade(RpcEndpoint):
  """`private/verify_block_trade`."""

  async def verify_block_trade(
    self,
    *,
    timestamp: int,
    nonce: str,
    role: Literal['maker', 'taker'],
    trades: list[VerifyBlockTradeLeg],
    validate: bool | None = None,
  ) -> VerifyBlockTradeResult:
    """Verifies and creates a block trade signature. This is the first step in the block trade workflow -- the first party calls this method to generate a signature that must be shared with the second party, who submits it to `private/execute_block_trade`.

    In the API, the `direction` field is always expressed from the maker's perspective: when accepting a block trade as a taker, the direction shown represents the opposite side of the actual trade.

    Scope: `block_trade:read`.

    Args:
      timestamp: Timestamp, shared with other party (milliseconds since the UNIX epoch)
      nonce: Nonce, shared with other party
      role: Describes if user wants to be maker or taker of trades
      trades: List of trades for block trade
      validate: Validate the response against the generated schema.

    References:
      - [Deribit API docs](https://docs.deribit.com/api-reference/block-trade/private-verify_block_trade)
    """
    params: dict = {
      'timestamp': timestamp,
      'nonce': nonce,
      'role': role,
      'trades': trades,
    }
    return await self.authed_request(
      'private/verify_block_trade',
      params=params,
      validator=validate_verify_block_trade,
      validate=validate,
    )
