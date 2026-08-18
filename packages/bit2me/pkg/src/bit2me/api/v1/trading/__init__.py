"""Hand-written PoC for the `http` surface's authenticated-endpoint shape.

Stands in for the full generated `v1.trading.*` namespace the codegen revamp will
produce — one representative method (`balance`), per `spec/endpoints/v1/trading/
wallet/balance/endpoint.json`.
"""

from dataclasses import dataclass

from bit2me.core.endpoint import RpcEndpoint
from typed_core.validation import validator
from bit2me.types import WalletResponse

validate_balance = validator(list[WalletResponse])


@dataclass(kw_only=True, frozen=True)
class V1Trading(RpcEndpoint):
  async def balance(
    self, *, symbols: str | None = None, validate: bool | None = None
  ) -> list[WalletResponse]:
    """Retrieve balances of all wallets and blocked balances in active orders.

    Args:
      symbols: Comma-separated symbols of the wallets to retrieve, for example
        `"BTC,EUR"`. Omit to retrieve every wallet.
      validate: Whether to validate the response against the expected schema.

    References:
      - [Bit2Me API docs](https://api.bit2me.com/trading-spot-rest#tag/funding/GET/v1/trading/wallet/balance)
    """
    params = {'symbols': symbols} if symbols is not None else None
    return await self.authed_request(
      'GET',
      '/v1/trading/wallet/balance',
      params=params,
      validator=validate_balance,
      validate=validate,
    )
