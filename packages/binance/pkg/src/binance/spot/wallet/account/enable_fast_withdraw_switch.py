from typing_extensions import Any
from typed_core.validation import validator
from binance.core.endpoint.rpc import RpcEndpoint


class EnableFastWithdrawSwitch(RpcEndpoint):
  """Enable the account's Fast Withdraw Switch. Requires the API key used to have the "trade" permission enabled. When enabled, transfers to a Binance account complete instantly with no on-chain transaction, transaction id, or withdrawal fee."""

  async def enable_fast_withdraw_switch(
    self,
    *,
    validate: bool | None = None,
  ) -> dict[str, Any]:
    """Enable the account's Fast Withdraw Switch. Requires the API key used to have the "trade" permission enabled. When enabled, transfers to a Binance account complete instantly with no on-chain transaction, transaction id, or withdrawal fee.

    References:
      - [Official docs](https://developers.binance.com/en/docs/catalog/core-trading-wallet/api/rest-api/account#enable-fast-withdraw-switch)
    """
    _Response = dict[str, Any]
    _validator = validator[_Response](_Response)
    return await self.authed_request(
      'POST',
      '/sapi/v1/account/enableFastWithdrawSwitch',
      validator=_validator,
      validate=validate,
    )
