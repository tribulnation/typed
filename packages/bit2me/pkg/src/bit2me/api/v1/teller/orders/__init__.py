from .cancel import Cancel
from .execute import Execute
from .get_status import GetStatus
from .preview import Preview


class Orders(Cancel, Execute, GetStatus, Preview): ...
