"""Internal transport, envelope, authentication and error-mapping plumbing shared by the
`classic` and `uta` surfaces. Re-exports the `typed_core` exception hierarchy for convenience.
"""

import lazy_loader as lazy

__getattr__, __dir__, __all__ = lazy.attach_stub(__name__, __file__)
