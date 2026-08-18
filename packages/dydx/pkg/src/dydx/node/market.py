"""Market conversion helpers for dYdX order construction."""

from dataclasses import dataclass
from decimal import Decimal, ROUND_FLOOR

from dydx.indexer.types.market import PerpetualMarket
from dydx.protos.dydxprotocol import clob, subaccounts

DecimalValue = Decimal | str | int

def round_down(value: Decimal, step: Decimal) -> Decimal:
  """Round a decimal down to the nearest step.

  Args:
    value: Decimal value to quantize.
    step: Step size used as the floor interval.

  Returns:
    Value floored to the nearest step.
  """
  return (value / step).to_integral_value(rounding=ROUND_FLOOR) * step

def parse_decimal(value: DecimalValue) -> Decimal:
  """Convert ergonomic numeric input into a precise decimal.

  Args:
    value: Decimal, integer, or string numeric value.

  Returns:
    Decimal representation suitable for protocol quantization.
  """
  return value if isinstance(value, Decimal) else Decimal(str(value))

@dataclass(frozen=True)
class Market:
  """Trading market metadata used to build protocol orders."""

  clob_pair_id: int
  """dYdX CLOB pair ID."""
  atomic_resolution: int
  """Base asset atomic resolution used for quantum conversion."""
  quantum_conversion_exponent: int
  """dYdX exponent used to convert between quantums and quote units."""
  step_base_quantums: int
  """Minimum base quantum step accepted by the market."""
  subticks_per_tick: int
  """Number of subticks represented by one market tick."""

  @classmethod
  def from_payload(cls, market: 'Market | PerpetualMarket') -> 'Market':
    """Create market metadata from an indexer-style payload.

    Args:
      market: Existing market metadata or an indexer perpetual market payload.

    Returns:
      Market metadata needed for CLOB order construction.
    """
    if isinstance(market, Market):
      return market
    return cls(
      clob_pair_id=int(market['clobPairId']),
      atomic_resolution=market['atomicResolution'],
      quantum_conversion_exponent=market['quantumConversionExponent'],
      step_base_quantums=market['stepBaseQuantums'],
      subticks_per_tick=market['subticksPerTick'],
    )

  def calculate_quantums(self, size: DecimalValue) -> int:
    """Convert human size into base quantums.

    Args:
      size: Human-readable base asset size.

    Returns:
      Protocol quantums floored to the market step size.
    """
    raw = parse_decimal(size) * (Decimal(10) ** (-self.atomic_resolution))
    quantums = round_down(raw, Decimal(self.step_base_quantums))
    return int(max(quantums, Decimal(self.step_base_quantums)))

  def calculate_subticks(self, price: DecimalValue) -> int:
    """Convert human price into subticks.

    Args:
      price: Human-readable order price.

    Returns:
      Protocol subticks floored to the market tick size.
    """
    quote_quantums_atomic_resolution = -6
    exponent = (
      self.atomic_resolution
      - self.quantum_conversion_exponent
      - quote_quantums_atomic_resolution
    )
    raw = parse_decimal(price) * (Decimal(10) ** exponent)
    subticks = round_down(raw, Decimal(self.subticks_per_tick))
    return int(max(subticks, Decimal(self.subticks_per_tick)))

  def order_id(
    self, *, owner: str, subaccount_number: int, client_id: int, order_flags: int,
  ) -> clob.OrderId:
    """Build a protocol order ID for this market.

    Args:
      owner: dYdX bech32 owner address.
      subaccount_number: dYdX subaccount number under the owner address.
      client_id: Client-generated order ID.
      order_flags: dYdX protocol order flag bits.

    Returns:
      Protocol order ID for this market and subaccount.
    """
    return clob.OrderId(
      subaccount_id=subaccounts.SubaccountId(owner=owner, number=subaccount_number),
      client_id=client_id,
      order_flags=order_flags,
      clob_pair_id=self.clob_pair_id,
    )
