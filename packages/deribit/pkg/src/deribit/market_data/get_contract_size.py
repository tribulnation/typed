"""`public/get_contract_size` — `public/get_contract_size`."""

from typing_extensions import TypedDict
from typed_core.validation import validator
from deribit.core import RpcEndpoint


class ContractSize(TypedDict):
  """Contract size for one instrument."""

  contract_size: int
  """Contract size, for futures in USD, for options in base currency of the instrument (BTC, ETH, ...)"""


validate_get_contract_size = validator[ContractSize](ContractSize)


class GetContractSize(RpcEndpoint):
  """`public/get_contract_size`."""

  async def get_contract_size(
    self,
    *,
    instrument_name: str,
    validate: bool | None = None,
  ) -> ContractSize:
    """Retrieves the contract size (also known as contract multiplier) for a given instrument. The contract size determines how many units of the underlying asset one contract represents.

    This value is essential for calculating position values, margin requirements, and P&L calculations. Different instruments may have different contract sizes.

    Args:
      instrument_name: Instrument name
      validate: Validate the response against the generated schema.

    References:
      - [Deribit API docs](https://docs.deribit.com/api-reference/market-data/public-get_contract_size)
    """
    params: dict = {
      'instrument_name': instrument_name,
    }
    return await self.request(
      'public/get_contract_size',
      params=params,
      validator=validate_get_contract_size,
      validate=validate,
    )
