from .cancel_transfer_by_id import CancelTransferById
from .get_transfers import GetTransfers
from .submit_transfer_between_subaccounts import SubmitTransferBetweenSubaccounts
from .submit_transfer_to_subaccount import SubmitTransferToSubaccount
from .submit_transfer_to_user import SubmitTransferToUser


class Transfers(
  CancelTransferById,
  GetTransfers,
  SubmitTransferBetweenSubaccounts,
  SubmitTransferToSubaccount,
  SubmitTransferToUser,
):
  """Transfers endpoints."""
