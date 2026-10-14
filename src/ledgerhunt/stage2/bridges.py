"""Stage 2 area 'bridges' (decisions 2.3 and 4.2): Ethereum and bridge data sources for case-001.

What it measures (keyless unless a key is configured in .env; key values are never written):
  P0 registry   the official USDT0 deployment list confirms the Legacy Mesh OFT contracts of case-001.
  P1 candidates which public Ethereum JSON-RPC endpoints serve a 3-week-old case-001 receipt and
                eth_getLogs (one attempt each, no retries, so a rate-limited host is not hammered).
  P2 pool       ERC-20 transfers of the launderer transit address 0x4079... (Blockscout) up to a cutoff:
                USDT0 inflows, Rango outflows and a few other txs (spam/dust) for the source comparison.
  P3 eth        per tx: Blockscout (tx, logs, token transfers) vs JSON-RPC receipts from several providers
                (+ Etherscan / paid RPC / Blockscout PRO when keys exist): status, block, logs and ERC-20
                amounts must agree. Calls are paced to spread the latency sample over time.
  P4 usdt0      every USDT0 inflow (TRON -> Ethereum): LayerZero Scan, TRON source tx raw logs
                (OFTSent, PacketSent) and an on-chain fallback without LayerZero Scan: OFTReceived(guid)
                found with eth_getLogs in a time window after the TRON send.
  P5 rango      every Rango outflow: RangoBridgeInitiated / Routed / FeeInfo decoded by us, the route
                (NEAR Intents 1Click deposit address or USDT0 back to TRON), recipient and destination tx,
                TRON payout verified on TronGrid, deposit sweep into the NEAR vault, and fallbacks without
                1Click (payout-wallet transfers filtered by the receiver prefix or amount) and without
                LayerZero Scan (TRON OFTReceived events by guid).
  P6 burst      a short burst (default 20 requests per host) at the shared default rate.
  P7 etherscan  one keyless Etherscan call (documents the key requirement); not-measured list.
  P8 case-001   every bridge fact of the fixture compared with what we observed (never adjusted).

Run: python -m ledgerhunt stage2 bridges [--pace-s 5 --burst-n 20 --other-txs 6 --skip-burst]
Replay: python -m ledgerhunt stage2 bridges --replay   (pacing sleeps are skipped in replay)
"""

from __future__ import annotations

import argparse
import json
import os
import statistics
import time
from datetime import datetime, timezone
from decimal import Decimal
from typing import Any, Callable

from ..core.config import has_secret, secrets_presence
from ..core.evm import USDT_ERC20, strip0x, to_checksum_address
from ..core.http import RecordingClient, RequestFailed
from ..core.paths import repo_root
from ..core.results import start_run
from ..core.tron import USDT_TRC20, USDT_TRC20_HEX, format_amount, hex_to_b58, sun_to_trx
from ..sources import (
    BlockscoutClient,
    EthRpcClient,
    JsonRpcError,
    LayerZeroScanClient,
    NearIntentsClient,
    SourceError,
    TronGridClient,
)
from ..sources import bridges_decode as bd
from ..sources.bridges_clients import (
    BlockscoutEtherscanApi,
    BlockscoutTokens,
    EtherscanV2Client,
    RangoStatusClient,
    Usdt0DeploymentsClient,
    find_usdt0_contract,
)
from ..sources.layerzero_scan import messages as lz_messages

AREA = "bridges"

# ---------------------------------------------------------------- case-001 constants

TRANSIT_ETH = "0x4079047990917F3150353FBd8A13b05b6286926d"
CASE_LZ_SRC_TX = "b49b0157d5327ca4b25683d2100d77c9b0c2c13584fdc96deea17a8c93057f6f"
CASE_LZ_DST_TX = "0x8ea2bdef31c5eefb89569a239d5208cdff99a7bb9a7fe2f48c168b16b9d73c15"
CASE_LZ_GUID = "0xba20537a6870e4ba2538d40ae16772f198f02d88d24c47d016b53863a7337bf8"
CASE_RANGO_TX = "0x41bac088520409376e60709fd7114b7b3d670abeedfb01a68b7ee42a84ec515a"
CASE_NEAR_SWEEP_TX = "0x224f3859d03f8a26fc697b7b2978d4a701cf3db1d280dbd911e18b508b54e762"
CASE_DEPOSIT = "0xdA392553ec3602D3e650a725f847C10d04E122C0"
USDT_ETH = USDT_ERC20.lower()
USDT_TRON_LOG = "0x" + USDT_TRC20_HEX[2:]  # TRON log address form of the USDT contract

# Public Ethereum JSON-RPC endpoints tried on 2026-10-14 (P1). The sampled set (P3) was chosen
# from those that served the 3-week-old case-001 receipt and eth_getLogs without a key.
RPC_CANDIDATES: list[tuple[str, str]] = [
    ("eth_publicnode", "https://ethereum-rpc.publicnode.com"),
    ("eth_drpc", "https://eth.drpc.org"),
    ("eth_tenderly", "https://mainnet.gateway.tenderly.co"),
    ("eth_nodies", "https://ethereum-public.nodies.app"),
    ("eth_mevblocker", "https://rpc.mevblocker.io"),
    ("eth_1rpc", "https://1rpc.io/eth"),
    ("eth_flashbots", "https://rpc.flashbots.net"),
    ("eth_cloudflare", "https://cloudflare-eth.com"),
    ("eth_llamarpc", "https://eth.llamarpc.com"),
    ("eth_ankr", "https://rpc.ankr.com/eth"),
    ("eth_blockpi", "https://ethereum.blockpi.network/v1/rpc/public"),
    ("eth_merkle", "https://eth.merkle.io"),
    ("eth_onfinality", "https://eth.api.onfinality.io/public"),
]
SAMPLED_RPCS = ("eth_publicnode", "eth_drpc", "eth_tenderly")
GETLOGS_CHUNK = 50  # largest range every sampled public RPC accepted (1rpc: max 50; PublicNode: archive refused)
ETH_ANCHOR_BLOCK = 26_000_000  # fixed anchor for the timestamp -> block estimate (deterministic requests)
ETH_SLOT_S = 12

FIXTURE_PATH = "tests/fixtures/case-001/case-001-ground-truth.json"


# ---------------------------------------------------------------- helpers


class Tap:
    """Wraps a RecordingClient and keeps the last HttpResult, so callers can read response headers."""

    def __init__(self, inner: RecordingClient) -> None:
        self.inner = inner
        self.last = None

    def request(self, *a: Any, **kw: Any):
        self.last = None
        res = self.inner.request(*a, **kw)
        self.last = res
        return res

    def get(self, url: str, **kw: Any):
        return self.request("GET", url, **kw)

    def post(self, url: str, **kw: Any):
        return self.request("POST", url, **kw)

    def __getattr__(self, name: str) -> Any:
        return getattr(self.inner, name)


def _rl_headers(headers: dict[str, str] | None) -> dict[str, str]:
    if not headers:
        return {}
    return {k: v for k, v in headers.items()
            if k.startswith(("x-ratelimit", "ratelimit", "x-rate-limit", "retry-after"))}


def _utc(ts: int | float | str | None) -> str | None:
    """Epoch seconds/ms or ISO text -> 'YYYY-MM-DD HH:MM:SS' (UTC), the fixture's format."""
    if ts is None:
        return None
    if isinstance(ts, str):
        if ts.isdigit():
            ts = int(ts)
        else:
            try:
                return datetime.fromisoformat(ts.replace("Z", "+00:00")).astimezone(timezone.utc).strftime("%Y-%m-%d %H:%M:%S")
            except ValueError:
                return ts
    ts = float(ts)
    if ts > 1e11:
        ts /= 1000.0
    return datetime.fromtimestamp(ts, tz=timezone.utc).strftime("%Y-%m-%d %H:%M:%S")


def _epoch(text: str) -> int:
    return int(datetime.fromisoformat(text.replace("Z", "+00:00")).timestamp())


def _amt(raw: int | str | None) -> str | None:
    return None if raw is None else format_amount(int(raw))


def _pct(values: list[float], p: float) -> float | None:
    if not values:
        return None
    v = sorted(values)
    if len(v) == 1:
        return round(v[0], 1)
    k = (len(v) - 1) * p / 100.0
    lo = int(k)
    hi = min(lo + 1, len(v) - 1)
    return round(v[lo] + (v[hi] - v[lo]) * (k - lo), 1)


def _tron_addr(word_or_hex: str | None) -> str | None:
    if not word_or_hex:
        return None
    return hex_to_b58("41" + strip0x(word_or_hex)[-40:])


class Calls:
    """Runs one logical source call, records a row (status, semantic ok, latency, rate-limit headers)."""

    def __init__(self, tap: Tap, replay: bool) -> None:
        self.tap = tap
        self.rows: list[dict[str, Any]] = []
        self.replay = replay

    def run(self, phase: str, source: str, op: str, target: str, fn: Callable[[], Any], *,
            check: Callable[[Any], bool] | None = None, expect: str = "ok") -> tuple[Any, dict[str, Any]]:
        """Call fn(); return (result | None, row). expect: 'ok' or 'not_found' (negative control)."""
        t0 = time.perf_counter()
        row: dict[str, Any] = {"phase": phase, "source": source, "op": op, "target": target, "expect": expect,
                               "ts_utc": datetime.now(timezone.utc).strftime("%Y-%m-%dT%H:%M:%SZ")}
        res = None
        fetched = None
        err = None
        try:
            res = fn()
            pages = getattr(res, "pages", None)
            fetched = pages[-1] if pages else res
        except JsonRpcError as exc:
            fetched, err = exc.fetched, f"jsonrpc_error: {str(exc.error)[:200]}"
        except SourceError as exc:
            fetched, err = exc.fetched, f"source_error: {str(exc)[:200]}"
        except RequestFailed as exc:
            err = f"no_response: {exc.error_class}"
        last = self.tap.last
        status = getattr(fetched, "status", None) if fetched is not None else (last.status if last else None)
        ok = False
        if err is None and res is not None:
            try:
                ok = bool(check(res)) if check else (200 <= (status or 0) < 300)
            except Exception as exc:  # noqa: BLE001 - a failed check is a data problem: record it
                ok, err = False, f"check_failed: {type(exc).__name__}: {str(exc)[:150]}"
        if expect == "not_found":
            ok = status == 404
        pages = getattr(res, "pages", None)
        row.update({
            "http_status": status,
            "ok": ok,
            "error": err,
            "pages": len(pages) if pages else (1 if fetched is not None else 0),
            "latency_ms": [p.latency_ms for p in pages] if pages else getattr(fetched, "latency_ms", None),
            "attempts": getattr(fetched, "attempts", None),
            "from_replay": getattr(fetched, "from_replay", None),
            "wall_ms": round((time.perf_counter() - t0) * 1000, 1),
            "rl_headers": _rl_headers(last.headers if last is not None else None),
            "refs": [p.ref_dict() for p in pages] if pages
            else ([fetched.ref_dict()] if fetched is not None and fetched.ref else []),
        })
        self.rows.append(row)
        return (res if err is None else None), row

    def pace(self, seconds: float) -> None:
        if seconds > 0 and not self.replay:
            time.sleep(seconds)


# ---------------------------------------------------------------- argument parsing


def _parse(extra: list[str]) -> argparse.Namespace:
    p = argparse.ArgumentParser(prog="stage2 bridges", add_help=False)
    p.add_argument("--pace-s", type=float, default=5.0, help="pause between per-tx sample rounds (live only)")
    p.add_argument("--burst-n", type=int, default=20, help="requests per host in the controlled burst (max 20)")
    p.add_argument("--skip-burst", action="store_true")
    p.add_argument("--skip-candidates", action="store_true")
    p.add_argument("--other-txs", type=int, default=6, help="non-bridge txs of the transit address in the P3 sample")
    p.add_argument("--pool-cutoff", default="2026-10-14T00:00:00Z", help="ignore transit-address txs after this UTC time")
    p.add_argument("--window-blocks", type=int, default=150, help="eth_getLogs window after the TRON send (~30 min)")
    p.add_argument("--payout-window-s", type=int, default=1200, help="TRON payout search window after the Rango tx")
    p.add_argument("--payout-pages", type=int, default=2, help="max TronGrid pages per payout search")
    a, _unknown = p.parse_known_args(extra)
    a.burst_n = max(0, min(20, a.burst_n))
    return a


def _spread(items: list[Any], n: int) -> list[Any]:
    """n items spread evenly over a sorted list (deterministic)."""
    if n <= 0 or not items:
        return []
    if len(items) <= n:
        return list(items)
    step = len(items) / n
    return [items[int(i * step)] for i in range(n)]


# ---------------------------------------------------------------- main


def run(args: argparse.Namespace) -> int:
    opts = _parse(list(getattr(args, "extra", None) or []))
    mode = os.environ.get("LEDGERHUNT_HTTP_MODE", "record")
    replay = mode == "replay"
    keys = secrets_presence()
    keyed = {
        "etherscan": has_secret("ETHERSCAN_API_KEY"),
        "blockscout_pro": has_secret("BLOCKSCOUT_API_KEY"),
        "eth_rpc_paid": has_secret("ETH_RPC_URL"),
        "near_intents_partner_key": has_secret("NEAR_INTENTS_JWT"),
        "rango": has_secret("RANGO_API_KEY"),
        "trongrid": has_secret("TRONGRID_API_KEY"),
    }
    config = {
        "purpose": "decisions 2.3/4.2: Ethereum and bridge sources for case-001 (USDT0/LayerZero, Rango, NEAR Intents 1Click)",
        "options": vars(opts),
        "transit_address": TRANSIT_ETH,
        "rpc_candidates": [{"provider": n, "url": u} for n, u in RPC_CANDIDATES],
        "sampled_rpcs": list(SAMPLED_RPCS),
        "getlogs_chunk_blocks": GETLOGS_CHUNK,
        "eth_anchor_block": ETH_ANCHOR_BLOCK,
        "keys_used": keyed,
        "notes": [
            "keyless measurements use the shared default rate limits (never raised for keyless hosts)",
            "latency_ms is the final attempt; in replay mode it is the recorded value",
            "repeated identical requests (burst) replay the latest recorded response",
        ],
    }
    ctx = start_run(AREA, config=config)
    fixture = json.loads((repo_root() / FIXTURE_PATH).read_text(encoding="utf-8"))
    steps = {s["step"]: s for s in fixture["transactions"]}

    tap = Tap(ctx.http_client())
    calls = Calls(tap, replay)

    tg = TronGridClient(tap)  # key from .env when present; keyless otherwise (1 rps shared)
    bs = BlockscoutClient(tap, api_key=None)
    bs_api = BlockscoutEtherscanApi(tap, api_key=None)
    bs_tok = BlockscoutTokens(tap)
    lz = LayerZeroScanClient(tap)
    ni = NearIntentsClient(tap, jwt=None)
    rpcs: dict[str, EthRpcClient] = {n: EthRpcClient(tap, url=u, provider=n) for n, u in RPC_CANDIDATES if n in SAMPLED_RPCS}
    if keyed["eth_rpc_paid"]:
        rpcs["eth_rpc_paid"] = EthRpcClient.from_env("ETH_RPC_URL", tap, provider="eth_rpc_paid")
    es = EtherscanV2Client(tap)
    bs_pro = BlockscoutClient(tap, base_url="https://api.blockscout.com/1", provider="blockscout_pro") if keyed["blockscout_pro"] else None
    ni_keyed = NearIntentsClient(tap, provider="near_intents_1click_keyed") if keyed["near_intents_partner_key"] else None
    rango = RangoStatusClient(tap)
    pn = rpcs["eth_publicnode"]

    out: dict[str, Any] = {"not_measured": [], "discrepancies": [], "observations": []}

    # ------------------------------------------------------------ P0 registry
    print(f"[{AREA}] P0 USDT0 deployments registry", flush=True)
    dep, _ = calls.run("registry", "usdt0_docs", "api/deployments", "-", Usdt0DeploymentsClient(tap).deployments)
    registry: dict[str, Any] = {"fetched": dep is not None}
    if dep is not None:
        for chain, addr in bd.USDT0_LEGACY_MESH.items():
            registry[f"{chain}_oft"] = find_usdt0_contract(dep.data, addr)
    ctx.write_json("raw/registry.json", registry)

    # ------------------------------------------------------------ P1 RPC candidates
    candidates: list[dict[str, Any]] = []
    if not opts.skip_candidates:
        print(f"[{AREA}] P1 public Ethereum RPC candidates", flush=True)
        ctap = Tap(ctx.http_client(max_attempts=1))  # one attempt: no retry/penalty loops on strict hosts
        ccalls = Calls(ctap, replay)
        for name, url in RPC_CANDIDATES:
            c = EthRpcClient(ctap, url=url, provider=name)
            row: dict[str, Any] = {"provider": name, "url": url}
            _, rr = ccalls.run("candidates", name, "eth_chainId", "-", lambda: c.call("eth_chainId"),
                               check=lambda f: f.data == "0x1")
            row["chain_id"] = {"ok": rr["ok"], "status": rr["http_status"], "error": rr["error"], "rl": rr["rl_headers"]}
            if rr["ok"]:
                _, rr = ccalls.run("candidates", name, "eth_getTransactionReceipt", CASE_LZ_DST_TX,
                                   lambda: c.get_transaction_receipt(CASE_LZ_DST_TX),
                                   check=lambda f: isinstance(f.data, dict) and f.data.get("status") == "0x1"
                                   and len(f.data.get("logs") or []) == 3)
                row["receipt_3w_old"] = {"ok": rr["ok"], "status": rr["http_status"], "error": rr["error"]}
                got: dict[str, Any] = {}

                def getlogs() -> Any:
                    f = c.get_logs(from_block=26025690, to_block=26025739, address=bd.USDT0_LEGACY_MESH["ethereum"],
                                   topics=[bd.TOPIC_OFT_RECEIVED, CASE_LZ_GUID])
                    got["n"] = len(f.data or [])
                    return f

                _, rr = ccalls.run("candidates", name, "eth_getLogs_50_blocks", CASE_LZ_GUID, getlogs,
                                   check=lambda f: len(f.data or []) == 1
                                   and (f.data[0].get("transactionHash") or "").lower() == CASE_LZ_DST_TX)
                row["getlogs_50"] = {"ok": rr["ok"], "status": rr["http_status"], "error": rr["error"],
                                     "logs_returned": got.get("n"),
                                     "false_negative": rr["error"] is None and got.get("n") == 0}
            row["usable"] = bool(row.get("receipt_3w_old", {}).get("ok") and row.get("getlogs_50", {}).get("ok"))
            candidates.append(row)
        # PublicNode refuses historical eth_getLogs (archive); record the evidence once with a wider range.
        _, rr = ccalls.run("candidates", "eth_publicnode", "eth_getLogs_1000_blocks", CASE_LZ_GUID,
                           lambda: EthRpcClient(ctap, provider="eth_publicnode").get_logs(
                               from_block=26025209, to_block=26026208, address=bd.USDT0_LEGACY_MESH["ethereum"],
                               topics=[bd.TOPIC_OFT_RECEIVED, CASE_LZ_GUID]))
        out["publicnode_getlogs_1000"] = {"ok": rr["ok"], "status": rr["http_status"], "error": rr["error"]}
        ctx.write_jsonl("raw/rpc_candidates.jsonl", candidates)
        ctx.write_jsonl("raw/calls_candidates.jsonl", ccalls.rows)

    # ------------------------------------------------------------ P2 pool
    print(f"[{AREA}] P2 transit-address pool (Blockscout)", flush=True)
    cutoff = _epoch(opts.pool_cutoff)
    pool_res, _ = calls.run("pool", "blockscout_eth", "address_token_transfers", TRANSIT_ETH,
                            lambda: bs.address_token_transfers(TRANSIT_ETH, type="ERC-20", max_pages=5),
                            check=lambda p: p.complete)
    pool_items = [it for it in (pool_res.rows if pool_res else []) if _epoch(it["timestamp"]) < cutoff]
    usdt0_in: dict[str, dict[str, Any]] = {}
    rango_out: dict[str, dict[str, Any]] = {}
    pool_txs: dict[str, dict[str, Any]] = {}
    for it in pool_items:
        txh = it["transaction_hash"].lower()
        frm = ((it.get("from") or {}).get("hash") or "").lower()
        to = ((it.get("to") or {}).get("hash") or "").lower()
        tok = ((it.get("token") or {}).get("address_hash") or (it.get("token") or {}).get("address") or "").lower()
        rec = {"tx": txh, "timestamp": it["timestamp"], "block": it.get("block_number"), "from": frm, "to": to,
               "token": tok, "value": (it.get("total") or {}).get("value"), "log_index": it.get("log_index")}
        pool_txs.setdefault(txh, {"tx": txh, "timestamp": it["timestamp"], "block": it.get("block_number"), "kinds": []})
        if tok == USDT_ETH and frm == bd.USDT0_LEGACY_MESH["ethereum"].lower() and to == TRANSIT_ETH.lower():
            usdt0_in[txh] = rec
            pool_txs[txh]["kinds"].append("usdt0_in")
        elif tok == USDT_ETH and frm == TRANSIT_ETH.lower() and to == bd.RANGO_DIAMOND_ETH.lower():
            rango_out[txh] = rec
            pool_txs[txh]["kinds"].append("rango_out")
    others = sorted((h for h, r in pool_txs.items() if not r["kinds"]), key=lambda h: pool_txs[h]["timestamp"])
    sample = sorted(set(usdt0_in) | set(rango_out) | set(_spread(others, opts.other_txs)),
                    key=lambda h: pool_txs[h]["timestamp"])
    sample.append(CASE_NEAR_SWEEP_TX)
    pool_txs.setdefault(CASE_NEAR_SWEEP_TX, {"tx": CASE_NEAR_SWEEP_TX, "timestamp": None, "block": None,
                                             "kinds": ["near_sweep_case001"]})
    for h in pool_txs:
        pool_txs[h]["in_sample"] = h in sample
    ctx.write_jsonl("raw/pool.jsonl", sorted(pool_txs.values(), key=lambda r: (r["timestamp"] or "9")))
    print(f"[{AREA}]   pool: {len(pool_txs)} txs, usdt0_in={len(usdt0_in)}, rango_out={len(rango_out)}, "
          f"sample={len(sample)}", flush=True)

    # ------------------------------------------------------------ P3 Ethereum source agreement + latency sample
    print(f"[{AREA}] P3 Ethereum source agreement on {len(sample)} txs (pace {opts.pace_s}s)", flush=True)
    eth: dict[str, dict[str, Any]] = {}
    agreement_rows: list[dict[str, Any]] = []
    token_info: dict[str, Any] = {}
    for i, txh in enumerate(sample):
        if i:
            calls.pace(opts.pace_s)
        d: dict[str, Any] = {}
        f, _ = calls.run("eth", "blockscout_eth", "transaction", txh, lambda: bs.transaction(txh),
                         check=lambda f: (f.data or {}).get("hash", "").lower() == txh)
        d["bs_tx"] = f.data if f else None
        p, _ = calls.run("eth", "blockscout_eth", "transaction_logs", txh, lambda: bs.transaction_logs(txh, max_pages=20))
        d["bs_logs_complete"] = bool(p and p.complete)
        d["bs_logs"] = [bd.norm_log(x, source="blockscout") for x in p.rows] if p else None
        d["bs_logs_raw"] = p.rows if p else None
        p, _ = calls.run("eth", "blockscout_eth", "transaction_token_transfers", txh,
                         lambda: bs.transaction_token_transfers(txh, max_pages=20))
        d["bs_transfers_complete"] = bool(p and p.complete)
        d["bs_transfers"] = bd.blockscout_token_transfers(p.rows) if p else None
        if bs_pro is not None:
            calls.run("eth", "blockscout_pro", "transaction_logs", txh, lambda: bs_pro.transaction_logs(txh, max_pages=20))
        for name, cli in rpcs.items():
            f, _ = calls.run("eth", name, "eth_getTransactionReceipt", txh, lambda: cli.get_transaction_receipt(txh),
                             check=lambda f: isinstance(f.data, dict) and f.data.get("transactionHash", "").lower() == txh)
            d[f"rcpt_{name}"] = f.data if f else None
        if es.has_key:
            f, _ = calls.run("eth", "etherscan_v2", "eth_getTransactionReceipt", txh, lambda: es.tx_receipt(txh),
                             check=lambda f: isinstance((f.data or {}).get("result"), dict))
            d["rcpt_etherscan_v2"] = (f.data or {}).get("result") if f else None
        eth[txh] = d
        agreement_rows.append(_compare_eth(txh, pool_txs[txh]["kinds"], d))
        # explain token-transfer gaps (Blockscout omits some tokens): look up the missing tokens' reputation
        tcmp = agreement_rows[-1].get("blockscout_transfers_vs_rpc_logs") or {}
        for tok in tcmp.get("missing_tokens", [])[:3]:
            if tok not in token_info and len(token_info) < 8:
                tf, _ = calls.run("eth", "blockscout_eth", "token", tok, lambda: bs_tok.token(tok))
                td = (tf.data or {}) if tf else {}
                token_info[tok] = {"http_status": tf.status if tf else None, "name": td.get("name"), "symbol": td.get("symbol"),
                                   "type": td.get("type"), "reputation": td.get("reputation"), "is_scam": td.get("is_scam")}
    for r in agreement_rows:
        tc = r.get("blockscout_transfers_vs_rpc_logs") or {}
        if tc.get("missing_tokens"):
            tc["missing_token_info"] = {t: token_info.get(t) for t in tc["missing_tokens"]}
    ctx.write_jsonl("raw/eth_agreement.jsonl", agreement_rows)

    def receipt_of(txh: str) -> tuple[dict[str, Any] | None, str | None]:
        """First non-null receipt among the sampled sources (PublicNode first)."""
        d = eth.get(txh) or {}
        for k in [f"rcpt_{n}" for n in rpcs] + ["rcpt_etherscan_v2"]:
            if isinstance(d.get(k), dict):
                return d[k], k[5:]
        return None, None

    # ------------------------------------------------------------ P4 USDT0 / LayerZero inflows (TRON -> Ethereum)
    print(f"[{AREA}] P4 USDT0/LayerZero inflows: {len(usdt0_in)}", flush=True)
    anchor_cache: dict[int, int] = {}

    def block_ts(n: int) -> int | None:
        if n in anchor_cache:
            return anchor_cache[n]
        f, _ = calls.run("usdt0", "eth_publicnode", "eth_getBlockByNumber", str(n), lambda: pn.get_block_by_number(n),
                         check=lambda f: isinstance(f.data, dict))
        if not f:
            return None
        anchor_cache[n] = int(f.data["timestamp"], 16)
        return anchor_cache[n]

    def estimate_block(ts: int) -> tuple[int | None, int]:
        """Ethereum block at or just before ``ts`` from a fixed anchor and 12 s slots (PublicNode)."""
        a_ts = block_ts(ETH_ANCHOR_BLOCK)
        if a_ts is None:
            return None, 0
        est = ETH_ANCHOR_BLOCK + (ts - a_ts) // ETH_SLOT_S
        for it in range(1, 6):
            bt = block_ts(est)
            if bt is None:
                return None, it
            if bt <= ts and ts - bt < 2 * ETH_SLOT_S:
                return est, it
            step = (ts - bt) // ETH_SLOT_S
            est += step if step != 0 else (-1 if bt > ts else 1)
        return est, 5

    usdt0_rows: list[dict[str, Any]] = []
    for dst_tx in sorted(usdt0_in, key=lambda h: usdt0_in[h]["timestamp"]):
        flow: dict[str, Any] = {"dst_tx": dst_tx, "case001": dst_tx == CASE_LZ_DST_TX,
                                "eth_transfer": {**usdt0_in[dst_tx], "value": _amt(usdt0_in[dst_tx]["value"])}}
        f, _ = calls.run("usdt0", "layerzero_scan", "messages_by_tx(dst)", dst_tx, lambda: lz.messages_by_tx(dst_tx),
                         check=lambda f: len(lz_messages(f)) == 1)
        msgs = lz_messages(f) if f else []
        lzs = bd.lz_message_summary(msgs[0]) if msgs else None
        flow["lz_by_dst"] = lzs
        src_tx = (lzs or {}).get("src_tx")
        if flow["case001"]:
            f2, _ = calls.run("usdt0", "layerzero_scan", "messages_by_tx(src)", CASE_LZ_SRC_TX,
                              lambda: lz.messages_by_tx(CASE_LZ_SRC_TX), check=lambda f: len(lz_messages(f)) == 1)
            f3, _ = calls.run("usdt0", "layerzero_scan", "message_by_guid", CASE_LZ_GUID,
                              lambda: lz.message_by_guid(CASE_LZ_GUID), check=lambda f: len(lz_messages(f)) == 1)
            s2 = bd.lz_message_summary(lz_messages(f2)[0]) if f2 and lz_messages(f2) else None
            s3 = bd.lz_message_summary(lz_messages(f3)[0]) if f3 and lz_messages(f3) else None
            flow["lz_by_src_equals_by_dst"] = s2 == lzs
            flow["lz_by_guid_equals_by_dst"] = s3 == lzs
            src_tx = src_tx or "0x" + CASE_LZ_SRC_TX
        tron = None
        if src_tx:
            tron = _tron_oft_tx(calls, tg, strip0x(src_tx), direction="send")
            if flow["case001"]:
                tx_tron = strip0x(src_tx)
                f, _ = calls.run("usdt0", "trongrid", "transaction_events", tx_tron, lambda: tg.transaction_events(tx_tron),
                                 check=lambda f: bool((f.data or {}).get("data")))
                if tron is not None:
                    tron["trongrid_decoded_events"] = [
                        {"event_name": e.get("event_name"), "contract": e.get("contract_address"), "event_index": e.get("event_index")}
                        for e in ((f.data or {}).get("data") or [])] if f else None
        flow["tron_source"] = tron
        # On-chain fallback without LayerZero Scan: OFTReceived(guid) on the Ethereum OFT via eth_getLogs.
        fb: dict[str, Any] = {}
        if tron and tron.get("oft_sent") and tron["oft_sent"]["dst_chain"] == "ethereum":
            guid = tron["oft_sent"]["guid"]
            est, iters = estimate_block(tron["block_ts"])
            fb["estimated_start_block"] = est
            fb["estimate_iterations"] = iters
            if est is not None:
                lo, hi = est - 2, est + opts.window_blocks
                fb["window"] = [lo, hi]
                fbr, _ = calls.run("usdt0", "blockscout_eth", "api getLogs(OFTReceived,guid)", guid,
                                   lambda: bs_api.get_logs(from_block=lo, to_block=hi, address=bd.USDT0_LEGACY_MESH["ethereum"],
                                                           topic0=bd.TOPIC_OFT_RECEIVED, topic1=guid),
                                   check=lambda f: isinstance((f.data or {}).get("result"), list))
                res = (fbr.data or {}).get("result") if fbr else None
                fb["blockscout_api"] = {**(_fallback_hits(res if isinstance(res, list) else None) or {"found": False, "error": True}),
                                        "requests": 1}
                for name in [n for n in rpcs if n != "eth_publicnode"]:
                    fb[name] = _getlogs_chunked(calls, name, rpcs[name], guid, lo, hi)
                if es.has_key:
                    fe, _ = calls.run("usdt0", "etherscan_v2", "getLogs(OFTReceived,guid)", guid,
                                      lambda: es.get_logs(from_block=lo, to_block=hi, address=bd.USDT0_LEGACY_MESH["ethereum"],
                                                          topic0=bd.TOPIC_OFT_RECEIVED, topic1=guid),
                                      check=lambda f: isinstance((f.data or {}).get("result"), list))
                    r = (fe.data or {}).get("result") if fe else None
                    fb["etherscan_v2"] = {**(_fallback_hits(r if isinstance(r, list) else None) or {"found": False, "error": True}),
                                          "requests": 1}
        flow["onchain_fallback"] = fb
        rc, rc_src = receipt_of(dst_tx)
        if isinstance(rc, dict):
            logs = [bd.norm_log(x, source="rpc") for x in rc.get("logs") or []]
            recv = next((x for x in (bd.decode_oft_received(lg) for lg in logs) if x), None)
            flow["eth_oft_received"] = {**recv, "amount": _amt(recv["amount_received_ld"]), "receipt_source": rc_src} if recv else None
            flow["eth_block"] = int(rc["blockNumber"], 16)
        lz_to = ((lzs or {}).get("payload") or {}).get("send_to")
        recv = flow.get("eth_oft_received") or {}
        os_ = (tron or {}).get("oft_sent") or {}
        fb_txs = {v.get("tx") for v in fb.values() if isinstance(v, dict) and v.get("found")}
        flow["verdict"] = {
            "exit_recognised_on_tron": bool((tron or {}).get("recognised_as_usdt0")),
            "recipient_via_lz_scan": lz_to,
            "recipient_via_onchain": recv.get("to"),
            "dst_tx_via_lz_scan": (lzs or {}).get("dst_tx"),
            "dst_tx_via_onchain_fallback": sorted(t for t in fb_txs if t),
            "recipient_agrees": bool(lz_to and recv.get("to") and lz_to.lower() == recv["to"].lower()
                                     and recv["to"].lower() == TRANSIT_ETH.lower()),
            "dst_tx_agrees": bool((lzs or {}).get("dst_tx") and fb_txs == {(lzs or {}).get("dst_tx", "").lower()}),
            "amount_agrees": bool(os_ and recv and os_["amount_received_ld"] == recv["amount_received_ld"]
                                  == int(usdt0_in[dst_tx]["value"]) == ((lzs or {}).get("payload") or {}).get("amount_sd")),
            "amount_sent": os_.get("amount_sent"),
            "amount_received": os_.get("amount_received"),
            "bridge_fee": _amt(os_["amount_sent_ld"] - os_["amount_received_ld"]) if os_ else None,
            "bridge_fee_bps": (str((Decimal(os_["amount_sent_ld"] - os_["amount_received_ld"]) * 10000
                                    / Decimal(os_["amount_sent_ld"])).quantize(Decimal("0.01"))) if os_ else None),
            "delivery_s": ((lzs or {}).get("dst_timestamp") - (lzs or {}).get("src_timestamp"))
            if (lzs or {}).get("dst_timestamp") and (lzs or {}).get("src_timestamp") else None,
            "tron_sender": os_.get("from"),
        }
        usdt0_rows.append(flow)
    ctx.write_jsonl("raw/usdt0_flows.jsonl", usdt0_rows)

    # ------------------------------------------------------------ P5 Rango outflows
    print(f"[{AREA}] P5 Rango outflows: {len(rango_out)}", flush=True)
    rango_rows: list[dict[str, Any]] = []
    deposit_addresses: list[str] = []
    for txh in sorted(rango_out, key=lambda h: rango_out[h]["timestamp"]):
        is_case = txh == CASE_RANGO_TX
        flow = {"tx": txh, "case001": is_case, "timestamp_utc": _utc(rango_out[txh]["timestamp"]),
                "into_rango": {**rango_out[txh], "value": _amt(rango_out[txh]["value"])}}
        d = eth.get(txh) or {}
        rc, rc_src = receipt_of(txh)
        flow["receipt_source"] = rc_src
        rpc_logs = [bd.norm_log(x, source="rpc") for x in (rc or {}).get("logs") or []] if isinstance(rc, dict) else []
        ev_rpc = next((x for x in (bd.decode_rango_bridge_initiated(lg) for lg in rpc_logs) if x), None)
        ev_bs = next((x for x in (bd.decode_rango_bridge_initiated(lg) for lg in d.get("bs_logs") or []) if x), None)
        bs_decoded = next((bd.blockscout_decoded_params(it) for it in d.get("bs_logs_raw") or []
                           if (it.get("topics") or [None])[0] == bd.TOPIC_RANGO_BRIDGE_INITIATED), None)
        routed = [x for x in (bd.decode_rango_routed(lg) for lg in rpc_logs) if x]
        fees = [x for x in (bd.decode_rango_fee_info(lg) for lg in rpc_logs) if x]
        oft_sent_eth = next((x for x in (bd.decode_oft_sent(lg, chain="ethereum") for lg in rpc_logs) if x), None)
        transfers = bd.erc20_transfers_from_logs(rpc_logs)
        ev = ev_rpc or ev_bs
        flow["rango_event"] = _jsonable_event(ev)
        flow["rango_event_same_on_rpc_and_blockscout_logs"] = (ev_rpc == ev_bs) if ev_rpc and ev_bs else None
        flow["rango_event_vs_blockscout_decoder"] = _cmp_blockscout_decoded(ev, bs_decoded)
        flow["routed"] = [{**r, "amount": _amt(r["amount"])} for r in routed]
        flow["fee_info"] = [{**x, "affiliate_fee": _amt(x["affiliate_fee"])} for x in fees]
        affiliates = {x["affiliator"].lower() for x in fees}
        out_of_diamond = [t for t in transfers if t["token"] == USDT_ETH and t["from"] == bd.RANGO_DIAMOND_ETH.lower()
                          and t["to"] not in affiliates]
        forward = routed[-1]["to"] if routed else (to_checksum_address(out_of_diamond[-1]["to"]) if out_of_diamond else None)
        flow["forward_address"] = forward
        flow["forward_amount"] = _amt(routed[-1]["amount"]) if routed else (_amt(out_of_diamond[-1]["value"]) if out_of_diamond else None)
        flow["exit_recognised"] = bool(ev and ev["emitter"].lower() == bd.RANGO_DIAMOND_ETH.lower())
        flow["destination_chain"] = (ev or {}).get("destination_chain_ascii")
        prefix = (ev or {}).get("receiver_ascii")
        flow["receiver_prefix"] = prefix if bd.tron_prefix_candidates(prefix) else None
        route = "usdt0" if oft_sent_eth or (forward or "").lower() == bd.USDT0_LEGACY_MESH["ethereum"].lower() else None
        if is_case:
            calls.run("rango", "layerzero_scan", "messages_by_tx(rango tx) negative control", txh,
                      lambda: lz.messages_by_tx(txh), expect="not_found")
            calls.run("rango", "near_intents_1click", "status(transit) negative control", TRANSIT_ETH,
                      lambda: ni.status(TRANSIT_ETH), expect="not_found")
        oc = None
        recipient = None
        dest_txs: list[str] = []
        if route == "usdt0":
            flow["oft_sent_eth"] = {**oft_sent_eth, "amount_sent": _amt(oft_sent_eth["amount_sent_ld"]),
                                    "amount_received": _amt(oft_sent_eth["amount_received_ld"])} if oft_sent_eth else None
            f, _ = calls.run("rango", "layerzero_scan", "messages_by_tx(eth src)", txh, lambda: lz.messages_by_tx(txh),
                             check=lambda f: len(lz_messages(f)) == 1)
            lzs = bd.lz_message_summary(lz_messages(f)[0]) if f and lz_messages(f) else None
            flow["lz"] = lzs
            recipient = ((lzs or {}).get("payload") or {}).get("send_to")
            if lzs and lzs.get("dst_tx"):
                dest_txs = [strip0x(lzs["dst_tx"])]
                flow["tron_destination"] = _tron_oft_tx(calls, tg, dest_txs[0], direction="receive")
            # fallback without LayerZero Scan: TRON OFTReceived events of the USDT0 OFT filtered by guid
            if oft_sent_eth:
                t0 = _epoch(rango_out[txh]["timestamp"]) * 1000
                p, _ = calls.run("rango", "trongrid", "contract_events(OFTReceived, window)", bd.USDT0_LEGACY_MESH["tron"],
                                 lambda: tg.contract_events(bd.USDT0_LEGACY_MESH["tron"], event_name="OFTReceived",
                                                            min_block_timestamp=t0, max_block_timestamp=t0 + 1800 * 1000,
                                                            order_by="block_timestamp,asc", limit=200, max_pages=opts.payout_pages),
                                 check=lambda p: True)
                evs = p.rows if p else []
                hits = [e for e in evs if strip0x(str((e.get("result") or {}).get("guid", ""))).lower() == strip0x(oft_sent_eth["guid"]).lower()]
                flow["tron_fallback_without_lz"] = {
                    "events_scanned": len(evs), "complete": bool(p and p.complete), "pages": len(p.pages) if p else 0,
                    "hits": [{"tx": e.get("transaction_id"), "to": _tron_addr((e.get("result") or {}).get("toAddress")),
                              "amount": _amt((e.get("result") or {}).get("amountReceivedLD")),
                              "timestamp_utc": _utc(e.get("block_timestamp"))} for e in hits]}
        elif forward:
            # 404 is a valid answer ("not a 1Click deposit address"), not a source failure
            f, _ = calls.run("rango", "near_intents_1click", "status", forward, lambda: ni.status(forward),
                             check=lambda f: (f.status == 200 and bd.oneclick_summary(f.data) is not None) or f.status == 404)
            oc = bd.oneclick_summary(f.data) if f and f.status == 200 else None
            flow["oneclick_http_status"] = f.status if f else None
            if ni_keyed is not None:
                calls.run("rango", "near_intents_1click_keyed", "status", forward, lambda: ni_keyed.status(forward))
            if oc:
                route = "near_intents_1click"
                deposit_addresses.append(forward)
                recipient = oc.get("recipient")
                dest_txs = list(oc.get("destination_chain_tx_hashes") or [])
            # deposit sweep into the NEAR Intents vault (on-chain recognition without 1Click)
            p, _ = calls.run("rango", "blockscout_eth", "address_token_transfers(deposit)", forward,
                             lambda: bs.address_token_transfers_page(forward, type="ERC-20"),
                             check=lambda f: isinstance((f.data or {}).get("items"), list))
            sweeps, foreign = [], []
            for it in ((p.data or {}).get("items") or []) if p else []:
                if ((it.get("from") or {}).get("hash") or "").lower() != forward.lower():
                    continue
                tok = ((it.get("token") or {}).get("address_hash") or (it.get("token") or {}).get("address") or "").lower()
                rec = {"tx": it["transaction_hash"], "to": (it.get("to") or {}).get("hash"), "token": tok,
                       "token_symbol": (it.get("token") or {}).get("symbol"), "value": (it.get("total") or {}).get("value"),
                       "timestamp_utc": _utc(it.get("timestamp"))}
                if tok == USDT_ETH:
                    sweeps.append({**rec, "value": _amt(rec["value"])})
                else:
                    foreign.append(rec)  # e.g. look-alike token transfers (address poisoning)
            flow["deposit_sweeps"] = sweeps
            flow["deposit_non_usdt_transfers"] = foreign
            flow["swept_to_near_vault"] = any((s["to"] or "").lower() == bd.NEAR_INTENTS_VAULT_ETH.lower() for s in sweeps)
        flow["route"] = route or ("unknown" if forward else None)
        flow["oneclick"] = oc
        # TRON payout verification (1Click route)
        payouts: list[dict[str, Any]] = []
        if route == "near_intents_1click":
            for dtx in dest_txs:
                payouts.extend(_tron_payout(calls, tg, dtx))
        flow["tron_payouts"] = payouts
        # Fallback without 1Click: payout-wallet transfers in a window (receiver prefix, else amount band)
        fbk: dict[str, Any] = {}
        dest_asset = str((oc or {}).get("destination_asset"))
        if route == "near_intents_1click" and "tron-" in dest_asset:
            t0 = _epoch(rango_out[txh]["timestamp"]) * 1000
            p, _ = calls.run("rango", "trongrid", "trc20_transfers(payout wallet, window)", bd.NEAR_INTENTS_TRON_PAYOUT_OBSERVED,
                             lambda: tg.trc20_transfers(bd.NEAR_INTENTS_TRON_PAYOUT_OBSERVED, only_from=True, min_timestamp=t0,
                                                        max_timestamp=t0 + opts.payout_window_s * 1000, limit=200,
                                                        max_pages=opts.payout_pages),
                             check=lambda p: True)
            rows = p.rows if p else []
            fwd_raw = int(Decimal(flow["forward_amount"]) * 10**6) if flow.get("forward_amount") else None
            if flow["receiver_prefix"]:
                method = "receiver_prefix"
                cands = [r for r in rows if str(r.get("to", "")).startswith(flow["receiver_prefix"])]
            else:
                method = "amount_band_99_100pct"
                cands = [r for r in rows if fwd_raw and fwd_raw * 99 // 100 <= int(r.get("value", 0)) <= fwd_raw]
            fbk = {"method": method, "payout_wallet_assumed": bd.NEAR_INTENTS_TRON_PAYOUT_OBSERVED,
                   "window_s": opts.payout_window_s, "transfers_scanned": len(rows), "complete": bool(p and p.complete),
                   "pages": len(p.pages) if p else 0,
                   "candidates": [{"tx": r["transaction_id"], "to": r["to"], "value": _amt(r["value"]),
                                   "timestamp_utc": _utc(r["block_timestamp"])} for r in cands]}
            fbk["unique_match"] = len(cands) == 1
            fbk["agrees_with_1click"] = bool(len(cands) == 1 and cands[0]["transaction_id"] in dest_txs)
        flow["payout_fallback_without_1click"] = fbk
        if rango.has_key and ev and ev.get("request_uuid"):
            f, _ = calls.run("rango", "rango_api", "basic/status", txh, lambda: rango.status(ev["request_uuid"], txh))
            flow["rango_status_api"] = f.data if f else None
        payout = payouts[0] if payouts else {}
        tdst = flow.get("tron_destination") or {}
        diff = None
        if payout.get("asset") == "USDT" and oc and oc.get("amount_out"):
            diff = format(Decimal(payout["value"]) - Decimal(_amt(oc["amount_out"])), "f")
        flow["verdict"] = {
            "route": flow["route"],
            "exit_recognised_on_ethereum": flow["exit_recognised"],
            "bridge_id": (ev or {}).get("bridge_id"),
            "destination_chain": flow["destination_chain"],
            "recipient": recipient,
            "recipient_matches_event_prefix": bool(recipient and prefix and str(recipient).startswith(prefix)),
            "dst_txs": dest_txs,
            "payout_to_matches_recipient": bool(payout and recipient and payout["to"] == recipient)
            or bool(tdst.get("oft_received") and tdst["oft_received"].get("to") == recipient),
            "payout_asset": payout.get("asset") or ("USDT" if tdst.get("oft_received") else None),
            "payout_value": payout.get("value") or ((tdst.get("oft_received") or {}).get("amount")),
            "oneclick_amount_out": (oc or {}).get("amount_out_formatted"),
            "payout_minus_1click_amount_out": diff,
            "payout_wallet": payout.get("from"),
            "fallback_method": fbk.get("method"),
            "fallback_unique_match": fbk.get("unique_match"),
            "fallback_agrees_with_1click": fbk.get("agrees_with_1click"),
            "tron_fallback_without_lz_hits": len((flow.get("tron_fallback_without_lz") or {}).get("hits") or []) if route == "usdt0" else None,
        }
        rango_rows.append(flow)
    ctx.write_jsonl("raw/rango_flows.jsonl", rango_rows)

    # ------------------------------------------------------------ P6 controlled burst
    burst_rows: list[dict[str, Any]] = []
    if not opts.skip_burst and opts.burst_n > 0:
        print(f"[{AREA}] P6 controlled burst: {opts.burst_n} requests per host at the default shared rate", flush=True)
        txs = list(sample)
        lz_txs = sorted(usdt0_in) or [CASE_LZ_DST_TX]
        deps = deposit_addresses or [CASE_DEPOSIT]
        targets: list[tuple[str, Callable[[int], Any], Callable[[Any], bool]]] = [
            ("blockscout_eth", lambda i: bs.transaction(txs[i % len(txs)]), lambda f: f.status == 200),
            ("layerzero_scan", lambda i: lz.messages_by_tx(lz_txs[i % len(lz_txs)]), lambda f: len(lz_messages(f)) == 1),
            ("near_intents_1click", lambda i: ni.status(deps[i % len(deps)]), lambda f: f.status == 200),
        ] + [
            # eth_getTransactionByHash (not the receipt): distinct request keys, so replay of P3 receipts stays faithful
            (n, (lambda c: (lambda i: c.get_transaction_by_hash(txs[i % len(txs)])))(c),
             lambda f: isinstance(f.data, dict) and bool(f.data.get("hash")))
            for n, c in rpcs.items()]
        for name, fn, chk in targets:
            t_start = time.perf_counter()
            first = len(calls.rows)
            for i in range(opts.burst_n):
                calls.run("burst", name, "burst", str(i), (lambda fn=fn, i=i: fn(i)), check=chk)
            rows = calls.rows[first:]
            rem = [int(v) for r in rows for k, v in r["rl_headers"].items() if "remaining" in k and str(v).isdigit()]
            burst_rows.append({
                "source": name, "requests": len(rows), "ok": sum(r["ok"] for r in rows),
                "not_ok_targets": [txs[int(r["target"]) % len(txs)] if name.startswith("eth_") else r["target"]
                                   for r in rows if not r["ok"]],
                "http_429": sum(1 for r in rows if r["http_status"] == 429),
                "retries": sum(max(0, (r["attempts"] or 1) - 1) for r in rows),
                "wall_s": round(time.perf_counter() - t_start, 2) if not replay else None,
                "rate_limit_headers_seen": sorted({k for r in rows for k in r["rl_headers"]}),
                "remaining_min": min(rem) if rem else None,
                "remaining_first_last": [rem[0], rem[-1]] if rem else None,
            })
        ctx.write_jsonl("raw/burst.jsonl", burst_rows)

    # ------------------------------------------------------------ P7 Etherscan keyless check / not measured
    f, rr = calls.run("etherscan", "etherscan_v2_keyless", "eth_getTransactionReceipt (no key)", CASE_LZ_DST_TX,
                      lambda: EtherscanV2Client(tap, api_key=None, provider="etherscan_v2_keyless").tx_receipt(CASE_LZ_DST_TX),
                      check=lambda f: isinstance((f.data or {}).get("result"), dict))
    out["etherscan_keyless"] = {"http_status": rr["http_status"], "ok": rr["ok"],
                                "body_status": (f.data or {}).get("status") if f else None,
                                "body_message": (f.data or {}).get("message") if f else None,
                                "body_result": str((f.data or {}).get("result"))[:160] if f else None}
    if not es.has_key:
        out["not_measured"].append({"what": "Etherscan API v2 с ключом", "why": "не измерено: нет ключа ETHERSCAN_API_KEY",
                                    "needed": "ключ Etherscan в .env"})
    if not keyed["eth_rpc_paid"]:
        out["not_measured"].append({"what": "платный Ethereum RPC", "why": "не измерено: нет ETH_RPC_URL",
                                    "needed": "URL платного провайдера в .env (переменная ETH_RPC_URL)"})
    if not keyed["blockscout_pro"]:
        out["not_measured"].append({"what": "Blockscout PRO API (api.blockscout.com, с ключом)",
                                    "why": "не измерено: нет BLOCKSCOUT_API_KEY",
                                    "needed": "бесплатный ключ PRO API (dev.blockscout.com) в .env"})
    if not keyed["near_intents_partner_key"]:
        out["not_measured"].append({"what": "статус 1Click с ключом партнёра",
                                    "why": "не измерено: нет NEAR_INTENTS_JWT",
                                    "needed": "ключ из partners.near-intents.org в .env"})
    if not keyed["rango"]:
        out["not_measured"].append({"what": "Rango status API (/basic/status)", "why": "не измерено: нет RANGO_API_KEY",
                                    "needed": "ключ Rango (выдаётся через тикет в Discord) в .env под именем RANGO_API_KEY"})

    ctx.write_jsonl("raw/calls.jsonl", calls.rows)

    # ------------------------------------------------------------ P8 case-001 fixture comparison
    checks = _case001_checks(steps, usdt0_rows, rango_rows, eth, receipt_of)
    ctx.write_json("case001_checks.json", checks)
    for c in checks:
        if c["match"] is False and c["kind"] == "fact":
            out["discrepancies"].append(c)
        elif c["kind"] == "observation":
            out["observations"].append(c)

    # ------------------------------------------------------------ summary
    metrics = tap.inner.metrics
    null_receipts = {n: [r["tx"] for r in agreement_rows if r.get(n, {}).get("available") is False]
                     for n in [*rpcs, *(["etherscan_v2"] if es.has_key else [])]}
    summary = {
        "date_utc": ctx.config["date_utc"],
        "http_mode": mode,
        "keys_present": {k: v for k, v in keys.items() if k != "ANTHROPIC_API_KEY"},
        "keys_used": keyed,
        "registry": {k: bool(v) for k, v in registry.items() if k.endswith("_oft")},
        "rpc_candidates": [{"provider": c["provider"], "usable": c["usable"],
                            "chain_id_status": c["chain_id"]["status"],
                            "receipt": (c.get("receipt_3w_old") or {}).get("ok"),
                            "getlogs_50": (c.get("getlogs_50") or {}).get("ok"),
                            "getlogs_false_negative": (c.get("getlogs_50") or {}).get("false_negative"),
                            "error": c["chain_id"]["error"] or (c.get("receipt_3w_old") or {}).get("error")
                            or (c.get("getlogs_50") or {}).get("error")} for c in candidates],
        "publicnode_getlogs_1000": out.get("publicnode_getlogs_1000"),
        "pool": {"txs": len(pool_txs), "usdt0_in": len(usdt0_in), "rango_out": len(rango_out), "sample": len(sample),
                 "cutoff": opts.pool_cutoff},
        "eth_agreement": {
            "txs": len(agreement_rows),
            "all_agree": sum(1 for r in agreement_rows if r["all_agree"]),
            "disagreements": [{"tx": r["tx"], "reasons": r["reasons"]} for r in agreement_rows if not r["all_agree"]],
            "null_receipts": null_receipts,
            "blockscout_transfer_gaps": sum(1 for r in agreement_rows if (r.get("blockscout_transfers_vs_rpc_logs") or {}).get("missing_tokens")),
            "token_info": token_info,
        },
        "usdt0": {
            "flows": len(usdt0_rows),
            "exit_recognised_on_tron": sum(r["verdict"]["exit_recognised_on_tron"] for r in usdt0_rows),
            "recipient_agrees": sum(r["verdict"]["recipient_agrees"] for r in usdt0_rows),
            "dst_tx_agrees_onchain_vs_lz": sum(r["verdict"]["dst_tx_agrees"] for r in usdt0_rows),
            "amount_agrees": sum(r["verdict"]["amount_agrees"] for r in usdt0_rows),
            "fees_bps": sorted({r["verdict"]["bridge_fee_bps"] for r in usdt0_rows if r["verdict"]["bridge_fee_bps"]}),
            "delivery_s": [r["verdict"]["delivery_s"] for r in usdt0_rows],
            "tron_senders": sorted({r["verdict"]["tron_sender"] for r in usdt0_rows if r["verdict"]["tron_sender"]}),
            "fallback_sources_found": {k: sum(1 for r in usdt0_rows if (r["onchain_fallback"].get(k) or {}).get("found"))
                                       for k in ["blockscout_api", *[n for n in rpcs if n != "eth_publicnode"], "etherscan_v2"]},
            "fallback_requests": {k: sum((r["onchain_fallback"].get(k) or {}).get("requests", 0) for r in usdt0_rows)
                                  for k in ["blockscout_api", *[n for n in rpcs if n != "eth_publicnode"], "etherscan_v2"]},
            "block_estimate_iterations": [r["onchain_fallback"].get("estimate_iterations") for r in usdt0_rows],
        },
        "rango": {
            "flows": len(rango_rows),
            "routes": {k: sum(1 for r in rango_rows if str(r["route"]) == k) for k in sorted({str(r["route"]) for r in rango_rows})},
            "bridge_initiated_event": sum(1 for r in rango_rows if r["exit_recognised"]),
            "to_tron_by_event": sum(1 for r in rango_rows if r["destination_chain"] == "TRON"),
            "bridge_ids_by_route": sorted({f"{r['verdict']['bridge_id']}:{r['route']}" for r in rango_rows
                                           if r["verdict"]["bridge_id"] is not None}),
            "recipients": sorted({r["verdict"]["recipient"] for r in rango_rows if r["verdict"]["recipient"]}),
            "recipient_matches_prefix": sum(r["verdict"]["recipient_matches_event_prefix"] for r in rango_rows),
            "payout_matches_recipient": sum(r["verdict"]["payout_to_matches_recipient"] for r in rango_rows),
            "payout_minus_1click_amount_out": [r["verdict"]["payout_minus_1click_amount_out"] for r in rango_rows
                                               if r["verdict"]["payout_minus_1click_amount_out"] is not None],
            "payout_wallets": sorted({r["verdict"]["payout_wallet"] for r in rango_rows if r["verdict"]["payout_wallet"]}),
            "fallback_unique_match": sum(1 for r in rango_rows if r["verdict"]["fallback_unique_match"]),
            "fallback_agrees_with_1click": sum(1 for r in rango_rows if r["verdict"]["fallback_agrees_with_1click"]),
            "fallback_attempted": sum(1 for r in rango_rows if r["verdict"]["fallback_method"]),
            "swept_to_near_vault": sum(1 for r in rango_rows if r.get("swept_to_near_vault")),
            "deposit_poisoning_transfers": sum(len(r.get("deposit_non_usdt_transfers") or []) for r in rango_rows),
            "ours_vs_blockscout_decoder_equal": sum(1 for r in rango_rows if (r["rango_event_vs_blockscout_decoder"] or {}).get("equal")),
            "events_compared_with_blockscout": sum(1 for r in rango_rows if r["rango_event_vs_blockscout_decoder"] is not None),
        },
        "burst": burst_rows,
        "per_source": _source_stats(calls.rows, metrics),
        "case001_checks": {"total": sum(1 for c in checks if c["kind"] == "fact"),
                           "match": sum(1 for c in checks if c["kind"] == "fact" and c["match"] is True),
                           "mismatch": sum(1 for c in checks if c["kind"] == "fact" and c["match"] is False),
                           "unverified": sum(1 for c in checks if c["kind"] == "fact" and c["match"] is None)},
        "observations": out["observations"],
        "etherscan_keyless": out.get("etherscan_keyless"),
        "not_measured": out["not_measured"],
        "discrepancies": out["discrepancies"],
        "requests_total": sum(len(c.metrics) for c in ctx._clients),
    }
    ctx.finish(summary, _markdown(summary))
    print(f"[{AREA}] done: {ctx.rel_dir}", flush=True)
    return 0


# ---------------------------------------------------------------- per-phase helpers


def _compare_eth(txh: str, kinds: list[str], d: dict[str, Any]) -> dict[str, Any]:
    """Compare Blockscout and every receipt source for one tx; list the reasons of any disagreement."""
    cmp: dict[str, Any] = {"tx": txh, "kinds": kinds}
    bs_tx = d.get("bs_tx") or {}
    cmp["blockscout_status"] = bs_tx.get("status")
    cmp["blockscout_block"] = bs_tx.get("block_number") or bs_tx.get("block")
    cmp["blockscout_timestamp"] = bs_tx.get("timestamp")
    cmp["blockscout_logs_complete"] = d.get("bs_logs_complete")
    cmp["blockscout_transfers_complete"] = d.get("bs_transfers_complete")
    receipts = {k[5:]: v for k, v in d.items() if k.startswith("rcpt_")}
    ref_name = next((n for n, rc in receipts.items() if isinstance(rc, dict)), None)
    ref_logs = [bd.norm_log(x, source="rpc") for x in receipts[ref_name].get("logs") or []] if ref_name else None
    cmp["reference_receipt"] = ref_name
    reasons: list[str] = []
    statuses, blocks = set(), set()
    for src, rc in receipts.items():
        if not isinstance(rc, dict):
            cmp[src] = {"available": False}
            reasons.append(f"{src}: no receipt (null or error)")
            continue
        logs = [bd.norm_log(x, source="rpc") for x in rc.get("logs") or []]
        c = bd.compare_log_sets(ref_logs, logs) if ref_logs is not None and src != ref_name else None
        cmp[src] = {"available": True, "status": rc.get("status"),
                    "block": int(rc["blockNumber"], 16) if rc.get("blockNumber") else None, "logs": len(logs),
                    "logs_vs_reference": c}
        statuses.add(rc.get("status"))
        blocks.add(cmp[src]["block"])
        if c is not None and not c["equal"]:
            reasons.append(f"{src}: logs differ from {ref_name}")
    if len(statuses) > 1:
        reasons.append(f"receipt status differs: {sorted(map(str, statuses))}")
    if len(blocks) > 1:
        reasons.append(f"block differs: {sorted(map(str, blocks))}")
    if statuses and cmp["blockscout_status"] != {"0x1": "ok", "0x0": "error"}.get(next(iter(statuses))):
        reasons.append(f"blockscout status {cmp['blockscout_status']} vs receipt {sorted(map(str, statuses))}")
    if blocks and cmp["blockscout_block"] is not None and int(cmp["blockscout_block"]) not in blocks:
        reasons.append("blockscout block differs")
    if ref_logs is not None and d.get("bs_logs") is not None:
        if d.get("bs_logs_complete"):
            cmp["blockscout_logs_vs_rpc"] = bd.compare_log_sets(ref_logs, d["bs_logs"])
            if not cmp["blockscout_logs_vs_rpc"]["equal"]:
                reasons.append("blockscout logs differ from receipt")
        else:
            reasons.append("blockscout logs pagination incomplete (cap)")
    if ref_logs is not None and d.get("bs_transfers") is not None:
        rpc_tr = bd.erc20_transfers_from_logs(ref_logs)
        tc = bd.compare_transfer_sets(rpc_tr, d["bs_transfers"])
        if not tc["equal"]:
            bs_keys = {(r["log_index"], r["token"]) for r in d["bs_transfers"]}
            missing = [r for r in rpc_tr if (r["log_index"], r["token"]) not in bs_keys]
            tc["missing_count"] = len(missing)
            tc["missing_tokens"] = sorted({r["token"] for r in missing})
            tc["usdt_missing"] = sum(1 for r in missing if r["token"] == USDT_ETH)
            reasons.append(f"blockscout token-transfers omit {len(missing)} transfer(s) of {len(tc['missing_tokens'])} token(s)")
        cmp["blockscout_transfers_vs_rpc_logs"] = tc
    if ref_name is None:
        reasons.append("no receipt from any source")
    cmp["reasons"] = reasons
    cmp["all_agree"] = not reasons
    return cmp


def _tron_oft_tx(calls: Calls, tg: TronGridClient, txid: str, *, direction: str) -> dict[str, Any] | None:
    """TRON tx of the USDT0 OFT from raw logs: OFTSent/PacketSent (send) or OFTReceived (receive)."""
    f, _ = calls.run("usdt0" if direction == "send" else "rango", "trongrid", "gettransactioninfobyid", txid,
                     lambda: tg.get_transaction_info_by_id(txid), check=lambda f: bool((f.data or {}).get("log")))
    if not f:
        return None
    info = f.data
    logs = [bd.norm_log(x, source="tron", default_index=i) for i, x in enumerate(info.get("log") or [])]
    contract = hex_to_b58(info["contract_address"]) if info.get("contract_address") else None
    usdt = [t for t in bd.erc20_transfers_from_logs(logs) if t["token"] == USDT_TRON_LOG]
    out: dict[str, Any] = {
        "tx": txid,
        "block": info.get("blockNumber"),
        "timestamp_utc": _utc(info.get("blockTimeStamp")),
        "block_ts": (info.get("blockTimeStamp") or 0) // 1000,
        "contract": contract,
        "result": (info.get("receipt") or {}).get("result"),
        "fee_sun": info.get("fee"),
        "usdt_trc20_transfers": [{"from": _tron_addr(t["from"]), "to": _tron_addr(t["to"]), "value": _amt(t["value"])} for t in usdt],
    }
    if direction == "send":
        oft_sent = next((x for x in (bd.decode_oft_sent(lg, chain="tron") for lg in logs) if x), None)
        out["oft_sent"] = {**oft_sent, "amount_sent": _amt(oft_sent["amount_sent_ld"]),
                           "amount_received": _amt(oft_sent["amount_received_ld"])} if oft_sent else None
        out["packet_sent"] = next((x for x in (bd.decode_packet_sent(lg) for lg in logs) if x), None)
        out["recognised_as_usdt0"] = bool(oft_sent and contract == bd.USDT0_LEGACY_MESH["tron"]
                                          and oft_sent["oft"] == bd.USDT0_LEGACY_MESH["tron"] and oft_sent["dst_chain"])
    else:
        recv = next((x for x in (bd.decode_oft_received(lg, chain="tron") for lg in logs) if x), None)
        out["oft_received"] = {**recv, "amount": _amt(recv["amount_received_ld"])} if recv else None
    return out


def _tron_payout(calls: Calls, tg: TronGridClient, dtx: str) -> list[dict[str, Any]]:
    """USDT Transfer events of a TRON payout tx; for a native TRX payout, the TransferContract of the tx."""
    f, _ = calls.run("rango", "trongrid", "transaction_events(payout)", dtx, lambda: tg.transaction_events(dtx),
                     check=lambda f: (f.data or {}).get("success") is not False)
    out = []
    for e in ((f.data or {}).get("data") or []) if f else []:
        if e.get("event_name") == "Transfer" and e.get("contract_address") == USDT_TRC20:
            r = e.get("result") or {}
            out.append({"tx": dtx, "asset": "USDT", "block": e.get("block_number"), "timestamp_utc": _utc(e.get("block_timestamp")),
                        "from": _tron_addr(r.get("from")), "to": _tron_addr(r.get("to")), "value": _amt(r.get("value"))})
    if out:
        return out
    f, _ = calls.run("rango", "trongrid", "gettransactionbyid(payout)", dtx, lambda: tg.get_transaction_by_id(dtx),
                     check=lambda f: bool((f.data or {}).get("raw_data")))
    for c in (((f.data or {}).get("raw_data") or {}).get("contract") or []) if f else []:
        if c.get("type") == "TransferContract":
            v = (c.get("parameter") or {}).get("value") or {}
            out.append({"tx": dtx, "asset": "TRX", "block": None,
                        "timestamp_utc": _utc(((f.data or {}).get("raw_data") or {}).get("timestamp")),
                        "from": v.get("owner_address"), "to": v.get("to_address"), "value": sun_to_trx(v.get("amount", 0))})
    return out


def _getlogs_chunked(calls: Calls, name: str, cli: EthRpcClient, guid: str, lo: int, hi: int) -> dict[str, Any]:
    hits: list[dict[str, Any]] | None = []
    chunks = 0
    for start in range(lo, hi + 1, GETLOGS_CHUNK):
        end = min(hi, start + GETLOGS_CHUNK - 1)
        chunks += 1
        fr, _ = calls.run("usdt0", name, "eth_getLogs(OFTReceived,guid)", f"{guid}@{start}",
                          lambda: cli.get_logs(from_block=start, to_block=end, address=bd.USDT0_LEGACY_MESH["ethereum"],
                                               topics=[bd.TOPIC_OFT_RECEIVED, guid]),
                          check=lambda f: isinstance(f.data, list))
        if fr is None:
            hits = None
            break
        hits.extend(fr.data)
        if fr.data:
            break
    return {**(_fallback_hits(hits) or {"found": False, "error": True}), "requests": chunks}


def _fallback_hits(rows: list[dict[str, Any]] | None) -> dict[str, Any] | None:
    if rows is None:
        return None
    hits = []
    for r in rows:
        lg = bd.norm_log(r, source="rpc")
        dec = bd.decode_oft_received(lg)
        if dec:
            bn = r.get("blockNumber")
            hits.append({"tx": (r.get("transactionHash") or "").lower(),
                         "block": int(bn, 16) if isinstance(bn, str) and bn.startswith("0x") else bn,
                         "to": dec["to"], "amount": _amt(dec["amount_received_ld"])})
    return {"found": len(hits) == 1, "hits": hits, **({"tx": hits[0]["tx"], "to": hits[0]["to"]} if len(hits) == 1 else {})}


def _jsonable_event(ev: dict[str, Any] | None) -> dict[str, Any] | None:
    if not ev:
        return None
    return {**ev, "bridge_amount": _amt(ev["bridge_amount"])}


def _cmp_blockscout_decoded(ev: dict[str, Any] | None, bs_dec: dict[str, Any] | None) -> dict[str, Any] | None:
    """Our RangoBridgeInitiated decode vs Blockscout's ABI decode (string values)."""
    if not ev or not bs_dec:
        return None
    pairs = {
        "requestId": ev["request_id"], "bridgeToken": ev["bridge_token"], "bridgeAmount": str(ev["bridge_amount"]),
        "receiver": ev["receiver_evm"], "destinationChainId": str(ev["destination_chain_id"]),
        "hasInterchainMessage": str(ev["has_interchain_message"]).lower(),
        "hasDestinationSwap": str(ev["has_destination_swap"]).lower(), "bridgeId": str(ev["bridge_id"]),
        "dAppTag": str(ev["dapp_tag"]), "dAppName": ev["dapp_name"],
    }
    diffs = {k: {"ours": v, "blockscout": bs_dec.get(k)} for k, v in pairs.items() if str(bs_dec.get(k)) != str(v)}
    return {"equal": not diffs, "diffs": diffs}


def _source_stats(rows: list[dict[str, Any]], metrics: list[dict[str, Any]]) -> list[dict[str, Any]]:
    """Per provider: semantic success share (expected-ok calls), HTTP latency p50/p95/max, 429s, retries."""
    out = []
    providers = sorted({r["source"] for r in rows} | {m["provider"] for m in metrics})
    for prov in providers:
        rs = [r for r in rows if r["source"] == prov and r["expect"] == "ok"]
        neg = [r for r in rows if r["source"] == prov and r["expect"] == "not_found"]
        ms = [m for m in metrics if m["provider"] == prov]
        lat = [m["latency_ms"] for m in ms if m["status"] is not None]
        out.append({
            "provider": prov,
            "calls": len(rs),
            "calls_ok": sum(1 for r in rs if r["ok"]),
            "success_share": round(sum(1 for r in rs if r["ok"]) / len(rs), 4) if rs else None,
            "negative_controls": len(neg),
            "negative_controls_ok": sum(1 for r in neg if r["ok"]),
            "http_requests": len(ms),
            "http_2xx": sum(1 for m in ms if m["status"] and 200 <= m["status"] < 300),
            "http_429_seen": sum(1 for m in ms for s in (m["attempt_statuses"] or []) if s == 429),
            "retries": sum(max(0, (m["attempts"] or 1) - 1) for m in ms),
            "latency_ms_p50": _pct(lat, 50),
            "latency_ms_p95": _pct(lat, 95),
            "latency_ms_max": round(max(lat), 1) if lat else None,
            "latency_ms_mean": round(statistics.fmean(lat), 1) if lat else None,
            "replayed": sum(1 for m in ms if m["from_replay"]),
            "first_ts_utc": min((m["ts_utc"] for m in ms), default=None),
            "last_ts_utc": max((m["ts_utc"] for m in ms), default=None),
            "rate_limit_headers": sorted({k for r in rows if r["source"] == prov for k in r["rl_headers"]}),
            "rate_limit_values": {k: sorted({str(r["rl_headers"][k]) for r in rows if r["source"] == prov and k in r["rl_headers"]})[:5]
                                  for k in sorted({k for r in rows if r["source"] == prov for k in r["rl_headers"]})
                                  if "remaining" not in k},
            "remaining_min": min((int(v) for r in rows if r["source"] == prov for k, v in r["rl_headers"].items()
                                  if "remaining" in k and str(v).isdigit()), default=None),
        })
    return out


def _check(fact: str, fixture: Any, observed: Any, source: str, *, step: int | None = None,
           kind: str = "fact") -> dict[str, Any]:
    if observed is None:
        match = None
    elif isinstance(fixture, str) and isinstance(observed, str) and fixture.startswith(("0x", "0X")):
        match = fixture.lower() == observed.lower()
    else:
        match = str(fixture) == str(observed)
    return {"step": step, "kind": kind, "fact": fact, "fixture": fixture, "observed": observed, "source": source,
            "match": match}


def _case001_checks(steps: dict[int, dict[str, Any]], usdt0_rows: list[dict[str, Any]], rango_rows: list[dict[str, Any]],
                    eth: dict[str, dict[str, Any]], receipt_of: Callable[[str], tuple[Any, Any]]) -> list[dict[str, Any]]:
    out: list[dict[str, Any]] = []
    s12, s14, s15, s16, s17 = steps[12], steps[14], steps[15], steps[16], steps[17]
    u = next((r for r in usdt0_rows if r["case001"]), None)
    if u is None:
        return [_check("case-001 USDT0 flow found in Blockscout pool", True, None, "blockscout_eth")]
    tron = u.get("tron_source") or {}
    os_ = tron.get("oft_sent") or {}
    pk = tron.get("packet_sent") or {}
    lzs = u.get("lz_by_dst") or {}
    recv = u.get("eth_oft_received") or {}
    lzf = s12["layerzero"]
    fb = u["verdict"]["dst_tx_via_onchain_fallback"]
    et = u.get("eth_transfer") or {}
    out += [
        _check("TRON bridge-out block", s12["block"], tron.get("block"), "TronGrid walletsolidity/gettransactioninfobyid", step=12),
        _check("TRON bridge-out time", s12["timestamp_utc"], tron.get("timestamp_utc"), "TronGrid gettransactioninfobyid", step=12),
        _check("TRON bridge-out contract (USDT0 OFT)", s12["to"], tron.get("contract"), "TronGrid gettransactioninfobyid", step=12),
        _check("TRON bridge-out sender", s12["from"], os_.get("from"), "OFTSent (raw TRON log, own decoder)", step=12),
        _check("TRON bridge-out amount", s12["amount"], os_.get("amount_sent"), "OFTSent.amountSentLD", step=12),
        _check("LayerZero guid", lzf["guid"], os_.get("guid"), "OFTSent topic1 (raw TRON log)", step=12),
        _check("LayerZero guid", lzf["guid"], lzs.get("guid"), "LayerZero Scan /messages/tx/{dst}", step=12),
        _check("srcEid", lzf["srcEid"], pk.get("src_eid"), "PacketSent (raw TRON log)", step=12),
        _check("srcEid", lzf["srcEid"], lzs.get("src_eid"), "LayerZero Scan", step=12),
        _check("dstEid", lzf["dstEid"], os_.get("dst_eid"), "OFTSent.dstEid", step=12),
        _check("dstEid", lzf["dstEid"], lzs.get("dst_eid"), "LayerZero Scan", step=12),
        _check("sendTo", lzf["sendTo"], (pk.get("oft_message") or {}).get("send_to"), "PacketSent message (raw TRON log)", step=12),
        _check("sendTo", lzf["sendTo"], (lzs.get("payload") or {}).get("send_to"), "LayerZero Scan payload", step=12),
        _check("sendTo", lzf["sendTo"], recv.get("to"), "OFTReceived.toAddress (Ethereum receipt)", step=12),
        _check("amountReceivedLD", lzf["amountReceivedLD"], os_.get("amount_received"), "OFTSent.amountReceivedLD", step=12),
        _check("amountReceivedLD", lzf["amountReceivedLD"], recv.get("amount"), "OFTReceived.amountReceivedLD", step=12),
        _check("LayerZero status", lzf["status"], lzs.get("status"), "LayerZero Scan", step=12),
        _check("Ethereum bridge-in tx", s14["txid"], lzs.get("dst_tx"), "LayerZero Scan destination.tx", step=14),
        _check("Ethereum bridge-in tx", s14["txid"], fb[0] if len(fb) == 1 else None,
               "eth_getLogs OFTReceived(guid) without LayerZero Scan", step=14),
        _check("Ethereum bridge-in block", s14["block"], u.get("eth_block"), "eth_getTransactionReceipt", step=14),
        _check("Ethereum bridge-in time", s14["timestamp_utc"], _utc(lzs.get("dst_timestamp")), "LayerZero Scan destination.tx", step=14),
        _check("Ethereum bridge-in time", s14["timestamp_utc"], _utc(et.get("timestamp")), "Blockscout token transfer", step=14),
        _check("Ethereum bridge-in from (USDT0 OFT)", s14["from"], to_checksum_address(et["from"]) if et.get("from") else None,
               "Blockscout token transfer", step=14),
        _check("Ethereum bridge-in amount", s14["amount"], et.get("value"), "Blockscout token transfer", step=14),
    ]
    r = next((x for x in rango_rows if x["case001"]), None)
    if r is None:
        out.append(_check("case-001 Rango tx found in Blockscout pool", True, None, "blockscout_eth", step=15))
        return out
    ev = r.get("rango_event") or {}
    rg = s15["rango"]
    fee = (r.get("fee_info") or [{}])[0]
    routed = (r.get("routed") or [{}])[-1]
    rc, _src = receipt_of(CASE_RANGO_TX)
    rc = rc or {}
    out += [
        _check("Rango tx block", s15["block"], int(rc["blockNumber"], 16) if rc.get("blockNumber") else None, "eth_getTransactionReceipt", step=15),
        _check("Rango tx time", s15["timestamp_utc"], r.get("timestamp_utc"), "Blockscout token transfer", step=15),
        _check("Rango tx amount into Rango", s15["amount"], (r.get("into_rango") or {}).get("value"), "Blockscout token transfer", step=15),
        _check("Rango Diamond", s15["to"], to_checksum_address(r["into_rango"]["to"]) if r.get("into_rango") else None,
               "Blockscout token transfer", step=15),
        _check("dAppName", rg["dAppName"], ev.get("dapp_name"), "RangoBridgeInitiated (own decoder, receipt log)", step=15),
        _check("dAppTag", rg["dAppTag"], ev.get("dapp_tag"), "RangoBridgeInitiated", step=15),
        _check("bridgeId", rg["bridgeId"], ev.get("bridge_id"), "RangoBridgeInitiated", step=15),
        _check("destinationChainId", rg["destinationChainId"], ev.get("destination_chain_id"), "RangoBridgeInitiated", step=15),
        _check("destinationChainId ASCII", rg["destinationChainId_ascii"], ev.get("destination_chain_ascii"), "RangoBridgeInitiated", step=15),
        _check("receiver ASCII", rg["receiver_bytes_ascii"], ev.get("receiver_ascii"), "RangoBridgeInitiated.receiver", step=15),
        _check("affiliate", rg["affiliate"], fee.get("affiliator"), "FeeInfo", step=15),
        _check("affiliateFee", rg["affiliateFee"], fee.get("affiliate_fee"), "FeeInfo", step=15),
        _check("forwarded_to", rg["forwarded_to"], routed.get("to"), "Routed (RangoRouter)", step=15),
        _check("forwarded_amount", rg["forwarded_amount"], routed.get("amount"), "Routed", step=15),
        _check("forwarded_amount = RangoBridgeInitiated.bridgeAmount", rg["forwarded_amount"], ev.get("bridge_amount"),
               "RangoBridgeInitiated", step=15),
    ]
    sweep = next((s for s in r.get("deposit_sweeps") or [] if s["tx"].lower() == s16["txid"].lower()), None)
    oc = r.get("oneclick") or {}
    nf = s16["near_intents"]
    out += [
        _check("deposit sweep tx", s16["txid"], sweep["tx"] if sweep else None, "Blockscout address token-transfers (deposit address)", step=16),
        _check("deposit sweep to (NEAR vault)", s16["to"], to_checksum_address(sweep["to"]) if sweep and sweep.get("to") else None,
               "Blockscout", step=16),
        _check("deposit sweep amount", s16["amount"], sweep["value"] if sweep else None, "Blockscout", step=16),
        _check("deposit sweep time", s16["timestamp_utc"], sweep["timestamp_utc"] if sweep else None, "Blockscout", step=16),
        _check("1Click status", nf["status"], oc.get("status"), "1Click /v0/status", step=16),
        _check("1Click recipient", nf["recipient_tron"], oc.get("recipient"), "1Click quoteRequest.recipient", step=16),
        _check("1Click refundTo", nf["refundTo"], oc.get("refund_to"), "1Click quoteRequest.refundTo", step=16),
        _check("1Click intentHash", nf["intentHash"], (oc.get("intent_hashes") or [None])[0], "1Click swapDetails.intentHashes", step=16),
        _check("1Click NEAR txs", ",".join(nf["near_tx"]), ",".join(oc.get("near_tx_hashes") or []) or None,
               "1Click swapDetails.nearTxHashes", step=16),
        _check("1Click destination tx", nf["destination_tx"], (oc.get("destination_chain_tx_hashes") or [None])[0], "1Click", step=16),
        _check("1Click originChainTxHashes vs fixture step 16 tx (different meaning: deposit tx vs sweep)", s16["txid"],
               (oc.get("origin_chain_tx_hashes") or [None])[0], "1Click originChainTxHashes", step=16, kind="observation"),
    ]
    p = (r.get("tron_payouts") or [{}])[0]
    out += [
        _check("TRON payout block", s17["block"], p.get("block"), "TronGrid /v1/transactions/{id}/events", step=17),
        _check("TRON payout time", s17["timestamp_utc"], p.get("timestamp_utc"), "TronGrid events", step=17),
        _check("TRON payout from (NEAR Intents payout wallet)", s17["from"], p.get("from"), "TronGrid events", step=17),
        _check("TRON payout to", s17["to"], p.get("to"), "TronGrid events", step=17),
        _check("TRON payout amount (on-chain)", s17["amount"], p.get("value"), "TronGrid events (USDT Transfer value)", step=17),
        _check("TRON payout amount vs 1Click amountOut (fixture note: differs)", s17["amount"], oc.get("amount_out_formatted"),
               "1Click swapDetails.amountOut", step=17, kind="observation"),
    ]
    return out


_KEY_LABELS = {"etherscan": "Etherscan", "blockscout_pro": "Blockscout PRO", "eth_rpc_paid": "платный ETH RPC",
               "near_intents_partner_key": "ключ партнёра 1Click", "rango": "Rango", "trongrid": "TronGrid"}


def _markdown(s: dict[str, Any]) -> str:
    # Wording avoids "name=value" / "Header: value" shapes for key names: the redactor masks those.
    used = "; ".join(f"{_KEY_LABELS.get(k, k)} — {'да' if v else 'нет'}" for k, v in s["keys_used"].items())
    L = ["# Мосты и источники Ethereum — итог замера", "",
         f"Дата (UTC): {s['date_utc']}. Режим HTTP: {s['http_mode']}. Использованы ключи: {used}.", "",
         "## Источники: доступность и задержка", "",
         "| Источник | Вызовов | Успешно | Доля | HTTP-запросов | 429 | Повторы | p50, мс | p95, мс | max, мс |",
         "|---|---|---|---|---|---|---|---|---|---|"]
    for r in s["per_source"]:
        L.append(f"| {r['provider']} | {r['calls']} | {r['calls_ok']} | {r['success_share']} | {r['http_requests']} | "
                 f"{r['http_429_seen']} | {r['retries']} | {r['latency_ms_p50']} | {r['latency_ms_p95']} | {r['latency_ms_max']} |")
    L += ["", "## Публичные Ethereum RPC (кандидаты)", "",
          "| Провайдер | Пригоден | Квитанция 3-недельной давности | eth_getLogs 50 блоков | Пустой ответ вместо события | Ошибка |",
          "|---|---|---|---|---|---|"]
    for c in s["rpc_candidates"]:
        L.append(f"| {c['provider']} | {c['usable']} | {c['receipt']} | {c['getlogs_50']} | {c['getlogs_false_negative']} | "
                 f"{(c['error'] or '')[:90]} |")
    u, r, e = s["usdt0"], s["rango"], s["eth_agreement"]
    L += ["", "## Мосты", "",
          f"- USDT0/LayerZero (TRON → Ethereum): потоков {u['flows']}; выход распознан по сырым логам TRON: {u['exit_recognised_on_tron']}; "
          f"получатель совпал (LZ Scan и OFTReceived): {u['recipient_agrees']}; tx назначения найдена без LZ Scan и совпала: "
          f"{u['dst_tx_agrees_onchain_vs_lz']}; суммы совпали: {u['amount_agrees']}; комиссия, б.п.: {u['fees_bps']}; "
          f"доставка, с: {u['delivery_s']}; запасной путь нашёл событие: {u['fallback_sources_found']}.",
          f"- Rango: потоков {r['flows']}; маршруты: {r['routes']}; событие RangoBridgeInitiated: {r['bridge_initiated_event']}; "
          f"bridgeId и маршрут: {r['bridge_ids_by_route']}; получатели: {r['recipients']}; получатель начинается с префикса из события: "
          f"{r['recipient_matches_prefix']}; выплата совпала с получателем: {r['payout_matches_recipient']}; "
          f"выплата минус amountOut 1Click: {r['payout_minus_1click_amount_out']}; кошельки выплат: {r['payout_wallets']}; "
          f"поиск без 1Click: попыток {r['fallback_attempted']}, один кандидат {r['fallback_unique_match']}, совпал с 1Click "
          f"{r['fallback_agrees_with_1click']}; депозит переведён в хранилище NEAR Intents: {r['swept_to_near_vault']}; "
          f"посторонних (не USDT) переводов с депозитных адресов: {r['deposit_poisoning_transfers']}; "
          f"наш декодер совпал с декодером Blockscout: {r['ours_vs_blockscout_decoder_equal']} из {r['events_compared_with_blockscout']}.",
          f"- Согласие источников Ethereum: {e['all_agree']} из {e['txs']} транзакций совпали полностью; "
          f"пустые квитанции: { {k: len(v) for k, v in e['null_receipts'].items()} }; "
          f"пропуски в token-transfers Blockscout: {e['blockscout_transfer_gaps']}.", "",
          "## Сверка с эталоном case-001", "",
          f"Фактов: {s['case001_checks']['total']}, совпало: {s['case001_checks']['match']}, расходится: "
          f"{s['case001_checks']['mismatch']}, не проверено: {s['case001_checks']['unverified']}.", ""]
    if s["discrepancies"]:
        L += ["Расхождения (данные не подгонялись):", ""]
        for d in s["discrepancies"]:
            L.append(f"- шаг {d['step']}, {d['fact']}: эталон `{d['fixture']}`, наблюдение `{d['observed']}` ({d['source']})")
        L.append("")
    if s.get("observations"):
        L += ["Наблюдения (не расхождения с эталоном, а разный смысл полей):", ""]
        for d in s["observations"]:
            L.append(f"- шаг {d['step']}, {d['fact']}: эталон `{d['fixture']}`, наблюдение `{d['observed']}` ({d['source']})")
        L.append("")
    if s["not_measured"]:
        L += ["## Не измерено", ""] + [f"- {n['what']} — {n['why']}; нужно: {n['needed']}" for n in s["not_measured"]] + [""]
    L.append(f"Всего HTTP-запросов в прогоне: {s['requests_total']}.")
    return "\n".join(L) + "\n"
