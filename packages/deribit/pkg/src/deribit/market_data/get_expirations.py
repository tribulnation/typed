"""`public/get_expirations` — `public/get_expirations`."""

from typing_extensions import Literal
from typed_core.validation import validator
from deribit.core import RpcEndpoint

validate_get_expirations = validator[dict[str, list[str]] | dict[str, dict[str, list[str]]]](dict[str, list[str]] | dict[str, dict[str, list[str]]])  # pyright: ignore[reportArgumentType]  # fmt: skip


class GetExpirations(RpcEndpoint):
  """`public/get_expirations`."""

  async def get_expirations(
    self,
    *,
    currency: Literal['BTC', 'ETH', 'USDC', 'USDT', 'any', 'grouped'],
    kind: Literal['future', 'option', 'any'],
    currency_pair: Literal[
      'btc_usd',
      'eth_usd',
      'ada_usdc',
      'algo_usdc',
      'avax_usdc',
      'bch_usdc',
      'bnb_usdc',
      'btc_usdc',
      'btcdvol_usdc',
      'buidl_usdc',
      'doge_usdc',
      'dot_usdc',
      'eurr_usdc',
      'eth_usdc',
      'ethdvol_usdc',
      'hype_usdc',
      'link_usdc',
      'ltc_usdc',
      'near_usdc',
      'paxg_usdc',
      'shib_usdc',
      'sol_usdc',
      'steth_usdc',
      'ton_usdc',
      'trump_usdc',
      'trx_usdc',
      'uni_usdc',
      'usde_usdc',
      'usyc_usdc',
      'xrp_usdc',
      'btc_usdt',
      'eth_usdt',
      'eurr_usdt',
      'sol_usdt',
      'steth_usdt',
      'usdc_usdt',
      'usde_usdt',
      'btc_eurr',
      'btc_usde',
      'btc_usyc',
      'eth_btc',
      'eth_eurr',
      'eth_usde',
      'eth_usyc',
      'steth_eth',
      'paxg_btc',
      'drbfix-btc_usdc',
      'drbfix-eth_usdc',
    ]
    | None = None,
    validate: bool | None = None,
  ) -> dict[str, list[str]] | dict[str, dict[str, list[str]]]:
    """Retrieves all available expiration timestamps for instruments. This method can be used to discover which expiration dates are available for trading, which is useful for finding instruments with specific expiration dates.

    Results can be filtered by settlement currency, instrument kind (future or option), and currency pair. The response includes expiration timestamps in milliseconds since the UNIX epoch.

    Args:
      currency: The currency symbol or `"any"` for all or '"grouped"' for all grouped by currency
      kind: Instrument kind, `"future"` or `"option"` or `"any"`
      currency_pair: The currency pair symbol
      validate: Validate the response against the generated schema.

    References:
      - [Deribit API docs](https://docs.deribit.com/api-reference/market-data/public-get_expirations)
    """
    params: dict = {
      'currency': currency,
      'kind': kind,
    }
    if currency_pair is not None:
      params['currency_pair'] = currency_pair
    return await self.request(
      'public/get_expirations',
      params=params,
      validator=validate_get_expirations,
      validate=validate,
    )
