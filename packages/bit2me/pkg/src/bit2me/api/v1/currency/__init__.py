from .conversion import Conversion
from .ohlca import Ohlca
from .prices import Prices
from .rates import Rates


class Currency(Conversion, Ohlca, Prices, Rates): ...
