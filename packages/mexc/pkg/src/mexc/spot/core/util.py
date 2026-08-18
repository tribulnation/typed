from typing_extensions import TypedDict, Mapping, TypeGuard, TypeVar
from dataclasses import dataclass, field
import json

from mexc.core import HttpMixin, ValidationMixin, validator
from .auth import AuthHttpMixin

T = TypeVar('T')

MEXC_SPOT_API_BASE = 'https://api.mexc.com'

class ErrorResponse(TypedDict):
  msg: str
  code: int

def is_error_response(r) -> TypeGuard[ErrorResponse]:
  return isinstance(r, Mapping) and 'msg' in r and 'code' in r and r['code'] != 0

def raise_on_error(r: T | ErrorResponse) -> T:
  from mexc.core import ApiError
  if is_error_response(r):
    raise ApiError(r)
  return r # type: ignore

class BaseMixin(ValidationMixin):
  def output(self, data: str | bytes, validator: validator[T | ErrorResponse], validate: bool | None) -> T:
    """Parse the data (optionally validating) and raise if the response is an error."""
    obj = validator(data) if self.validate(validate) else json.loads(data)
    return raise_on_error(obj)

@dataclass
class SpotMixin(HttpMixin, BaseMixin):
  base_url: str = field(default=MEXC_SPOT_API_BASE, kw_only=True)

@dataclass
class AuthSpotMixin(AuthHttpMixin, BaseMixin):
  base_url: str = field(default=MEXC_SPOT_API_BASE, kw_only=True)
