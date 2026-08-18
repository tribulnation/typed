"""`private/cancel_by_label` — `private/cancel_by_label`."""

from typing_extensions import Literal
from typed_core.validation import validator
from deribit.core import RpcEndpoint

validate_cancel_by_label = validator[float](float)


class CancelByLabel(RpcEndpoint):
  """`private/cancel_by_label`."""

  async def cancel_by_label(
    self,
    *,
    label: str,
    currency: Literal['BTC', 'ETH', 'USDC', 'USDT', 'EURR'] | None = None,
    validate: bool | None = None,
  ) -> float:
    """Cancels all orders (including trigger orders) that have a specific label. This is useful for managing groups of related orders that share the same label.

    Orders can be cancelled across all currencies or filtered to a specific currency. When cancelling by currency, the currency queue is used for processing.

    **Rate Limits:** When called without the `currency` parameter, this method is subject to `cancel_all` rate limits. Different rate limit values may apply for per-currency cancels versus calls without providing the currency parameter.

    Args:
      label: user defined label for the order (maximum 64 characters)
      currency: The currency symbol
      validate: Validate the response against the generated schema.

    References:
      - [Deribit API docs](https://docs.deribit.com/api-reference/trading/private-cancel_by_label)
    """
    params: dict = {
      'label': label,
    }
    if currency is not None:
      params['currency'] = currency
    return await self.authed_request(
      'private/cancel_by_label',
      params=params,
      validator=validate_cancel_by_label,
      validate=validate,
    )
