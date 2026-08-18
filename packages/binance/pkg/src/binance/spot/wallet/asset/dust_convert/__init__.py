from .convert import Convert
from .convertible_assets import ConvertibleAssets


class DustConvert(Convert, ConvertibleAssets):
  """Binance dust_convert endpoints."""
