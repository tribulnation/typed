"""Comet transaction lookup endpoint."""

from pydantic import TypeAdapter

from typed_dydx.chain.comet.core import CometEndpoint
from typed_dydx.chain.comet.types import TxResponse


tx_adapter = TypeAdapter(TxResponse)


class Tx(CometEndpoint):
  """Comet transaction lookup endpoint group."""

  async def tx(
    self,
    hash: str,
    *,
    prove: bool | None = None,
    validate: bool | None = None,
  ) -> TxResponse:
    """Return one indexed Comet transaction by hash.

    Args:
      hash: Transaction hash. Comet HTTP accepts the hash with a `0x` prefix.
      prove: Include a Merkle proof for the transaction.
      validate: Validation override for this request.

    Returns:
      Transaction lookup result.

    References:
      - [CometBFT RPC docs](https://docs.cosmos.network/cometbft/latest/api-reference/rpc/info/tx)
    """
    params: dict[str, str | bool] = {'hash': hash}
    if prove is not None:
      params['prove'] = prove
    return await self.result('/tx', params=params, result_adapter=tx_adapter, validate=validate)

