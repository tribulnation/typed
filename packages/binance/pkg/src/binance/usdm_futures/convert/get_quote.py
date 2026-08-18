from typing_extensions import Literal, NotRequired, TypedDict
from typed_core.validation import validator
from binance.core.endpoint.rpc import RpcEndpoint


class UsdMFuturesConvertQuote(TypedDict):
  """A quote for a token pair conversion."""

  quoteId: NotRequired[str]
  """Quote identifier. Returned only if this account has enough funds to convert. Pass to `usdm_futures.convert.accept_quote` to execute the trade."""
  ratio: NotRequired[str]
  """Conversion ratio, `toAmount` / `fromAmount`."""
  inverseRatio: NotRequired[str]
  """Inverse conversion ratio, `fromAmount` / `toAmount`."""
  validTimestamp: NotRequired[int]
  """Millisecond epoch timestamp after which the quote can no longer be accepted."""
  toAmount: NotRequired[str]
  """Amount that would be credited to `toAsset`."""
  fromAmount: NotRequired[str]
  """Amount that would be debited from `fromAsset`."""


class GetQuote(RpcEndpoint):
  """Request a quote for a token pair conversion. The returned `quoteId` is accepted by `usdm_futures.convert.accept_quote` to execute the trade."""

  async def get_quote(
    self,
    *,
    from_asset: str,
    to_asset: str,
    from_amount: float | None = None,
    to_amount: float | None = None,
    valid_time: Literal['10s', '30s', '1m'] | None = None,
    validate: bool | None = None,
  ) -> UsdMFuturesConvertQuote:
    """Request a quote for a token pair conversion. The returned `quoteId` is accepted by `usdm_futures.convert.accept_quote` to execute the trade.

    Args:
      from_asset: Asset the user would spend.
      to_asset: Asset the user would receive.
      from_amount: Amount debited after the conversion. Either this or `toAmount` should be sent.
      to_amount: Amount credited after the conversion. Either this or `fromAmount` should be sent.
      valid_time: How long the returned quote stays acceptable.

    References:
      - [Official docs](https://developers.binance.com/en/docs/catalog/core-trading-derivatives-trading-usd-s-m-futures/api/rest-api/convert#send-quote-request)
    """
    params: dict = {
      'fromAsset': from_asset,
      'toAsset': to_asset,
    }
    if from_amount is not None:
      params['fromAmount'] = from_amount
    if to_amount is not None:
      params['toAmount'] = to_amount
    if valid_time is not None:
      params['validTime'] = valid_time
    _Response = UsdMFuturesConvertQuote
    _validator = validator[_Response](_Response)
    return await self.authed_request(
      'POST',
      '/fapi/v1/convert/getQuote',
      params=params,
      validator=_validator,
      validate=validate,
    )
