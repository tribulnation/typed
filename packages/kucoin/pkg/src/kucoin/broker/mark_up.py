"""`GET /api/v1/broker/nd/mark-up` — Get Mark Up Fee."""

from typed_core.validation import TypedDict, validator
from kucoin.core import RpcEndpoint


class MarkUpFeeDefaultConfig(TypedDict):
  """The broker's account-wide default mark-up fee."""

  spotMakerMarkUp: str
  """Spot maker mark-up; empty string when unset."""
  spotTakerMarkUp: str
  """Spot taker mark-up; empty string when unset."""
  futuresMakerMarkUp: str
  """Futures maker mark-up; empty string when unset."""
  futuresTakerMarkUp: str
  """Futures taker mark-up; empty string when unset."""
  updatedAt: int
  """Time this configuration was last updated, Unix milliseconds."""


class MarkUpFeeItem(TypedDict):
  """One sub-account UID's mark-up fee override."""

  uid: int
  """Sub-account UID."""
  spotMakerMarkUp: str
  """Spot maker mark-up; empty string when unset."""
  spotTakerMarkUp: str
  """Spot taker mark-up; empty string when unset."""
  futuresMakerMarkUp: str
  """Futures maker mark-up; empty string when unset."""
  futuresTakerMarkUp: str
  """Futures taker mark-up; empty string when unset."""
  updatedAt: int
  """Time this UID's override was last updated, Unix milliseconds."""


class MarkUpFeeConfig(TypedDict):
  """The broker's default mark-up plus any per-UID overrides looked up."""

  defaultMarkUp: MarkUpFeeDefaultConfig
  items: list[MarkUpFeeItem]
  """Per-UID mark-up overrides for the `subUids` looked up, sorted by UID ascending. Empty when `subUids` was omitted or every UID given was invalid."""


_Type = MarkUpFeeConfig
adapter = validator[_Type](_Type)  # type: ignore


class MarkUp(RpcEndpoint):
  """`Get Mark Up Fee` — mixed into `Broker`, the product exposing `broker.mark_up`."""

  async def mark_up(
    self,
    *,
    sub_uids: str | None = None,
    validate: bool | None = None,
  ) -> MarkUpFeeConfig:
    """Get the Exchange (ND) Broker's current mark-up fee configuration: the account-wide default, and (optionally) the per-UID overrides for a given list of sub-account UIDs. `items` is empty when `subUids` is omitted or every UID given is invalid.

    Args:
      sub_uids: Sub-account UIDs to look up, up to 20, comma-separated (e.g. `200674083,200675142`). KuCoin's docs type this field a single `integer`, which the comma-joined example contradicts -- typed `string` here to match the wire value a multi-UID query actually sends. See `spec/status.md`'s flagged `client-core` comma-encoding issue: `HttpRpcClient.authed_request` historically percent-encoded `,` before signing, which KuCoin's signing scheme rejects, and this parameter would trip the same bug once called with more than one UID.
      validate: Validate the response against the generated schema.

    References:
      - [KuCoin API docs](https://www.kucoin.com/docs-new)
    """
    params = {}
    if sub_uids is not None:
      params['subUids'] = sub_uids
    return await self.authed_request(
      'GET',
      '/api/v1/broker/nd/mark-up',
      params=params,
      validator=adapter,
      validate=validate,
    )
