"""`private/set_disabled_trading_products` — `private/set_disabled_trading_products`."""

from typing_extensions import Literal
from typed_core.validation import validator
from deribit.core import RpcEndpoint

validate_set_disabled_trading_products = validator[Literal['ok']](Literal['ok'])  # pyright: ignore[reportArgumentType]  # fmt: skip


class SetDisabledTradingProducts(RpcEndpoint):
  """`private/set_disabled_trading_products`."""

  async def set_disabled_trading_products(
    self,
    *,
    user_id: int,
    trading_products: list[
      Literal[
        'perpetual', 'futures', 'options', 'future_combos', 'option_combos', 'spots'
      ]
    ],
    validate: bool | None = None,
  ) -> Literal['ok']:
    """Configures which trading products are disabled for a (sub)account -- disabled products cannot be traded by that account. Intended for risk management and compliance restrictions on subaccounts. Requires two-factor authentication on the calling session.

    Args:
      user_id: Id of the (sub)account to configure.
      trading_products: Trading products to disable for the account. Confirmed live that the bare repeated-key encoding this client sends is refused (`value must be a list`); a `trading_products[]` bracket-suffixed key is required -- see this endpoint's `unverified` detail.
      validate: Validate the response against the generated schema.

    References:
      - [Deribit API docs](https://docs.deribit.com/api-reference/account-management/private-set_disabled_trading_products)
    """
    params: dict = {
      'user_id': user_id,
      'trading_products': trading_products,
    }
    return await self.authed_request(
      'private/set_disabled_trading_products',
      params=params,
      validator=validate_set_disabled_trading_products,
      validate=validate,
    )
