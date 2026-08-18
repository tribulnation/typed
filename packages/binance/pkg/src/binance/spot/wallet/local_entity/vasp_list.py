from typing_extensions import NotRequired, TypedDict
from typed_core.validation import validator
from binance.core.endpoint.rpc import RpcEndpoint


class LocalEntityVasp(TypedDict):
  """One registered VASP."""

  vaspName: NotRequired[str]
  """VASP legal entity name."""
  vaspCode: NotRequired[str]
  """VASP entity code."""
  identifier: NotRequired[str]
  """Value to use when populating the `vasp` field of a deposit or withdrawal travel rule questionnaire."""


class VaspList(RpcEndpoint):
  """Fetch the VASP (Virtual Asset Service Provider) list for local entities — the registry of counterparty exchanges/entities that can be named when answering a travel rule deposit or withdrawal questionnaire."""

  async def __call__(self, *, validate: bool | None = None) -> list[LocalEntityVasp]:
    """Fetch the VASP (Virtual Asset Service Provider) list for local entities — the registry of counterparty exchanges/entities that can be named when answering a travel rule deposit or withdrawal questionnaire.

    References:
      - [Official docs](https://developers.binance.com/en/docs/catalog/core-trading-wallet/api/rest-api/travel-rule#vasp-list)
    """
    _Response = list[LocalEntityVasp]
    _validator = validator[_Response](_Response)
    return await self.authed_request(
      'GET', '/sapi/v1/localentity/vasp', validator=_validator, validate=validate
    )
