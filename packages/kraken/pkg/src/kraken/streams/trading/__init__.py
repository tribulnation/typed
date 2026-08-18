"""`trading` endpoints."""

from .add_order import AddOrder
from .amend_order import AmendOrder
from .batch_add import BatchAdd
from .batch_cancel import BatchCancel
from .cancel_all import CancelAll
from .cancel_all_orders_after import CancelAllOrdersAfter
from .cancel_order import CancelOrder
from .edit_order import EditOrder


class Trading(
  AddOrder,
  AmendOrder,
  BatchAdd,
  BatchCancel,
  CancelAll,
  CancelAllOrdersAfter,
  CancelOrder,
  EditOrder,
):
  """`trading` endpoints."""
