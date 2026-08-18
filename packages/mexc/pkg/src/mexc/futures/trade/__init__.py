from .batch_query import BatchQuery
from .cancel_all_orders import CancelAllOrders
from .cancel_all_plan import CancelAllPlan
from .cancel_all_stop import CancelAllStop
from .cancel_external_order import CancelExternalOrder
from .cancel_order import CancelOrder
from .cancel_plan import CancelPlan
from .cancel_stop import CancelStop
from .change_stop_plan_price import ChangeStopPlanPrice
from .change_stop_price import ChangeStopPrice
from .deal_details import DealDetails
from .external_order import ExternalOrder
from .history_orders import HistoryOrders
from .open_orders import OpenOrders
from .order import Order
from .order_deals import OrderDeals
from .place_plan import PlacePlan
from .plan_orders import PlanOrders
from .stop_orders import StopOrders
from .submit_batch import SubmitBatch
from .submit_order import SubmitOrder

class Trade(BatchQuery, CancelAllOrders, CancelAllPlan, CancelAllStop, CancelExternalOrder, CancelOrder, CancelPlan, CancelStop, ChangeStopPlanPrice, ChangeStopPrice, DealDetails, ExternalOrder, HistoryOrders, OpenOrders, Order, OrderDeals, PlacePlan, PlanOrders, StopOrders, SubmitBatch, SubmitOrder):
  ...
