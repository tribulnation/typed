"""Small shared helpers for the new core. `timestamps`/`rounding`/`paging` were the
legacy core's own copies (`core/mixin.py`'s pre-revamp `Endpoint`/`Router`, since
retired) and are gone with it -- `path_join` is the one still used, by `core/auth.py`'s
`api_key_url`.
"""

from .paths import path_join
