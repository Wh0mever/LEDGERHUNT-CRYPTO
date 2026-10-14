"""Inputs of the deterministic reference tracer: known tokens, bridge contracts, event ABIs,
LayerZero endpoint ids, exchange hot-wallet labels and every heuristic threshold.

Nothing here is specific to case-001 except what a real investigation would also have as
input: a small registry of bridge contracts / aggregators with their sources, and a list of
labelled exchange hot wallets with the source of each label. The tracer never hard-codes
case addresses beyond the starting TXID it is given.

Every entry carries a ``source`` string so the report can say where it came from. Sources
marked "observed in case-001 raw data" were checked against the raw responses stored in
tests/fixtures/case-001/raw/ (contract names returned by the chain / explorer, keccak of the
event signature equal to topic0 of the raw log).
"""

from __future__ import annotations

from ..core.evm import USDT_ERC20, event_topic, function_selector
from ..core.tron import USDT_TRC20

ALGORITHM_VERSION = "baseline-v1"

# ---------------------------------------------------------------- tokens

TOKENS: dict[tuple[str, str], dict[str, object]] = {
    ("tron", USDT_TRC20): {
        "asset": "USDT-TRC20",
        "decimals": 6,
        "source": "Tether USDT on TRON (well-known contract; on-chain name TetherToken)",
    },
    ("ethereum", USDT_ERC20.lower()): {
        "asset": "USDT-ERC20",
        "decimals": 6,
        "source": "Tether USDT on Ethereum (well-known contract; Blockscout name TetherToken)",
    },
}

# ---------------------------------------------------------------- event ABIs
# name -> (canonical signature, [(param name, ABI type, indexed)])
# Only the static types used here plus one dynamic ``string`` are supported by the decoder.

EVENT_ABIS: dict[str, tuple[str, list[tuple[str, str, bool]]]] = {
    "Transfer": (
        "Transfer(address,address,uint256)",
        [("from", "address", True), ("to", "address", True), ("value", "uint256", False)],
    ),
    "Approval": (
        "Approval(address,address,uint256)",
        [("owner", "address", True), ("spender", "address", True), ("value", "uint256", False)],
    ),
    # LayerZero V2 OFT (USDT0 uses it on TRON and Ethereum)
    "OFTSent": (
        "OFTSent(bytes32,uint32,address,uint256,uint256)",
        [("guid", "bytes32", True), ("dstEid", "uint32", False), ("fromAddress", "address", True),
         ("amountSentLD", "uint256", False), ("amountReceivedLD", "uint256", False)],
    ),
    "OFTReceived": (
        "OFTReceived(bytes32,uint32,address,uint256)",
        [("guid", "bytes32", True), ("srcEid", "uint32", False), ("toAddress", "address", True),
         ("amountReceivedLD", "uint256", False)],
    ),
    # Rango Diamond (aggregator) events
    "RangoBridgeInitiated": (
        "RangoBridgeInitiated(address,address,uint256,address,uint256,bool,bool,uint8,uint16,string)",
        [("requestId", "address", True), ("bridgeToken", "address", False), ("bridgeAmount", "uint256", False),
         ("receiver", "address", False), ("destinationChainId", "uint256", False),
         ("hasInterchainMessage", "bool", False), ("hasDestinationSwap", "bool", False),
         ("bridgeId", "uint8", True), ("dAppTag", "uint16", True), ("dAppName", "string", False)],
    ),
    "FeeInfo": (
        "FeeInfo(address,address,uint256,uint8,uint16)",
        [("token", "address", False), ("affiliatorAddress", "address", True), ("affiliateFee", "uint256", False),
         ("feeType", "uint8", True), ("dAppTag", "uint16", True)],
    ),
    "Routed": (
        "Routed(address,address,address,uint256)",
        [("token", "address", True), ("from", "address", True), ("to", "address", True), ("amount", "uint256", False)],
    ),
}

EVENT_SOURCES = {
    "Transfer": "ERC-20 / TRC-20 standard",
    "Approval": "ERC-20 / TRC-20 standard",
    "OFTSent": "LayerZero V2 OFT standard; TronGrid v1 decodes it as OFTSent for the USDT0 contract; "
               "keccak topic equals topic0 of the raw TRON log (observed in case-001 raw data)",
    "OFTReceived": "LayerZero V2 OFT standard; keccak topic equals topic0 of the raw Ethereum log "
                   "(observed in case-001 raw data)",
    "RangoBridgeInitiated": "Blockscout verified ABI of RangoDiamond (decoded method_call); keccak topic equals "
                            "topic0 of the raw log (observed in case-001 raw data)",
    "FeeInfo": "Blockscout verified ABI of RangoDiamond; keccak topic equals raw topic0 (observed)",
    "Routed": "Blockscout verified ABI of RangoRouter; keccak topic equals raw topic0 (observed)",
}

TOPIC_TO_EVENT: dict[str, str] = {event_topic(sig)[2:]: name for name, (sig, _) in EVENT_ABIS.items()}

# Function selectors (calldata) the tracer understands.
SELECTORS: dict[str, str] = {
    function_selector("transfer(address,uint256)"): "transfer",
    function_selector("approve(address,uint256)"): "approve",
    function_selector("transferFrom(address,address,uint256)"): "transferFrom",
    function_selector("send((uint32,bytes32,uint256,uint256,bytes,bytes,bytes),(uint256,uint256),address)"): "oft_send",
}

# ---------------------------------------------------------------- bridges

# Detection is by events (OFTSent / OFTReceived / RangoBridgeInitiated) or by a bridge API that
# recognises a deposit address (NEAR Intents 1Click). The registry names the protocol and the
# expected emitter so the report can say "known contract" vs "unknown emitter of a known event".
BRIDGE_REGISTRY: list[dict[str, str]] = [
    {
        "id": "usdt0_oft_tron",
        "protocol": "USDT0 (LayerZero OFT)",
        "chain": "tron",
        "address": "TFG4wBaDQ8sHWWP1ACeSGnoNR6RRzevLPt",
        "detect": "event OFTSent in the transaction receipt",
        "source": "on-chain contract name 'UsdtOFT' (TronGrid wallet/getcontract); LayerZero Scan pathway "
                  "sender id 'usdt0' for this contract (observed in case-001 raw data)",
    },
    {
        "id": "usdt0_oft_ethereum",
        "protocol": "USDT0 (LayerZero OFT)",
        "chain": "ethereum",
        "address": "0x1F748c76dE468e9D11bd340fA9D5CBADf315dFB0",
        "detect": "event OFTReceived in the destination transaction",
        "source": "Blockscout verified contract name 'UsdtOFT'; LayerZero Scan pathway receiver id 'usdt0' "
                  "(observed in case-001 raw data)",
    },
    {
        "id": "rango_diamond_ethereum",
        "protocol": "Rango (aggregator)",
        "chain": "ethereum",
        "address": "0x69460570c93f9DE5E2edbC3052bf10125f0Ca22d",
        "detect": "event RangoBridgeInitiated in the transaction logs",
        "source": "Blockscout verified contract name 'RangoDiamond' (observed in case-001 raw data)",
    },
    {
        "id": "near_intents_1click",
        "protocol": "NEAR Intents 1Click",
        "chain": "any",
        "address": "",
        "detect": "GET https://1click.chaindefuser.com/v0/status?depositAddress=<address> answers with a swap",
        "source": "NEAR Intents 1Click public status API",
    },
]

# LayerZero V2 endpoint ids used here (docs.layerzero.network deployed endpoints; LayerZero Scan
# reports the same mapping in pathway.sender.chain / pathway.receiver.chain for case-001).
LAYERZERO_EIDS: dict[int, str] = {30101: "ethereum", 30420: "tron"}

# NEAR Intents asset ids look like "nep141:<chain>-<token>.omft.near"; the chain prefix names the network.
NEAR_ASSET_CHAINS: dict[str, str] = {"tron": "tron", "eth": "ethereum"}

# ---------------------------------------------------------------- exchange labels (input)

# Labelled exchange hot wallets. A deposit address is attributed to an exchange only when it
# fully and quickly forwards to one of these (heuristic below), with TXID evidence.
EXCHANGE_HOT_WALLETS: dict[str, dict[str, str]] = {
    "TWBPGLwQw2EbqYLLw1DJnTDt2ZQ9yJW1JJ": {
        "chain": "tron",
        "exchange": "WhiteBIT",
        "source": "TronScan public address tag, taken from the manual case-001 investigation. Stage 2 re-check "
                  "(one keyless TronScan account lookup) got HTTP 401: not re-verified, needs TRONSCAN_API_KEY "
                  "and written consent",
        "status": "TronScan, pending written consent, not stored in any label store",
    },
}

# ---------------------------------------------------------------- thresholds

# Every number the tracer uses to decide something. Amount thresholds are decimal strings.
THRESHOLDS: dict[str, object] = {
    # follow rule: outflows of a holder after the tainted funds arrived
    "follow_window_s": 6 * 3600,          # look for outflows up to 6 h after arrival
    "drain_tolerance_share": "0.001",     # allocation stops once cumulative outflow >= A * (1 - 0.001)
    "follow_min_share": "0.2",            # an allocated outflow >= 20% of A is followed as a branch
    "dust_max_amount": "1",               # allocated outflow <= 1 USDT is dust
    "exact_cut_shares": ["0.01"],         # outflow == A * share rounded to 6 decimals (floor or half-up) -> exact cut
    "remainder_window_s": 3600,           # dust outflows within 1 h after the drain are reported as remainder
    # hub rule (stop): measured over the 24 h after arrival, excluding the tainted arrival itself
    "hub_window_s": 24 * 3600,
    "hub_min_counterparties": 10,         # >= 10 distinct USDT counterparties -> hub
    "hub_volume_multiple": 5,             # or other USDT volume (in + out) >= 5 * A -> hub
    # exchange exit rule for hub outflows
    "exit_max_checks": 10,                # check at most 10 hub outflows (chronological)
    "deposit_window_s": 6 * 3600,         # window of the counterparty's transfers to inspect
    "deposit_forward_min_share": "0.99",  # forwards >= 99% of what it received ("fully")
    "deposit_forward_max_delay_s": 3600,  # within 1 h ("quickly")
    "deposit_max_counterparties": 3,      # few counterparties in the window (deposit-like)
    # theft context (victim side)
    "theft_context_window_s": 120,        # victim transactions within 120 s around the theft
    "incoming_lookback_s": 2 * 3600,      # look back 2 h for the incoming payment before the theft
    # common TRX funder rule
    "funding_min_trx_sun": 1_000_000,     # TRX transfers >= 1 TRX count as funding (plus the activation)
    "funder_inbound_page_limit": 50,      # earliest inbound native transactions inspected per address
    "funder_fanout_page_limit": 200,      # funder's earliest outgoing transactions inspected
    "funder_fanout_service_threshold": 50,  # > 50 distinct TRX recipients there -> looks like a funding service
    # paging limits
    "trc20_page_limit": 200,
    "max_pages": 5,
    "blockscout_max_pages": 5,
}

# Confidence scale of the "likely same operator" link (not a fact).
FUNDER_CONFIDENCE_LEVELS = {1: "low", 2: "medium", 3: "medium-high", 4: "high"}
