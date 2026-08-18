from .fee_group_commission_update import FeeGroupCommissionUpdate
from .fee_group_create import FeeGroupCreate
from .fee_group_delete import FeeGroupDelete
from .fee_group_members import FeeGroupMembers
from .fee_group_members_assign import FeeGroupMembersAssign
from .fee_group_members_unassign import FeeGroupMembersUnassign
from .fee_groups import FeeGroups
from .markup_trade_aggregations import MarkupTradeAggregations
from .markup_trade_details import MarkupTradeDetails
from .member_fee_group import MemberFeeGroup


class Caas(
  FeeGroupCommissionUpdate,
  FeeGroupCreate,
  FeeGroupDelete,
  FeeGroupMembers,
  FeeGroupMembersAssign,
  FeeGroupMembersUnassign,
  FeeGroups,
  MarkupTradeAggregations,
  MarkupTradeDetails,
  MemberFeeGroup,
):
  """Binance caas endpoints."""
