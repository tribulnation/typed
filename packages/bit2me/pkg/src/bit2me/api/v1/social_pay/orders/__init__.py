from .claim import Claim
from .create import Create
from .list import List


class Orders(Claim, Create, List): ...
