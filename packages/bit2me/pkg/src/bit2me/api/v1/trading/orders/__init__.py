from .cancel import Cancel
from .create import Create
from .get import Get
from .list import List
from .list_trades import ListTrades


class Orders(Cancel, Create, Get, List, ListTrades): ...
