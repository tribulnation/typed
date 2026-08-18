from .create_combo import CreateCombo
from .get_combo_details import GetComboDetails
from .get_combo_ids import GetComboIds
from .get_combos import GetCombos
from .get_leg_prices import GetLegPrices


class ComboBooks(
  CreateCombo,
  GetComboDetails,
  GetComboIds,
  GetCombos,
  GetLegPrices,
):
  """ComboBooks endpoints."""
