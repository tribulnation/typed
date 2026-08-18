from dataclasses import dataclass, field
from coinbase.core.endpoint.rpc import RpcEndpoint
from .batch_cancel import BatchCancel
from .close_position import ClosePosition
from .create import Create
from .edit import Edit
from .edit_preview import EditPreview
from .historical import Historical
from .preview import Preview


@dataclass(frozen=True, kw_only=True)
class Orders(RpcEndpoint):
  """`orders` endpoints."""

  batch_cancel: BatchCancel = field(init=False)
  close_position: ClosePosition = field(init=False)
  create: Create = field(init=False)
  edit: Edit = field(init=False)
  edit_preview: EditPreview = field(init=False)
  historical: Historical = field(init=False)
  preview: Preview = field(init=False)

  def __post_init__(self):
    object.__setattr__(self, 'batch_cancel', BatchCancel(client=self.client))
    object.__setattr__(self, 'close_position', ClosePosition(client=self.client))
    object.__setattr__(self, 'create', Create(client=self.client))
    object.__setattr__(self, 'edit', Edit(client=self.client))
    object.__setattr__(self, 'edit_preview', EditPreview(client=self.client))
    object.__setattr__(self, 'historical', Historical(client=self.client))
    object.__setattr__(self, 'preview', Preview(client=self.client))
