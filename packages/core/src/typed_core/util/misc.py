from decimal import Decimal, ROUND_HALF_DOWN, ROUND_FLOOR, ROUND_CEILING

def round2tick(x: Decimal, tick_size: Decimal) -> Decimal:
  r = (x / tick_size).quantize(Decimal('1.'), rounding=ROUND_HALF_DOWN) * tick_size
  return r.normalize()

def trunc2tick(x: Decimal, tick_size: Decimal) -> Decimal:
  r = (x / tick_size).to_integral_value(rounding=ROUND_FLOOR) * tick_size
  return r.normalize()

def ceil2tick(x: Decimal, tick_size: Decimal) -> Decimal:
  r = (x / tick_size).to_integral_value(rounding=ROUND_CEILING) * tick_size
  return r.normalize()

def path_join(*parts: str):
  return '/'.join([part.strip('/') for part in parts])