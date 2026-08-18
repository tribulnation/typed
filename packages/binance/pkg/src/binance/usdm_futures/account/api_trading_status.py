from typing_extensions import NotRequired, TypedDict
from typed_core.validation import validator
from binance.core.endpoint.rpc import RpcEndpoint


class UsdMFuturesQuantitativeAccountIndicatorEntry(TypedDict):
  """A single account-wide quantitative-rules indicator reading, triggered by violations across multiple symbols."""

  indicator: NotRequired[str]
  """Indicator code. Not documented as an exhaustive enum."""
  value: NotRequired[int]
  """Current value of this indicator."""
  triggerValue: NotRequired[int]
  """Threshold value that triggers an account-wide violation."""
  plannedRecoverTime: NotRequired[int]
  """Millisecond epoch timestamp when the lock is planned to lift."""
  isLocked: NotRequired[bool]
  """Whether trading on this account is currently locked due to a violation."""


class UsdMFuturesQuantitativeIndicatorEntryBtcusdtItem(TypedDict):
  """A single quantitative-rules indicator reading for one symbol."""

  isLocked: NotRequired[bool]
  """Whether trading on this symbol is currently locked due to a violation."""
  plannedRecoverTime: NotRequired[int]
  """Millisecond epoch timestamp when the lock is planned to lift."""
  indicator: NotRequired[str]
  """Indicator code, e.g. GCR (GTC cancel ratio), IFER (IOC/FOK expiration ratio), UFR (unfilled ratio), or DR (dropped ratio). Not documented as an exhaustive enum."""
  value: NotRequired[float]
  """Current value of this indicator."""
  triggerValue: NotRequired[float]
  """Threshold value that triggers a violation for this indicator."""


class UsdMFuturesQuantitativeIndicatorEntryEthusdtItem(TypedDict):
  """A single quantitative-rules indicator reading for one symbol."""

  isLocked: NotRequired[bool]
  """Whether trading on this symbol is currently locked due to a violation."""
  plannedRecoverTime: NotRequired[int]
  """Millisecond epoch timestamp when the lock is planned to lift."""
  indicator: NotRequired[str]
  """Indicator code, e.g. GCR (GTC cancel ratio), IFER (IOC/FOK expiration ratio), UFR (unfilled ratio), or DR (dropped ratio). Not documented as an exhaustive enum."""
  value: NotRequired[float]
  """Current value of this indicator."""
  triggerValue: NotRequired[float]
  """Threshold value that triggers a violation for this indicator."""


class UsdMFuturesQuantitativeIndicators(TypedDict):
  """Per-symbol and account-level indicator values, keyed by symbol (or `ACCOUNT` for the account-wide bucket). Only symbols/buckets with an active or recent violation are present."""

  BTCUSDT: NotRequired[list[UsdMFuturesQuantitativeIndicatorEntryBtcusdtItem]]
  """Indicator values for BTCUSDT."""
  ETHUSDT: NotRequired[list[UsdMFuturesQuantitativeIndicatorEntryEthusdtItem]]
  """Indicator values for ETHUSDT."""
  ACCOUNT: NotRequired[list[UsdMFuturesQuantitativeAccountIndicatorEntry]]
  """Account-wide indicator values, triggered when too many symbols individually violate the rules."""


class UsdMFuturesApiTradingStatus(TypedDict):
  """Futures trading quantitative rules indicators for this account."""

  indicators: NotRequired[UsdMFuturesQuantitativeIndicators]
  updateTime: NotRequired[int]
  """Millisecond epoch timestamp this snapshot was computed."""


class ApiTradingStatus(RpcEndpoint):
  """Futures trading quantitative rules indicators. See [Futures Trading Quantitative Rules](https://www.binance.com/en/support/faq/4f462ebe6ff445d4a170be7d9e897272) for background on what these indicators measure and how a violation is resolved."""

  async def api_trading_status(
    self,
    *,
    symbol: str | None = None,
    validate: bool | None = None,
  ) -> UsdMFuturesApiTradingStatus:
    """Futures trading quantitative rules indicators. See [Futures Trading Quantitative Rules](https://www.binance.com/en/support/faq/4f462ebe6ff445d4a170be7d9e897272) for background on what these indicators measure and how a violation is resolved.

    Args:
      symbol: Symbol to query indicators for. Weight is 1 with a symbol, 10 without.

    References:
      - [Official docs](https://developers.binance.com/en/docs/catalog/core-trading-derivatives-trading-usd-s-m-futures/api/rest-api/account#futures-trading-quantitative-rules-indicators)
    """
    params = {}
    if symbol is not None:
      params['symbol'] = symbol
    _Response = UsdMFuturesApiTradingStatus
    _validator = validator[_Response](_Response)
    return await self.authed_request(
      'GET',
      '/fapi/v1/apiTradingStatus',
      params=params,
      validator=_validator,
      validate=validate,
    )
