from typing_extensions import Any, Literal, NotRequired, TypedDict
from mexc.core import Timestamp, validator
from mexc.futures.core import FuturesMixin

class ContractSpecListItem(TypedDict):
  """Contract metadata record."""
  symbol: str
  """Contract symbol."""
  displayName: NotRequired[str]
  """Display name."""
  displayNameEn: NotRequired[str]
  """English display name."""
  positionOpenType: NotRequired[Literal[1, 2, 3]]
  """Supported margin modes: 1 isolated, 2 cross, 3 both."""
  baseCoin: NotRequired[str]
  """Base currency."""
  quoteCoin: NotRequired[str]
  """Quote currency."""
  settleCoin: NotRequired[str]
  """Settlement currency."""
  contractSize: NotRequired[float]
  """Contract value."""
  minLeverage: NotRequired[int]
  """Minimum supported leverage."""
  maxLeverage: NotRequired[int]
  """Maximum supported leverage."""
  priceScale: NotRequired[int]
  """Price precision scale."""
  volScale: NotRequired[int]
  """Volume precision scale."""
  amountScale: NotRequired[int]
  """Amount precision scale."""
  priceUnit: NotRequired[float]
  """Minimum price increment."""
  volUnit: NotRequired[float]
  """Minimum volume increment."""
  minVol: NotRequired[float]
  """Minimum order volume."""
  maxVol: NotRequired[float]
  """Maximum order volume."""
  state: NotRequired[Literal[0, 1, 2, 3, 4]]
  """Contract status: 0 enabled, 1 delivery, 2 completed, 3 offline, 4 paused."""
  apiAllowed: NotRequired[bool]
  """Whether API trading is allowed for the contract."""

class RiskLimitCustomItem(TypedDict):
  """Returned riskLimitCustom item field."""
  imr: float
  """Returned imr field."""
  level: int
  """Returned level field."""
  maxLeverage: int
  """Returned maxLeverage field."""
  maxVol: int
  """Returned maxVol field."""
  mmr: float
  """Returned mmr field."""

class ContractSpec(TypedDict):
  """Contract metadata record."""
  symbol: str
  """Contract symbol."""
  displayName: str
  """Display name."""
  displayNameEn: str
  """English display name."""
  positionOpenType: Literal[1, 2, 3]
  """Supported margin modes: 1 isolated, 2 cross, 3 both."""
  baseCoin: str
  """Base currency."""
  quoteCoin: str
  """Quote currency."""
  settleCoin: str
  """Settlement currency."""
  contractSize: float
  """Contract value."""
  minLeverage: int
  """Minimum supported leverage."""
  maxLeverage: int
  """Maximum supported leverage."""
  priceScale: int
  """Price precision scale."""
  volScale: int
  """Volume precision scale."""
  amountScale: int
  """Amount precision scale."""
  priceUnit: float
  """Minimum price increment."""
  volUnit: float
  """Minimum volume increment."""
  minVol: float
  """Minimum order volume."""
  maxVol: float
  """Maximum order volume."""
  state: Literal[0, 1, 2, 3, 4]
  """Contract status: 0 enabled, 1 delivery, 2 completed, 3 offline, 4 paused."""
  apiAllowed: bool
  """Whether API trading is allowed for the contract."""
  appraisal: int
  """Returned appraisal field."""
  askLimitPriceRate: float
  """Returned askLimitPriceRate field."""
  automaticDelivery: int
  """Returned automaticDelivery field."""
  baseCoinIconUrl: str
  """Returned baseCoinIconUrl field."""
  baseCoinId: str
  """baseCoinId identifier."""
  baseCoinName: str
  """Returned baseCoinName field."""
  bidLimitPriceRate: float
  """Returned bidLimitPriceRate field."""
  conceptPlate: list[str]
  """Returned conceptPlate field."""
  conceptPlateId: list[int]
  """conceptPlateId identifier."""
  countryConfigContractMaxLeverage: int
  """Returned countryConfigContractMaxLeverage field."""
  createTime: Timestamp
  """createTime timestamp in milliseconds."""
  depthStepList: list[str]
  """Returned depthStepList field."""
  feeRateMode: str
  """Returned feeRateMode field."""
  feeRateType: str
  """Returned feeRateType field."""
  fn: str
  """Returned fn field."""
  futureType: int
  """Returned futureType field."""
  id: int
  """id identifier."""
  indexOrigin: list[str]
  """Returned indexOrigin field."""
  initialMarginRate: float
  """Returned initialMarginRate field."""
  isHidden: bool
  """Returned isHidden field."""
  isHot: bool
  """Returned isHot field."""
  isMaxLeverage: bool
  """Returned isMaxLeverage field."""
  isNew: bool
  """Returned isNew field."""
  isZeroFeeRate: bool
  """Returned isZeroFeeRate field."""
  isZeroFeeSymbol: bool
  """Returned isZeroFeeSymbol field."""
  leverageFeeRates: list[dict[str, Any]]
  """Undocumented leverage fee-rate rows; upstream returns an empty array in every observed response."""
  limitMaxVol: int
  """Returned limitMaxVol field."""
  liquidationFeeRate: float
  """Returned liquidationFeeRate field."""
  maintenanceMarginRate: float
  """Returned maintenanceMarginRate field."""
  makerFeeRate: int
  """Returned makerFeeRate field."""
  marketOrderMaxLevel: int
  """Returned marketOrderMaxLevel field."""
  marketOrderPriceLimitRate1: float
  """Returned marketOrderPriceLimitRate1 field."""
  marketOrderPriceLimitRate2: float
  """Returned marketOrderPriceLimitRate2 field."""
  maxNumOrders: list[int]
  """Returned maxNumOrders field."""
  openingCountdownOption: int
  """Returned openingCountdownOption field."""
  openingTime: Timestamp
  """openingTime timestamp in milliseconds."""
  preMarket: bool
  """Returned preMarket field."""
  priceCoefficientVariation: float
  """Returned priceCoefficientVariation field."""
  quoteCoinName: str
  """Returned quoteCoinName field."""
  riskBaseVol: int
  """Returned riskBaseVol field."""
  riskIncrImr: int
  """Returned riskIncrImr field."""
  riskIncrMmr: int
  """Returned riskIncrMmr field."""
  riskIncrVol: int
  """Returned riskIncrVol field."""
  riskLevelLimit: int
  """Returned riskLevelLimit field."""
  riskLimitCustom: list[RiskLimitCustomItem]
  """Returned riskLimitCustom field."""
  riskLimitMode: str
  """Returned riskLimitMode field."""
  riskLimitType: Literal['BY_VOLUME', 'BY_VALUE']
  """Risk-limit basis: BY_VOLUME or BY_VALUE."""
  riskLongShortSwitch: int
  """Returned riskLongShortSwitch field."""
  showAppraisalCountdown: int
  """Returned showAppraisalCountdown field."""
  showBeforeOpen: bool
  """Returned showBeforeOpen field."""
  stopOnlyFair: bool
  """Returned stopOnlyFair field."""
  tagIdList: list[int]
  """Returned tagIdList field."""
  takerFeeRate: float
  """Returned takerFeeRate field."""
  threshold: int
  """Returned threshold field."""
  tieredFeeRates: list[dict[str, Any]]
  """Undocumented tiered fee-rate rows; upstream returns an empty array in every observed response."""
  triggerProtect: float
  """Returned triggerProtect field."""
  type: int
  """Contract type code. Absent from the upstream field table, so its value set is unknown and no `enum` is declared; every observed response returns 1."""
  typeLabel: int
  """Returned typeLabel field."""
  vid: str
  """vid identifier."""

class ContractInfoResponse(TypedDict):
  """Contract information envelope"""
  success: bool
  """Whether the API request succeeded."""
  code: NotRequired[int]
  """MEXC response code; zero indicates success when present."""
  message: NotRequired[str]
  """Error or status message when present."""
  data: NotRequired[ContractSpec | list[ContractSpecListItem]]
  """Contract metadata object when symbol is supplied, otherwise a list."""

adapter = validator(ContractInfoResponse)

class ContractInfo(FuturesMixin):
  async def contract_info(
    self, *,
    symbol: str | None = None, validate: bool | None = None,
  ) -> ContractInfoResponse:
    """Return contract metadata, optionally filtered to one futures contract.

    Args:
      symbol: Optional contract symbol filter, for example BTC_USDT.
      validate: Validation override for this request.

    Returns:
      The validated endpoint response.

    References:
      - [MEXC API docs](https://mexcdevelop.github.io/apidocs/contract_v1_en/#get-the-contract-information)
    """
    params = {}
    if symbol is not None:
      params['symbol'] = symbol
    r = await self.request('GET', '/api/v1/contract/detail', params=params)
    return self.envelope_output(r.text, adapter, validate)
