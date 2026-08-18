from typing_extensions import NotRequired, TypedDict
from typed_core.validation import validator
from binance.core.endpoint.rpc import RpcEndpoint


class WbethWrapResult(TypedDict):
  """Result of a BETH-to-WBETH wrap."""

  success: NotRequired[bool]
  """Whether the wrap succeeded."""
  wbethAmount: NotRequired[str]
  """Amount of WBETH received, as a decimal string."""
  exchangeRate: NotRequired[str]
  """BETH/WBETH exchange rate applied to this wrap, as a decimal string."""


class Wrap(RpcEndpoint):
  """Wrap BETH into WBETH."""

  async def __call__(
    self, *, amount: float, validate: bool | None = None
  ) -> WbethWrapResult:
    """Wrap BETH into WBETH.

    Args:
      amount: Amount of BETH to wrap. Limited to 4 decimal places.

    References:
      - [Official docs](https://developers.binance.com/en/docs/catalog/investment-and-services-staking/api/rest-api/eth-staking#wrap-beth)
    """
    params: dict = {
      'amount': amount,
    }
    _Response = WbethWrapResult
    _validator = validator[_Response](_Response)
    return await self.authed_request(
      'POST',
      '/sapi/v1/eth-staking/wbeth/wrap',
      params=params,
      validator=_validator,
      validate=validate,
    )
