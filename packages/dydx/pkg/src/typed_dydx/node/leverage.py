"""dYdX per-market leverage helper (`MsgUpdateLeverage`)."""

from dataclasses import dataclass

from typed_core.exceptions import BadRequest
from typing_extensions import Mapping

from typed_dydx.node.context import NodeContext
from typed_dydx.node.tx import Tx
from typed_dydx.protos.cosmos.tx import v1beta1 as tx_proto
from typed_dydx.protos.dydxprotocol import clob, subaccounts

MAX_IMF_PPM = 1_000_000
"""The highest initial margin fraction the chain accepts: 100%, or 1x leverage."""


@dataclass
class UpdateLeverage:
  """Per-market leverage endpoint."""

  context: NodeContext
  """Shared node context used for wallet and chain access."""
  tx: Tx
  """Transaction helper used for signing and broadcasting."""

  def build_update_leverage(
    self, imf_ppm: Mapping[int, int], *, subaccount: int = 0
  ) -> clob.MsgUpdateLeverage:
    """Build a `MsgUpdateLeverage` for the wallet's subaccount.

    Args:
      imf_ppm: The initial margin fraction to set, in parts per million, by CLOB pair
        id. Leverage is `1_000_000 / imf_ppm`: `100_000` is 10x.
      subaccount: dYdX subaccount number owned by the wallet.

    Returns:
      dYdX protocol message, with entries ordered by CLOB pair id.

    Raises:
      BadRequest: `imf_ppm` is empty or a value is outside `(0, 1_000_000]`, which the
        chain refuses.
    """
    if not imf_ppm:
      raise BadRequest('At least one CLOB pair leverage entry is required')
    for clob_pair_id, ppm in imf_ppm.items():
      if not 0 < ppm <= MAX_IMF_PPM:
        raise BadRequest(
          f'IMF ppm for CLOB pair {clob_pair_id} must be in (0, {MAX_IMF_PPM}], got {ppm}'
        )
    wallet = self.context.require_wallet()
    return clob.MsgUpdateLeverage(
      subaccount_id=subaccounts.SubaccountId(owner=wallet.address, number=subaccount),
      clob_pair_leverage=[
        clob.LeverageEntry(clob_pair_id=clob_pair_id, custom_imf_ppm=ppm)
        for clob_pair_id, ppm in sorted(imf_ppm.items())
      ],
    )

  async def update_leverage(
    self,
    imf_ppm: Mapping[int, int],
    *,
    subaccount: int = 0,
    mode: tx_proto.BroadcastMode = tx_proto.BroadcastMode.SYNC,
    simulate: bool = False,
  ) -> tx_proto.BroadcastTxResponse:
    """Build, sign, and broadcast a per-market leverage update.

    The chain keeps the subaccount's other markets' settings, refuses a fraction below
    the market's liquidity tier initial margin (above its maximum leverage) or one the
    subaccount's collateral would no longer cover, and rate-limits updates per block
    window. A market's initial margin is the larger of this fraction and its own
    open-interest-scaled one.

    Args:
      imf_ppm: The initial margin fraction to set, in parts per million, by CLOB pair
        id. Leverage is `1_000_000 / imf_ppm`: `100_000` is 10x.
      subaccount: dYdX subaccount number owned by the wallet.
      mode: Cosmos broadcast mode.
      simulate: Whether to simulate the transaction before broadcasting.

    Returns:
      Cosmos broadcast response.

    Raises:
      BadRequest: `imf_ppm` is empty or a value is outside `(0, 1_000_000]`.
    """
    message = self.build_update_leverage(imf_ppm, subaccount=subaccount)
    return await self.tx.sign_and_broadcast([message], mode=mode, simulate=simulate)
