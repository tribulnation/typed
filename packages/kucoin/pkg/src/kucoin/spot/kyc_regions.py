"""`GET /api/kyc/regions/v4` — Get KYC Regions."""

from typed_core.validation import TypedDict, validator
from kucoin.core import RpcEndpoint


class KycRegion(TypedDict):
  """One country/region KuCoin recognizes for KYC purposes."""

  code: str
  """Two-letter region code, for example `US`."""
  enName: str
  """English name of the region, for example `United States`."""


_Type = list[KycRegion]
adapter = validator[_Type](_Type)  # type: ignore


class KycRegions(RpcEndpoint):
  """`Get KYC Regions` — mixed into `Spot`, the product exposing `spot.kyc_regions`."""

  async def kyc_regions(self, *, validate: bool | None = None) -> list[KycRegion]:
    """Get the list of country/region codes and names KuCoin uses for KYC purposes. Public. Its docs page URL is misleadingly slugged under 'account-info/withdrawals', but the site's own sidebar places it under Spot Trading → Market Data — confirmed live 2026-08-09, and specced here to match.

    Args:
      validate: Validate the response against the generated schema.

    References:
      - [KuCoin API docs](https://www.kucoin.com/docs-new)
    """
    return await self.request(
      'GET',
      '/api/kyc/regions/v4',
      validator=adapter,
      validate=validate,
    )
