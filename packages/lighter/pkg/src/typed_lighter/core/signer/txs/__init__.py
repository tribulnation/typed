"""The 20 user L2 transaction types: Go-exact validation, hashing and `tx_info` encoding.

`base` holds what every type shares (`L2Tx`, `Attributes`, `SignedTx`); the types live in
`orders`, `account`, `assets` and `pools`.
"""

from . import account, assets, orders, pools
from .base import L2Tx

TX_TYPES: dict[int, type[L2Tx]] = {
  cls.TX_TYPE: cls
  for cls in (
    account.ChangePubKey,
    account.CreateSubAccount,
    pools.CreatePublicPool,
    pools.UpdatePublicPool,
    assets.Transfer,
    assets.Withdraw,
    orders.CreateOrder,
    orders.CancelOrder,
    orders.CancelAllOrders,
    orders.ModifyOrder,
    pools.MintShares,
    pools.BurnShares,
    account.UpdateLeverage,
    orders.CreateGroupedOrders,
    account.UpdateMargin,
    assets.StakeAssets,
    assets.UnstakeAssets,
    account.UpdateAccountConfig,
    account.UpdateAccountAssetConfig,
    account.ApproveIntegrator,
  )
}
"""Every user transaction class, by `tx_type`."""
