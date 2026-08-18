from decimal import Decimal
from bit2me.core.endpoint import RpcEndpoint
from typed_core.validation import validator

validate_response = validator(list[Decimal])


class Conversion(RpcEndpoint):
  async def conversion(
    self,
    *,
    from_: str,
    to: str,
    value: str,
    time: str,
    validate: bool | None = None,
  ) -> list[Decimal]:
    """Convert the specified amounts to the specified currency

    Args:
      from_: Comma delimited list of base currencies (can be just one in order to use the same currency base for all convertions)
      to: The target currency
      value: Comma delimited list of values (number of values must be equal to number of times)
      time: Comma delimited list of times (ISO 8601 or epoch) (number of times must be equal to number of values)
      validate: Whether to validate the response against the expected schema.

    References:
      - [Bit2Me API docs](https://api.bit2me.com/doc#tag/market/GET/v1/currency/convert)
    """
    params: dict = {
      'from': from_,
      'to': to,
      'value': value,
      'time': time,
    }
    return await self.authed_request(
      'GET',
      '/v1/currency/convert',
      params=params,
      validator=validate_response,
      validate=validate,
    )
