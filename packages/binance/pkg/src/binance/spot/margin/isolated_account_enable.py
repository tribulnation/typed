from typing_extensions import TypedDict
from typed_core.validation import validator
from binance.core.endpoint.rpc import RpcEndpoint


class IsolatedMarginAccountStatus(TypedDict):
  """Result of enabling or disabling an isolated margin account."""

  success: bool
  """Whether the operation succeeded."""
  symbol: str
  """Isolated margin trading symbol the operation applied to."""


class IsolatedAccountEnable(RpcEndpoint):
  """Enable an isolated margin account for a specific symbol."""

  async def isolated_account_enable(
    self,
    *,
    symbol: str,
    validate: bool | None = None,
  ) -> IsolatedMarginAccountStatus:
    """Enable an isolated margin account for a specific symbol.

    Args:
      symbol: Isolated margin trading symbol to enable, e.g. BNBUSDT.

    References:
      - [Official docs](https://developers.binance.com/en/docs/catalog/core-trading-margin-trading/api/rest-api/account#enable-isolated-margin-account)
    """
    params: dict = {
      'symbol': symbol,
    }
    _Response = IsolatedMarginAccountStatus
    _validator = validator[_Response](_Response)
    return await self.authed_request(
      'POST',
      '/sapi/v1/margin/isolated/account',
      params=params,
      validator=_validator,
      validate=validate,
    )
