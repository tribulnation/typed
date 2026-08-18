from typing_extensions import Literal, NotRequired, TypedDict
from typed_core.validation import validator
from binance.core.endpoint.rpc import RpcEndpoint


class PredictionInboundTransferResult(TypedDict):
  """The created inbound transfer."""

  transferId: NotRequired[str]
  """Transfer ID. Pass this to `spot.prediction.transfer_status` to poll its status."""
  status: NotRequired[str]
  """Initial transfer status."""


class TransferInbound(RpcEndpoint):
  """Transfer funds from the prediction wallet back to the user's CEX account (SPOT or FUNDING). Requires SAS authorization on the wallet; if SAS is not enabled, the request is rejected with `-31003 SAS authorization required`."""

  async def transfer_inbound(
    self,
    *,
    wallet_id: str,
    wallet_address: str,
    from_token_amount: str,
    account_type: Literal['SPOT', 'FUNDING'],
    from_token: str | None = None,
    to_token: str | None = None,
    chain_id: str | None = None,
    validate: bool | None = None,
  ) -> PredictionInboundTransferResult:
    """Transfer funds from the prediction wallet back to the user's CEX account (SPOT or FUNDING). Requires SAS authorization on the wallet; if SAS is not enabled, the request is rejected with `-31003 SAS authorization required`.

    Args:
      wallet_id: Wallet ID.
      wallet_address: User's prediction wallet address.
      from_token_amount: Transfer amount in wei (18 decimals). Must be > 0. Example: `1000000000000000000` = 1 USDT.
      account_type: Destination CEX account.
      from_token: Source token symbol. Default `USDT`.
      to_token: Destination token symbol. Default `USDT`.
      chain_id: Chain ID. Default `56` (BSC).

    References:
      - [Official docs](https://developers.binance.com/en/docs/catalog/web3-wallet-prediction-trading/api/rest-api/transfer#create-inbound-transfer)
    """
    params: dict = {
      'walletId': wallet_id,
      'walletAddress': wallet_address,
      'fromTokenAmount': from_token_amount,
      'accountType': account_type,
    }
    if from_token is not None:
      params['fromToken'] = from_token
    if to_token is not None:
      params['toToken'] = to_token
    if chain_id is not None:
      params['chainId'] = chain_id
    _Response = PredictionInboundTransferResult
    _validator = validator[_Response](_Response)
    return await self.authed_request(
      'POST',
      '/sapi/v1/w3w/wallet/prediction/transfer/inbound',
      params=params,
      validator=_validator,
      validate=validate,
    )
