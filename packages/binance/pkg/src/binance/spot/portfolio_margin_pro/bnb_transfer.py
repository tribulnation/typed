from typing_extensions import Literal, NotRequired, TypedDict
from typed_core.validation import validator
from binance.core.endpoint.rpc import RpcEndpoint


class PmProBnbTransfer(TypedDict):
  """BNB transfer."""

  tranId: NotRequired[int]
  """Transaction ID."""


class BnbTransfer(RpcEndpoint):
  """BNB Transfer"""

  async def bnb_transfer(
    self,
    *,
    amount: float,
    transfer_side: Literal['TO_UM', 'FROM_UM'],
    validate: bool | None = None,
  ) -> PmProBnbTransfer:
    """BNB transfer can be between Margin Account and USDM Account.

    Args:
      amount: Transfer amount.
      transfer_side: Transfer direction.

    References:
      - [Official docs](https://developers.binance.com/en/docs/catalog/advanced-trading-derivatives-trading-portfolio-margin-pro/api/rest-api/account#bnb-transfer)
    """
    params: dict = {
      'amount': amount,
      'transferSide': transfer_side,
    }
    _Response = PmProBnbTransfer
    _validator = validator[_Response](_Response)
    return await self.authed_request(
      'POST',
      '/sapi/v1/portfolio/bnb-transfer',
      params=params,
      validator=_validator,
      validate=validate,
    )
