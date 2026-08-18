"""`private/get_mmp_config` — `private/get_mmp_config`."""

from typing_extensions import Literal, NotRequired, TypedDict
from typed_core.validation import validator
from deribit.core import RpcEndpoint


class GetMmpConfigResultEntry(TypedDict):
  index_name: Literal[
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
  """Index identifier, matches (base) cryptocurrency with quote currency"""
  interval: int
  """The duration of the monitoring window in seconds. For example, an interval of 3 implies a 3-second window. 

The interval begins after the first trade. 

If a new trade is executed after the interval has ended, a new interval is started, and counters reset. 

If a trade occurs during an already running interval, that interval continues unaffected. 

This mechanism allows the platform to track activity in short, rolling windows to identify potentially risky trading behavior. 

If set to 0, MMP is disabled. 

Maximum value: 3600 seconds (1 hour)."""
  frozen_time: int
  """Time in seconds that MMP remains active after being triggered. Once this frozen period has passed, MMP will automatically reset, allowing new orders to be submitted. 

If you want to disable automatic reset, set frozen_time to 0. In that case, a manual reset is required using the private/reset_mmp method. 

Manual reset is also possible during the frozen time period. 

Maximum value: 3600 seconds (1 hour)."""
  id: NotRequired[int]
  """Integer identifier for the MMP group (int64). This is the programmatic identifier for the group. Entries without an `mmp_group` name correspond to the orders MMP group (the default group)."""
  mmp_group: NotRequired[str]
  """Name of the MMP group. Absent for the orders MMP group (the default group), which has no string name — its entry is identified by the `id` field alone."""
  quantity_limit: NotRequired[float]
  """The total traded quantity, measured in units of the base currency (e.g., BTC in BTC-PERPETUAL), within the interval. 

This count is direction-agnostic—a buy followed by a sell counts double. 

Example: Buy 10 BTC and sell 10 BTC = 20 total quantity. 

Applicable to both options and futures. 

Maximum 4 decimal places."""
  delta_limit: NotRequired[float]
  """The maximum allowable net transaction delta change during the interval. 

Expressed in units of base currency. 

The delta_limit is treated as an absolute threshold: e.g., delta_limit: 10 → MMP is triggered if net transaction delta exceeds +10 or drops below -10. 

Direction matters: buying +5 delta and selling −5 delta cancels out if within the same interval. 

Note: Note that we use the net transaction delta instead of delta. Net Transaction Delta = Delta - Mark Price. In the rest of this document, "delta" actually refers to net transaction delta. 

Maximum 4 decimal places."""
  vega_limit: NotRequired[float]
  """The maximum change in vega exposure allowed within a given interval, measured in absolute terms. 

Expressed in USD, representing the change in sensitivity to implied volatility across executed trades. 

This parameter is primarily relevant for options traders managing risk in volatile markets. 

Similar to delta_limit, the vega_limit is direction-aware and evaluated on a net basis. If the exposure exceeds the set threshold (positively or negatively), MMP will be triggered. 

Notice: When evaluating Delta and Vega limits for MMP, Deribit uses the greeks at the moment of trade execution. The system does not re-evaluate Delta or Vega using live greeks at the time of MMP checking. 

Maximum 4 decimal places."""
  max_quote_quantity: NotRequired[float]
  """Maximum Quote Quantity (MQQ). MQQ is configured per index but enforced per side, per order book (instrument) — the total combined size of open MMP orders per side per instrument cannot exceed MQQ (specified in base currency). 

**MQQ reserves Initial Margin unconditionally.** As soon as MMP configuration with a non-zero MQQ is active, the platform reserves Initial Margin equal to `MQQ × 3%` — regardless of whether you have any open positions or open orders. This reservation is continuous: it applies from the moment the config is set until it is removed. The reserved margin is visible in the **Portfolio Margin** section of the platform. 

**Releasing MMP-reserved margin.** To free the reserved margin, remove the MMP configuration entirely by calling `private/set_mmp_config` with `interval = 0`. Setting only `max_quote_quantity = 0` without removing the config is not sufficient — the entire configuration entry must be deleted. 

**Important Notes:** 
- **Configured per index, enforced per instrument:** MQQ is configured at the index level (an MMP group is linked to an index). However, the limit is enforced separately per order book (instrument) per side. "Per order book" means per instrument (not per expiry). The limit is NOT the sum across all instruments — each instrument has its own separate MQQ enforcement. 
- **MQQ limits cumulative size, not order count:** For example, with MQQ of 3 BTC, you can place multiple orders (three orders of 1 BTC each, or one order of 2.5 BTC plus one of 0.5 BTC) as long as the total size per side per instrument does not exceed 3 BTC 
- **MQQ is separate per MMP group:** Each MMP group has its own independent MQQ configuration. MQQ limits are enforced separately for each MMP group. 
- **MQQ vs Quantity Limit relationship:** You can set MQQ > `quantity_limit`. This allows quotes to be larger than the quantity limit, and enables MMP to trigger on partial fills of quotes. This decouples the MMP reserved margin from the MMP quantity limit. 
- **Base currency:** MQQ is specified and enforced in base currency 
- **Inverse futures:** Size is calculated as Amount / Price to convert to base currency 
- **Inverse future spreads:** Size is calculated as Amount / IndexPrice 
- **SM accounts:** MMP orders and quotes on options and option_combos are not supported for SM accounts 
- **Rejections:** MQQ is enforced for **MMP-enabled orders and quotes**. Quote entries and MMP-enabled orders (i.e., orders with `mmp=true`) are rejected if their individual size is greater than `max_quote_quantity`, or if accepting them would make the total open MMP size per side per instrument exceed `max_quote_quantity`. Non‑MMP orders are not subject to MQQ and may be larger than `max_quote_quantity`. 
- **Precision:** All MMP configuration values support maximum 4 decimal places 
- **Latency:** There are no latency benefits from MQQ if you already use mass quotes."""
  block_rfq: NotRequired[bool]
  """If true, indicates MMP configuration for Block RFQ. Block RFQ MMP settings are completely separate from normal order/quote MMP settings."""
  trade_count_limit: NotRequired[int]
  """For Block RFQ only. The maximum number of Block RFQ trades allowed in the lookback window. Each RFQ trade counts as +1 towards the limit (not individual legs). Works across all currency pairs."""


validate_get_mmp_config = validator[list[GetMmpConfigResultEntry]](
  list[GetMmpConfigResultEntry]
)


class GetMmpConfig(RpcEndpoint):
  """`private/get_mmp_config`."""

  async def get_mmp_config(
    self,
    *,
    index_name: Literal[
      'btc_usd',
      'eth_usd',
      'btc_usdc',
      'eth_usdc',
      'ada_usdc',
      'algo_usdc',
      'avax_usdc',
      'bch_usdc',
      'bnb_usdc',
      'doge_usdc',
      'dot_usdc',
      'hype_usdc',
      'link_usdc',
      'ltc_usdc',
      'near_usdc',
      'paxg_usdc',
      'shib_usdc',
      'sol_usdc',
      'ton_usdc',
      'trx_usdc',
      'trump_usdc',
      'uni_usdc',
      'xrp_usdc',
      'usde_usdc',
      'buidl_usdc',
      'btcdvol_usdc',
      'ethdvol_usdc',
      'btc_usdt',
      'eth_usdt',
      'all',
    ]
    | None = None,
    mmp_group: str | None = None,
    block_rfq: bool | None = None,
    validate: bool | None = None,
  ) -> list[GetMmpConfigResultEntry]:
    """Retrieves Market Maker Protection (MMP) configuration for an index. Returns all currently active MMP parameters for the selected index, including the interval, `frozen_time`, quantity/delta/vega limits, and `max_quote_quantity`.

    If the `index_name` parameter is not provided, a list of all MMP configurations is returned. An empty list means no MMP configuration exists. This method is useful for verifying your configuration or confirming applied updates.

    For Mass Quotes, specify the `mmp_group` parameter to retrieve configuration for a specific MMP group. If no group is provided, returns configuration for regular orders. Set `block_rfq` to `true` to retrieve MMP configuration for Block RFQ (requires `block_rfq:read` scope).

    Each entry in the response includes an `id` field (integer) that uniquely identifies the MMP group. This integer ID is the programmatic identifier for the group and can be used to reference it in contexts where the string `mmp_group` name is not accepted. Entries that have no `mmp_group` name in the response correspond to the orders MMP group (the default group).

     or `block_rfq:read` (when `block_rfq` = `true`)

    Args:
      index_name: Index identifier of derivative instrument on the platform; skipping this parameter will return all configurations
      mmp_group: Specifies the MMP group for which the configuration is being retrieved. MMP groups are used for Mass Quotes. If MMP group is not provided, the method returns the configuration for the MMP settings for regular orders. The `index_name` must be specified before using this parameter.

    **Note:** Leaving `mmp_group` empty is explicitly allowed and is the correct way to retrieve configuration for the orders MMP group. It is not an error or an incomplete request — omitting this field intentionally targets the default orders MMP group rather than any named mass quote group.

    **📖 Related Article:** [Mass Quotes Specifications](https://docs.deribit.com/articles/mass-quotes-specifications)
      block_rfq: If true, retrieves MMP configuration for Block RFQ. When set, requires `block_rfq` scope instead of `trade` scope. Block RFQ MMP settings are completely separate from normal order/quote MMP settings.
      validate: Validate the response against the generated schema.

    References:
      - [Deribit API docs](https://docs.deribit.com/api-reference/trading/private-get_mmp_config)
    """
    params = {}
    if index_name is not None:
      params['index_name'] = index_name
    if mmp_group is not None:
      params['mmp_group'] = mmp_group
    if block_rfq is not None:
      params['block_rfq'] = block_rfq
    return await self.authed_request(
      'private/get_mmp_config',
      params=params,
      validator=validate_get_mmp_config,
      validate=validate,
    )
