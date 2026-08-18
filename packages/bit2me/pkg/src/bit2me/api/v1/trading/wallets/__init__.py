from .request_deposit import RequestDeposit
from .request_withdrawal import RequestWithdrawal


class Wallets(RequestDeposit, RequestWithdrawal): ...
