from dataclasses import dataclass, field

# Re-exported here, not re-implemented: `mexc.core.__init__.pyi` needs a within-module
# import to reach them (`lazy_loader.attach_stub` only supports `from .* import`), so an
# absolute `typed_core` import can't sit directly in the `.pyi` stub itself. `as X` (not
# the project's usual style, but the standard PEP 484 signal a static checker needs to
# treat a plain re-export as intentional, not private) is load-bearing here specifically.
from typed_core.validation import TypedDict as TypedDict, validator as validator

@dataclass
class ValidationMixin:
  default_validate: bool = field(default=True, kw_only=True)

  def validate(self, validate: bool | None) -> bool:
    return self.default_validate if validate is None else validate
