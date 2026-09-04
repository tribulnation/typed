"""JSON-RPC core for Alchemy's chain-hosted, network-parameterized surfaces (Token,
Transfers, Utility, Simulation) -- the enhanced `alchemy_*` methods, riding a standard
JSON-RPC envelope (`{jsonrpc, id, result}` / `{jsonrpc, id, error}`) over the shared
`api-key-path` HTTP transport (`docs/spec/authoring.md` rule 6: alchemy unwraps JSON-RPC
and passes its REST half through under one core -- `core.rest` is that REST half).

Wire placement is a fixed, per-method convention this core decides once (design §2),
never per-endpoint codegen: most `alchemy_*` methods take their whole flat `request` dict
as one JSON-RPC positional object argument; a handful take something narrower
(`_UNWRAP`/`_ARRAY` below), and `alchemy_getTokenBalances` alone needs a genuinely
positional, partly-folded params array that no by-shape rule can express (rule 0's own
worked example -- see `_get_token_balances_params`).
"""

from typing_extensions import Any, Self, TypeVar, cast
from types import UnionType
from dataclasses import dataclass
import json

from typed_core.validation import validator

from .auth import api_key_url
from .base import AlchemyTransport, Network
from .envelope import unwrap_rpc

T = TypeVar('T')

CHAIN_RPC_HOSTS: dict[Network, str] = {
  'ethereum': 'https://eth-mainnet.g.alchemy.com/v2',
  'bnb': 'https://bnb-mainnet.g.alchemy.com/v2',
  'polygon': 'https://polygon-mainnet.g.alchemy.com/v2',
  'base': 'https://base-mainnet.g.alchemy.com/v2',
  'avalanche': 'https://avax-mainnet.g.alchemy.com/v2',
  'optimism': 'https://opt-mainnet.g.alchemy.com/v2',
  'arbitrum': 'https://arb-mainnet.g.alchemy.com/v2',
  'gnosis': 'https://gnosis-mainnet.g.alchemy.com/v2',
  'celo': 'https://celo-mainnet.g.alchemy.com/v2',
}
"""Per-chain host for Chain APIs and the enhanced `alchemy_*` JSON-RPC methods."""


def chain_rpc_url(network: Network) -> str:
  """Base URL for Chain APIs / enhanced JSON-RPC methods on `network`, without the API
  key segment."""
  return CHAIN_RPC_HOSTS[network]


_UNWRAP: frozenset[str] = frozenset({
  'alchemy_getTokenMetadata',
  'alchemy_simulateExecution',
  'alchemy_simulateAssetChanges',
})
"""Methods whose `request` has exactly one property, sent as that one property's own
value -- never wrapped in an enclosing object -- as the sole JSON-RPC positional
argument. `alchemy_getTokenMetadata`'s `contractAddress` is a scalar; `simulateExecution`/
`simulateAssetChanges`'s `transaction` is itself an object (`SimulationCallTransaction`/
`SimulationTransaction`), still sent unwrapped rather than nested one level deeper."""

_ARRAY: frozenset[str] = frozenset({
  'alchemy_simulateExecutionBundle',
  'alchemy_simulateAssetChangesBundle',
})
"""Methods whose `request` has exactly one, array-valued property (`transactions`), sent
as that array directly -- each element becomes its own positional slot, not wrapped in a
further enclosing list."""


def _json_rpc_params(path: str, request: dict[str, Any] | None) -> list[Any]:
  """Build one method's JSON-RPC positional `params` array from its flat, wire-ready
  `request` dict (already run through `request_type`'s validator).

  Wire placement is a per-method fact (`_UNWRAP`/`_ARRAY` above), not something derivable
  from the request's own runtime shape: `alchemy_getTransactionReceipts` also has a
  request that, on any one call, carries only a single key (exactly one of
  `blockNumber`/`blockHash` is ever set), yet it still needs the whole dict as one
  object param (`[dict(request)]`), not the unwrapped single value `_UNWRAP` produces for
  a genuinely single-argument method. `alchemy_getTokenBalances` never reaches this
  function at all -- see `ChainRpc.request`'s own dispatch, ahead of this one.

  Args:
    path: The JSON-RPC method name (`RpcEndpointSpec.path`).
    request: The wire-ready request dict (`None`/empty for a parameterless call).
  """
  if not request:
    return []
  if path in _UNWRAP:
    (value,) = request.values()
    return [value]
  if path in _ARRAY:
    (value,) = request.values()
    return list(value)
  return [dict(request)]


def _get_token_balances_params(request: dict[str, Any]) -> list[Any]:
  """Build `alchemy_getTokenBalances`'s own positional params: `[address, tokenSpec,
  {pageKey?, maxCount?}?]` (`docs/spec/authoring.md` rule 0's own worked example).

  `tokenSpec` defaults to `'erc20'` when the caller omits it -- the wire array always
  carries a value in that slot; only the trailing options object is ever genuinely
  optional, folding `pageKey`/`maxCount` together only when at least one is set.

  Args:
    request: The wire-ready request dict (`address` required by the spec; `tokenSpec`/
      `pageKey`/`maxCount` all optional).
  """
  params: list[Any] = [request['address'], request.get('tokenSpec') or 'erc20']
  options: dict[str, Any] = {}
  if 'pageKey' in request:
    options['pageKey'] = request['pageKey']
  if 'maxCount' in request:
    options['maxCount'] = request['maxCount']
  if options:
    params.append(options)
  return params


@dataclass(kw_only=True, frozen=True)
class ChainRpc:
  """JSON-RPC core scoped to one EVM network -- threads `network` into `base_url`."""

  client: AlchemyTransport
  base_url: str

  @classmethod
  def new(
    cls, client: AlchemyTransport, *, network: Network | None = None, base_url: str | None = None,
  ) -> Self:
    """Build a chain-scoped JSON-RPC core sharing `client`'s already-built transport.

    Args:
      client: Already-built shared transport, forwarded from whichever composing class
        constructs this core.
      network: EVM network every call through this core is scoped to. Defaults to
        `'ethereum'` when omitted.
      base_url: Fully-qualified base URL override, used as-is when given.
    """
    return cls(
      client=client,
      base_url=base_url or api_key_url(chain_rpc_url(network or 'ethereum'), client.api_key),
    )

  async def request(
    self,
    request: Any = None,
    *,
    method: str | None = None,
    path: str,
    validate: bool | None = None,
    request_type: type[Any] | UnionType | None = None,
    response_type: type[T] | UnionType | None = None,
  ) -> T:
    """Perform one `alchemy_*` enhanced JSON-RPC call: serialize `request` through
    `request_type`'s validator (ADR 0020/S28), place it on the wire per `_json_rpc_params`
    (or `_get_token_balances_params`, for that one irregular method), POST it to
    `base_url`, and validate the reply through `response_type`'s validator.

    No `meta` parameter: this core declares no `[cores.<name>].meta` schema in
    `codegen/config.toml` (design §2/§6) -- every surface it serves authenticates identically, by
    construction, with no per-call credential or other quirk to decide. Every endpoint
    resolving to this core declares `meta: {}`.

    Args:
      request: The generated `Request` value (a `TypedDict` instance, or `None` for a
        parameterless operation).
      method: Unused -- every enhanced method rides HTTP POST; kept only so this method's
        signature matches `core.rest.RestEndpoint.request`'s, since `rpc_endpoint`
        (design §7) always passes `method=` whenever the spec declares one, and this
        subtree's own endpoints simply never declare one.
      path: The JSON-RPC method name, e.g. `alchemy_getTokenBalances`.
      validate: Per-call override of response validation.
      request_type: The generated request type, used to serialize `request`.
      response_type: The generated response type, used to validate the reply.
    """
    # `validator(...).dump(...)` returns JSON *bytes*; `_json_rpc_params`/
    # `_get_token_balances_params` both need a real dict to inspect and rearrange
    # individual fields, so round-trip through `json.loads` to get one back with every
    # declared format's `PlainSerializer` (S27) already applied.
    values = (
      json.loads(validator(cast(type, request_type)).dump(request))
      if request_type is not None and request is not None
      else None
    )
    params = (
      _get_token_balances_params(values or {})
      if path == 'alchemy_getTokenBalances'
      else _json_rpc_params(path, values)
    )
    body = {'jsonrpc': '2.0', 'id': 1, 'method': path, 'params': params}
    response = await self.client.http.request('POST', self.base_url, json=body)
    payload = unwrap_rpc(response)
    if response_type is None:
      return None  # type: ignore[return-value]
    if not self.client.should_validate(validate):
      return payload  # type: ignore[return-value]
    return validator(cast(type, response_type)).python(payload)
