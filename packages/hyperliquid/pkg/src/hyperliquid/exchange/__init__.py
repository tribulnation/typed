from dataclasses import dataclass as _dataclass
from .activate_outcome_deployer import ActivateOutcomeDeployer
from .agent_enable_dex_abstraction import AgentEnableDexAbstraction
from .agent_send_asset import AgentSendAsset
from .agent_set_abstraction import AgentSetAbstraction
from .approve_agent import ApproveAgent
from .approve_builder_fee import ApproveBuilderFee
from .authorize_aqav2_role import AuthorizeAqav2Role
from .cancel import Cancel
from .cancel_by_cloid import CancelByCloid
from .claim_rewards import ClaimRewards
from .disable_aligned_quote_token import DisableAlignedQuoteToken
from .disable_dex import DisableDex
from .disable_quote_token import DisableQuoteToken
from .enable_aligned_quote_token import EnableAlignedQuoteToken
from .enable_quote_token import EnableQuoteToken
from .genesis import Genesis
from .gossip_priority_bid import GossipPriorityBid
from .halt_trading import HaltTrading
from .hip3_liquidator_transfer import Hip3LiquidatorTransfer
from .merge_outcome import MergeOutcome
from .merge_question import MergeQuestion
from .modify_order import ModifyOrder
from .modify_orders import ModifyOrders
from .negate_outcome import NegateOutcome
from .noop import Noop
from .order import Order
from .register_and_associate_named_outcome_from_template import (
  RegisterAndAssociateNamedOutcomeFromTemplate,
)
from .register_asset import RegisterAsset
from .register_asset2 import RegisterAsset2
from .register_hyperliquidity import RegisterHyperliquidity
from .register_question_from_template import RegisterQuestionFromTemplate
from .register_spot import RegisterSpot
from .register_standalone_outcome_from_template import (
  RegisterStandaloneOutcomeFromTemplate,
)
from .register_token2 import RegisterToken2
from .reserve_request_weight import ReserveRequestWeight
from .schedule_cancel import ScheduleCancel
from .send_asset import SendAsset
from .send_to_evm_with_data import SendToEvmWithData
from .set_deployer_fees import SetDeployerFees
from .set_deployer_trading_fee_share import SetDeployerTradingFeeShare
from .set_fee_recipient import SetFeeRecipient
from .set_funding_interest_rates import SetFundingInterestRates
from .set_funding_multipliers import SetFundingMultipliers
from .set_margin_modes import SetMarginModes
from .set_margin_table_ids import SetMarginTableIds
from .set_open_interest_caps import SetOpenInterestCaps
from .set_oracle import SetOracle
from .set_perp_annotation import SetPerpAnnotation
from .set_sub_deployers import SetSubDeployers
from .settle_outcome import SettleOutcome
from .settle_question2 import SettleQuestion2
from .split_outcome import SplitOutcome
from .spot_transfer import SpotTransfer
from .staking_deposit import StakingDeposit
from .staking_withdraw import StakingWithdraw
from .token_delegate import TokenDelegate
from .top_up_isolated_only_margin import TopUpIsolatedOnlyMargin
from .twap_cancel import TwapCancel
from .twap_order import TwapOrder
from .update_isolated_margin import UpdateIsolatedMargin
from .update_leverage import UpdateLeverage
from .usd_class_transfer import UsdClassTransfer
from .usdc_transfer import UsdcTransfer
from .user_dex_abstraction import UserDexAbstraction
from .user_genesis import UserGenesis
from .user_set_abstraction import UserSetAbstraction
from .validator_l1_stream import ValidatorL1Stream
from .vault_transfer import VaultTransfer
from .withdraw3 import Withdraw3


@_dataclass
class Exchange(
  ActivateOutcomeDeployer,
  AgentEnableDexAbstraction,
  AgentSendAsset,
  AgentSetAbstraction,
  ApproveAgent,
  ApproveBuilderFee,
  AuthorizeAqav2Role,
  Cancel,
  CancelByCloid,
  ClaimRewards,
  DisableAlignedQuoteToken,
  DisableDex,
  DisableQuoteToken,
  EnableAlignedQuoteToken,
  EnableQuoteToken,
  Genesis,
  GossipPriorityBid,
  HaltTrading,
  Hip3LiquidatorTransfer,
  MergeOutcome,
  MergeQuestion,
  ModifyOrder,
  ModifyOrders,
  NegateOutcome,
  Noop,
  Order,
  RegisterAndAssociateNamedOutcomeFromTemplate,
  RegisterAsset,
  RegisterAsset2,
  RegisterHyperliquidity,
  RegisterQuestionFromTemplate,
  RegisterSpot,
  RegisterStandaloneOutcomeFromTemplate,
  RegisterToken2,
  ReserveRequestWeight,
  ScheduleCancel,
  SendAsset,
  SendToEvmWithData,
  SetDeployerFees,
  SetDeployerTradingFeeShare,
  SetFeeRecipient,
  SetFundingInterestRates,
  SetFundingMultipliers,
  SetMarginModes,
  SetMarginTableIds,
  SetOpenInterestCaps,
  SetOracle,
  SetPerpAnnotation,
  SetSubDeployers,
  SettleOutcome,
  SettleQuestion2,
  SplitOutcome,
  SpotTransfer,
  StakingDeposit,
  StakingWithdraw,
  TokenDelegate,
  TopUpIsolatedOnlyMargin,
  TwapCancel,
  TwapOrder,
  UpdateIsolatedMargin,
  UpdateLeverage,
  UsdClassTransfer,
  UsdcTransfer,
  UserDexAbstraction,
  UserGenesis,
  UserSetAbstraction,
  ValidatorL1Stream,
  VaultTransfer,
  Withdraw3,
): ...
