from typing_extensions import NotRequired, TypedDict
from typed_core.validation import validator
from binance.core.endpoint.rpc import RpcEndpoint


class UsdMFuturesOrderRateLimit(TypedDict):
  """A single order rate-limit rule."""

  rateLimitType: NotRequired[str]
  """Rate limit category this rule applies to, e.g. `ORDERS`. Not confirmed as a closed enum in this pass."""
  interval: NotRequired[str]
  """Time unit the limit is measured over, e.g. `MINUTE`. Not confirmed as a closed enum in this pass."""
  intervalNum: NotRequired[int]
  """Number of `interval` units in one window."""
  limit: NotRequired[int]
  """Maximum number of orders allowed within the window."""


class RateLimitOrder(RpcEndpoint):
  """Query this account's current order rate limits."""

  async def rate_limit_order(
    self,
    *,
    validate: bool | None = None,
  ) -> list[UsdMFuturesOrderRateLimit]:
    """Query this account's current order rate limits.

    References:
      - [Official docs](https://developers.binance.com/en/docs/catalog/core-trading-derivatives-trading-usd-s-m-futures/api/rest-api/account#query-user-rate-limit)
    """
    _Response = list[UsdMFuturesOrderRateLimit]
    _validator = validator[_Response](_Response)
    return await self.authed_request(
      'GET', '/fapi/v1/rateLimit/order', validator=_validator, validate=validate
    )
