"""`GET /api/v1/margin/config` — Get Margin Config."""

from typed_core.validation import TypedDict, validator
from typed_kucoin.core.endpoint.rpc import RpcEndpoint


class MarginConfig(TypedDict):
  """Cross-margin trading configuration."""

  currencyList: list[str]
  """Currencies available for margin trade."""
  maxLeverage: int
  """Maximum leverage available."""
  warningDebtRatio: str
  """Debt ratio at which a forced-liquidation warning is issued."""
  liqDebtRatio: str
  """Debt ratio at which forced liquidation triggers."""


adapter = validator(MarginConfig)


class Config(RpcEndpoint):
  """`Get Margin Config` — mixed into `Margin`, the product exposing `margin.config`."""

  async def config(self, *, validate: bool | None = None) -> MarginConfig:
    """Get the cross-margin trading configuration: eligible currencies, max leverage and
    the debt ratios that trigger a liquidation warning or forced liquidation.

    Args:
      validate: Validate the response against the generated schema.

    References:
      - [KuCoin API docs](https://www.kucoin.com/docs-new)
    """
    return await self.client.request(
      'GET', '/api/v1/margin/config', validator=adapter, validate=validate
    )
