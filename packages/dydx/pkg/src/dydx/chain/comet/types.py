"""Shared Comet HTTP JSON response types."""

from datetime import datetime

from typing_extensions import NotRequired, TypedDict


class ProtocolVersion(TypedDict):
  """Comet peer protocol versions."""

  p2p: str
  """Peer-to-peer protocol version."""
  block: str
  """Block protocol version."""
  app: str
  """Application protocol version."""


class NodeOtherInfo(TypedDict):
  """Additional node metadata."""

  tx_index: str
  """Transaction indexer mode."""
  rpc_address: str
  """RPC listener address advertised by the node."""


class NodeInfo(TypedDict):
  """Comet node identity and network metadata."""

  protocol_version: ProtocolVersion
  """Protocol versions supported by the node."""
  id: str
  """Node identifier."""
  listen_addr: str
  """Peer listener address."""
  network: str
  """Chain identifier served by the node."""
  version: str
  """CometBFT node version."""
  channels: str
  """Enabled peer channels."""
  moniker: str
  """Human-readable node name."""
  other: NodeOtherInfo
  """Additional node metadata."""


class SyncInfo(TypedDict):
  """Comet sync and available block range metadata."""

  latest_block_hash: str
  """Latest block hash known by the node."""
  latest_app_hash: str
  """Latest application hash known by the node."""
  latest_block_height: str
  """Latest block height known by the node."""
  latest_block_time: datetime
  """Timestamp for the latest block known by the node."""
  earliest_block_hash: str
  """Earliest block hash available from the node."""
  earliest_app_hash: str
  """Earliest application hash available from the node."""
  earliest_block_height: str
  """Earliest block height available from the node."""
  earliest_block_time: datetime
  """Timestamp for the earliest block available from the node."""
  catching_up: bool
  """Whether the node is still syncing."""


class PublicKey(TypedDict):
  """Comet public key container."""

  type: str
  """Public key type."""
  value: str
  """Base64-encoded public key value."""


class ValidatorInfo(TypedDict):
  """Comet validator identity and power metadata."""

  address: str
  """Validator consensus address."""
  pub_key: PublicKey
  """Validator public key."""
  voting_power: str
  """Validator voting power."""


class StatusResponse(TypedDict):
  """Comet node status result."""

  node_info: NodeInfo
  """Node protocol, identity, network, version, and RPC metadata."""
  sync_info: SyncInfo
  """Latest and earliest block metadata plus catch-up state."""
  validator_info: ValidatorInfo
  """Validator identity and voting power for the serving node."""


class BlockIdParts(TypedDict):
  """Comet block part set metadata."""

  total: int
  """Number of parts in the block part set."""
  hash: str
  """Block part set hash."""


class BlockId(TypedDict):
  """Comet block identifier."""

  hash: str
  """Block hash."""
  parts: BlockIdParts
  """Block part set metadata."""


class BlockVersion(TypedDict, total=False):
  """Comet block header version."""

  block: str
  """Block protocol version."""
  app: str
  """Application protocol version."""


class BlockHeader(TypedDict):
  """Comet block header."""

  version: BlockVersion
  """Block and application protocol versions."""
  chain_id: str
  """Chain identifier."""
  height: str
  """Block height."""
  time: datetime
  """Block timestamp."""
  last_block_id: BlockId
  """Previous block identifier."""
  last_commit_hash: str
  """Previous commit hash."""
  data_hash: str
  """Block data hash."""
  validators_hash: str
  """Current validator set hash."""
  next_validators_hash: str
  """Next validator set hash."""
  consensus_hash: str
  """Consensus parameters hash."""
  app_hash: str
  """Application hash after block execution."""
  last_results_hash: str
  """Previous block results hash."""
  evidence_hash: str
  """Evidence hash."""
  proposer_address: str
  """Consensus address of the block proposer."""


class BlockData(TypedDict):
  """Comet block transaction data."""

  txs: list[str]
  """Base64-encoded transactions included in the block."""


class DuplicateVoteEvidence(TypedDict, total=False):
  """Comet duplicate-vote evidence."""

  vote_a: object
  """First conflicting vote."""
  vote_b: object
  """Second conflicting vote."""
  total_voting_power: str
  """Total validator voting power at the infraction height."""
  validator_power: str
  """Voting power of the offending validator."""
  timestamp: datetime
  """Evidence timestamp."""


class LightClientAttackEvidence(TypedDict, total=False):
  """Comet light-client attack evidence."""

  conflicting_block: object
  """Conflicting light block."""
  common_height: str
  """Common height shared with the canonical chain."""
  byzantine_validators: list[ValidatorInfo]
  """Validators identified as Byzantine."""
  total_voting_power: str
  """Total validator voting power at the infraction height."""
  timestamp: datetime
  """Evidence timestamp."""


EvidenceItem = DuplicateVoteEvidence | LightClientAttackEvidence
"""Evidence item returned in a Comet block."""


class BlockEvidence(TypedDict):
  """Comet block evidence container."""

  evidence: list[EvidenceItem]
  """Evidence records included in the block."""


class CommitSignature(TypedDict):
  """Validator commit signature for a block."""

  block_id_flag: int
  """Commit signature block ID flag."""
  validator_address: str
  """Consensus address of the signing validator."""
  timestamp: datetime
  """Signature timestamp."""
  signature: str | None
  """Base64-encoded validator signature, or null when the validator did not sign."""


class Commit(TypedDict):
  """Comet block commit."""

  height: str
  """Committed block height."""
  round: int
  """Consensus round."""
  block_id: BlockId
  """Committed block identifier."""
  signatures: list[CommitSignature]
  """Validator commit signatures."""


class Block(TypedDict):
  """Comet block payload."""

  header: BlockHeader
  """Block header."""
  data: BlockData
  """Transaction data."""
  evidence: BlockEvidence
  """Evidence included in the block."""
  last_commit: Commit
  """Commit for the previous block."""


class BlockResponse(TypedDict):
  """Comet block result."""

  block_id: BlockId
  """Block hash and parts metadata."""
  block: Block
  """Block header, transaction data, evidence, and last commit."""


class EventAttribute(TypedDict):
  """ABCI event attribute."""

  key: str
  """Attribute key."""
  value: str
  """Attribute value."""
  index: bool
  """Whether the attribute is indexed for event queries."""


class Event(TypedDict):
  """ABCI event emitted by block or transaction execution."""

  type: str
  """Event type."""
  attributes: list[EventAttribute]
  """Event attributes."""


class ConsensusBlockParams(TypedDict):
  """Consensus block size and gas parameters."""

  max_bytes: str
  """Maximum block size in bytes."""
  max_gas: str
  """Maximum block gas."""


class ConsensusEvidenceParams(TypedDict):
  """Consensus evidence age and size parameters."""

  max_age_num_blocks: str
  """Maximum evidence age in blocks."""
  max_age_duration: str
  """Maximum evidence age as a duration string."""
  max_bytes: str
  """Maximum evidence size in bytes."""


class ConsensusValidatorParams(TypedDict):
  """Consensus validator key parameters."""

  pub_key_types: list[str]
  """Allowed validator public key types."""


class ConsensusVersionParams(TypedDict, total=False):
  """Consensus version parameters."""

  app: str
  """Application protocol version."""


class ConsensusAbciParams(TypedDict):
  """Consensus ABCI feature parameters."""

  vote_extensions_enable_height: str
  """Height where vote extensions become enabled."""


class ConsensusParams(TypedDict, total=False):
  """Consensus parameter updates emitted by block execution."""

  block: ConsensusBlockParams
  """Block size and gas parameters."""
  evidence: ConsensusEvidenceParams
  """Evidence age and size parameters."""
  validator: ConsensusValidatorParams
  """Validator key parameters."""
  version: ConsensusVersionParams
  """Consensus version parameters."""
  abci: ConsensusAbciParams
  """ABCI feature parameters."""


class ValidatorUpdate(TypedDict):
  """Validator set update emitted by block execution."""

  pub_key: PublicKey
  """Validator public key."""
  power: str
  """Updated validator voting power."""


class BlockResultsResponse(TypedDict, total=False):
  """Comet block results payload."""

  height: str
  """Block height for these execution results."""
  txs_results: list['TxResult'] | None
  """Transaction execution results for transactions in the block."""
  finalize_block_events: list[Event] | None
  """Events emitted while finalizing the block."""
  validator_updates: list[ValidatorUpdate] | None
  """Validator set updates returned by the application."""
  consensus_param_updates: ConsensusParams | None
  """Consensus parameter updates returned by the application."""
  app_hash: str | None
  """Application hash returned by the block execution result."""


class TxResult(TypedDict, total=False):
  """Comet transaction execution result."""

  code: int
  """Application result code."""
  data: str | None
  """Base64-encoded response data, when present."""
  log: str
  """Application log output."""
  info: str
  """Additional application information."""
  gas_wanted: str
  """Requested gas as a string."""
  gas_used: str
  """Consumed gas as a string."""
  events: list[Event]
  """Events emitted by the transaction."""
  codespace: str
  """Application codespace for non-zero result codes."""


class TxProof(TypedDict, total=False):
  """Merkle proof returned by transaction lookup when requested."""

  root_hash: str
  """Proof root hash."""
  data: str
  """Proof data."""
  proof: object
  """Proof operations returned by Comet."""


class TxResponse(TypedDict, total=False):
  """Comet transaction lookup result."""

  hash: str
  """Transaction hash."""
  height: str
  """Block height containing the transaction."""
  index: int
  """Transaction index within the block."""
  tx_result: TxResult
  """Transaction execution result."""
  tx: str
  """Base64-encoded transaction bytes."""
  proof: TxProof
  """Merkle proof for the transaction when requested."""


class TxSearchResponse(TypedDict):
  """Comet transaction search result."""

  txs: list[TxResponse]
  """Matching transactions for the requested page."""
  total_count: str
  """Total number of transactions matching the query."""
