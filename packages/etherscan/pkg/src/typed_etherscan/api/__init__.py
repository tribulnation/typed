"""Generated endpoint tree, one subpackage per Etherscan module (`account`, `blocks`, ...).

Hand-written and excluded from codegen's router generation (`codegen/python.py`'s
`skip_router`): with every section attaching directly to the client root, composing a
second, redundant wrapper class here on top of `main.py`'s `Etherscan` would just repeat
it one level down -- `main.py` is the one place that composition belongs (S11).
"""
