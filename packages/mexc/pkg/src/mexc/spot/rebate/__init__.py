from .affiliate_campaign import AffiliateCampaign
from .affiliate_commission import AffiliateCommission
from .affiliate_commission_detail import AffiliateCommissionDetail
from .affiliate_referral import AffiliateReferral
from .affiliate_subaffiliates import AffiliateSubaffiliates
from .affiliate_withdraw import AffiliateWithdraw
from .detail import Detail
from .history import History
from .refer_code import ReferCode
from .self_detail import SelfDetail

class Rebate(AffiliateCampaign, AffiliateCommission, AffiliateCommissionDetail, AffiliateReferral, AffiliateSubaffiliates, AffiliateWithdraw, Detail, History, ReferCode, SelfDetail):
  ...
