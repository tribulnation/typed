from typing_extensions import NotRequired, TypedDict
from typed_core.validation import validator
from binance.core.endpoint.rpc import RpcEndpoint


class MiningAccountHashrateSample(TypedDict):
  """One hashrate sample."""

  time: NotRequired[int]
  """Millisecond epoch sample timestamp."""
  hashrate: NotRequired[str]
  """Hashrate at this sample."""
  reject: NotRequired[str]
  """Rejected-share rate at this sample."""


class MiningAccountHashrateSeries(TypedDict):
  """One hashrate history time series."""

  type: NotRequired[str]
  """Hashrate series type, e.g. H_hashrate."""
  userName: NotRequired[str]
  """Mining account."""
  list: NotRequired[list[MiningAccountHashrateSample]]
  """Hashrate samples over time."""


class MiningAccountListResponse(TypedDict):
  """Account hashrate history response frame. This product line wraps its business data in {code,msg,data} on the wire, and the core does not strip it -- see spec/core.md's Envelope section."""

  code: NotRequired[int]
  """Response code. 0 indicates success."""
  msg: NotRequired[str]
  """Response message."""
  data: NotRequired[list[MiningAccountHashrateSeries]]
  """Hashrate history series, one entry per series type."""


class AccountList(RpcEndpoint):
  """Query this mining account's hashrate history series."""

  async def account_list(
    self,
    *,
    algo: str,
    user_name: str,
    validate: bool | None = None,
  ) -> MiningAccountListResponse:
    """Query this mining account's hashrate history series.

    Args:
      algo: Mining algorithm name.
      user_name: Mining account.

    References:
      - [Official docs](https://developers.binance.com/docs/mining/rest-api#account-list)
    """
    params: dict = {
      'algo': algo,
      'userName': user_name,
    }
    _Response = MiningAccountListResponse
    _validator = validator[_Response](_Response)
    return await self.authed_request(
      'GET',
      '/sapi/v1/mining/statistics/user/list',
      params=params,
      validator=_validator,
      validate=validate,
    )
