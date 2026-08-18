from .asset import Asset
from .assets import Assets
from .funding_records import FundingRecords
from .tiered_fee_rate import TieredFeeRate
from .transfer_record import TransferRecord

class Account(Asset, Assets, FundingRecords, TieredFeeRate, TransferRecord):
  ...
