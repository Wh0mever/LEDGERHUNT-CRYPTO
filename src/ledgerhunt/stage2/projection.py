"""Stage 2 area 'projection' (decisions 4.3): a 1,000-address graph projected from measurements.

No network. Inputs come from the newest tron_sources run (results/stage-2/tron-sources/latest.json),
the case-001 reference run (results/stage-2/case-001/<run>/timings.json and step3-reference-run.json)
and documented plan limits/prices (docs/stage-2/accounts-and-keys.md, Stage 1 proposal section 1).
Every input carries its origin: measured / documented / assumed.

Model (TRON part of the graph; bridge crossings are listed separately):
    E       = N * k                                  report edges (TXIDs to verify)
    R_tg    = N * p + N * f_ctx * c + E * r_ev       TronGrid requests (history pages, context, v1 events)
    R_node  = E + N * a                              independent node requests (receipt per edge, account check)
    T_src   = R_src / rps_src                        time at a sustained request rate
    graphs/day (TronGrid BASIC) = floor(Q_day / R_tg)
    cost/graph (Chainstack Growth, archive) = R_node * RU_archive * price_month / RU_month

Run:    python -m ledgerhunt stage2 projection
Replay: python -m ledgerhunt stage2 projection --replay   (identical: the area makes no HTTP requests)
"""

from __future__ import annotations

import argparse
import json
import math
from decimal import ROUND_HALF_UP, Decimal
from pathlib import Path
from typing import Any

from ..core.paths import rel_to_root, repo_root, results_root
from ..core.results import start_run

AREA = "projection"
TRON_SOURCES_AREA = "tron-sources"
CASE001_MAIN_RUN = "results/stage-2/case-001/20261014T113519Z"  # main live run named in case-001-reference-run.md
N_MAIN = 1000
N_STANDARD = 40  # «стандартное расследование» of the Stage 1 proposal (40-45 addresses)
FOLLOW_WINDOW_H = 6  # baseline THRESHOLDS["follow_window_s"]
PAGE_ROWS = 200

STAGE1 = {
    "trongrid_requests": "≈3 300 (индекс события из квитанции) … 6–7 тыс. (запрос событий на каждое ребро)",
    "node_receipts": "3 000–4 000 TXID (по одной квитанции на TXID)",
    "total_requests": "6–10 тыс.",
    "graphs_per_day": "14–30",
    "rps_5_min": "11–24 зап/с",
    "rps_240_s": "14–29 зап/с",
    "data_share_s": 240,
    "energy_context": "около 2 000 из 3 300 — контекст энергии",
    "source": "docs/stage-1-stack-proposal.md, раздел 1 «Инфраструктура и затраты» и A6",
}

DOC = {
    "trongrid_basic_quota_day": (100_000, "documented", "TronGrid BASIC: 100 000 запросов в сутки (accounts-and-keys.md [S5])"),
    "trongrid_key_rps_published": (None, "documented", "TronGrid не публикует частоту с ключом (страница rate-limits, accounts-and-keys.md [S6])"),
    "trongrid_key_rps_old_docs": (15, "documented", "в старых версиях документации TronGrid встречалось 15 зап/с (accounts-and-keys.md 1.2)"),
    "trongrid_keyless_rps_docs": (3, "documented", "журнал изменений TronGrid: без ключа 3 зап/с (accounts-and-keys.md [S5])"),
    "chainstack_dev_ru_month": (3_000_000, "documented", "Chainstack Developer: $0, 3 млн RU/мес, 25 зап/с, архива нет ([S7])"),
    "chainstack_dev_rps": (25, "documented", "Chainstack Developer: 25 зап/с ([S7])"),
    "chainstack_growth_price_usd": (Decimal("49"), "documented", "Chainstack Growth: $49/мес ([S7])"),
    "chainstack_growth_ru_month": (20_000_000, "documented", "Chainstack Growth: 20 млн RU/мес ([S7])"),
    "chainstack_growth_rps": (250, "documented", "Chainstack Growth: 250 зап/с ([S7])"),
    "chainstack_overage_usd_per_m_ru": (Decimal("15"), "documented", "сверх лимита $15 за 1 млн RU ([S7])"),
    "chainstack_ru_full": (1, "documented", "запрос к полному узлу — 1 RU ([S7])"),
    "chainstack_ru_archive": (2, "documented", "запрос к архивному узлу — 2 RU ([S7])"),
    "getblock_starter_price_usd": (Decimal("49"), "documented", "GetBlock Starter $49/мес, 90 млн CU; вес методов TRON в CU не опубликован ([S9])"),
    "nodit_basic_price_usd": (Decimal("10"), "documented", "Nodit Basic $10/мес, 100 млн CU; Node API для TRON не подтверждён ([S11])"),
    "getblock_tron_dedicated_usd": (Decimal("150"), "documented", "GetBlock Limitless Node TRON: полный узел от $150/мес за 25 зап/с ([S9])"),
}

OWN_NODE = {
    "min": {"cpu_cores": 8, "ram_gb": 16, "ssd_tb": "3", "bandwidth_mbps": 100},
    "recommended": {"cpu_cores": 16, "ram_gb": 32, "ssd_tb": "3.5+", "bandwidth_mbps": 100},
    "snapshot_size": "более 2 ТБ («The TRON network snapshot data size exceeds 2TB»)",
    "lite_fullnode": "состояние сети + последние 65 536 блоков (≈2.3 сут); история до снимка недоступна",
    "sync_time": "официальная документация длительность синхронизации с нуля не называет («significant amount of time»); рекомендует снимки данных",
    "sources": [
        "https://tronprotocol.github.io/documentation-en/using_javatron/installing_javatron/ (страница от 2026-09-25)",
        "https://tronprotocol.github.io/documentation-en/using_javatron/backup_restore/ (страница от 2026-09-29)",
        "https://tronprotocol.github.io/documentation-en/using_javatron/litefullnode/ (страница от 2026-07-30)",
    ],
    "server_price": "не проверено: цены выделенных серверов с ≥3.5 ТБ NVMe на страницах Hetzner рисуются скриптом и в тексте страниц отсутствуют (проверено 2026-10-14)",
}


def _inp(value: Any, origin: str, source: str, unit: str = "") -> dict[str, Any]:
    return {"value": value, "origin": origin, "source": source, "unit": unit}


def _d(x: Any) -> Decimal:
    return Decimal(str(x))


def _money(x: Decimal) -> str:
    return str(x.quantize(Decimal("0.0001"), rounding=ROUND_HALF_UP))


def _read_json(p: Path) -> Any:
    return json.loads(p.read_text(encoding="utf-8"))


def _tron_sources_pointer() -> dict[str, Any]:
    """latest.json of tron_sources; refuses a run that did not finish with status 'ok'."""
    latest = results_root() / TRON_SOURCES_AREA / "latest.json"
    if not latest.is_file():
        raise FileNotFoundError("results/stage-2/tron-sources/latest.json: run 'stage2 tron_sources' first")
    pointer = _read_json(latest)
    if pointer.get("status") != "ok":
        # e.g. a replay miss or a partial live run: its numbers must not feed the projection
        raise RuntimeError(f"tron_sources run {pointer.get('path')} finished with status {pointer.get('status')!r}; "
                           "the projection needs a successful tron_sources run (fix it and re-run tron_sources)")
    return pointer


class Projection:
    def __init__(self, args: argparse.Namespace) -> None:
        self.mode = (getattr(args, "http_mode", None) or "record").lower()
        self.ctx = start_run(AREA, config={"n_main": N_MAIN, "n_standard": N_STANDARD,
                                           "follow_window_h": FOLLOW_WINDOW_H, "case001_run": CASE001_MAIN_RUN},
                             reproduce="python -m ledgerhunt stage2 projection" +
                                       (" --replay" if self.mode == "replay" else ""))

    # ------------------------------------------------------------ inputs
    def load_sources(self) -> tuple[dict[str, Any], str]:
        run_dir = repo_root() / _tron_sources_pointer()["path"]
        summary = _read_json(run_dir / "summary.json")
        label = rel_to_root(run_dir)
        if summary.get("live_source_run"):
            label += f" (офлайн-повтор живого прогона {summary['live_source_run']})"
        return summary, label

    def load_case001(self) -> tuple[dict[str, Any], dict[str, Any], str]:
        run = repo_root() / CASE001_MAIN_RUN
        timings = _read_json(run / "timings.json")
        ref = _read_json(run / "step3-reference-run.json")
        return timings, ref, rel_to_root(run)

    def build_inputs(self) -> dict[str, Any]:
        ts, ts_run = self.load_sources()
        timings, ref, case_run = self.load_case001()
        pi = ts.get("projection_inputs") or {}
        load = pi.get("load") or {}
        src_ts = f"{ts_run.split(' ')[0]}/summary.json"
        inp: dict[str, Any] = {"_runs": {"tron_sources": ts_run, "case001": case_run}}

        # --- measured rates (tron_sources L phase)
        for name in ("trongrid_keyless", "trongrid_key", "publicnode", "paid_rpc"):
            v = load.get(name)
            if not v:
                inp[f"rps_{name}"] = _inp(None, "not_measured",
                                          "не измерено: нет ключа" if name.startswith("paid") else "нет данных", "зап/с")
                continue
            su = v.get("sustained") or {}
            inp[f"rps_{name}"] = _inp(su.get("achieved_ok_rps"), "measured",
                                      f"{src_ts}: load.{name}.sustained (план {su.get('rate_rps')} зап/с, "
                                      f"429: {su.get('http_429')}, ошибок {su.get('error_share')})", "зап/с")
            inp[f"first_429_{name}"] = _inp(v.get("first_429_step_rps"), "measured",
                                            f"{src_ts}: первая ступень ramp с HTTP 429", "зап/с")
            inp[f"declared_limit_{name}"] = _inp(v.get("declared_limit_rps"), "measured",
                                                 f"{src_ts}: лимит, названный сервером в теле ответа 429", "зап/с")
            inp[f"declared_suspension_{name}"] = _inp(v.get("declared_suspension_s"), "measured",
                                                      f"{src_ts}: пауза, названная сервером в теле 429", "с")
            inp[f"latency_{name}"] = _inp({"p50": su.get("latency_ms_p50"), "p95": su.get("latency_ms_p95"),
                                           "by_kind": su.get("latency_by_kind")}, "measured", src_ts, "мс")

        # --- history pages per address (C phase windows, scaled to the baseline's 6 h follow window)
        aw = [r for r in pi.get("address_windows") or [] if r["kind"] == "case"]
        per_addr: dict[str, dict[str, Any]] = {}
        for r in aw:
            hours = r["blocks"] * 3 / 3600
            rate = r["v1_transfers"] / hours if hours else 0
            pages6 = max(1, math.ceil(rate * FOLLOW_WINDOW_H / PAGE_ROWS))
            cur = per_addr.get(r["address"])
            if cur is None or rate > cur["transfers_per_hour"]:
                per_addr[r["address"]] = {"address": r["address"], "window": r["window"],
                                          "transfers_per_hour": round(rate, 2), "pages_6h": pages6,
                                          "out": r["v1_out"], "distinct_out": r["v1_distinct_counterparties_out"]}
        rows = sorted(per_addr.values(), key=lambda x: x["transfers_per_hour"])
        inp["address_history_profile"] = _inp(rows, "measured",
                                              f"{src_ts}: completeness.by_address_window (окна case-001), "
                                              f"пересчёт на окно {FOLLOW_WINDOW_H} ч и страницу {PAGE_ROWS} строк")
        ordinary = [r for r in rows if r["pages_6h"] == 1]
        hv = [r for r in rows if r["pages_6h"] > 1]
        inp["share_high_volume_case"] = _inp(round(len(hv) / len(rows), 3) if rows else None, "measured",
                                             f"доля адресов case-001, которым за {FOLLOW_WINDOW_H} ч нужно >1 страницы "
                                             f"({len(hv)} из {len(rows)}: {', '.join(r['address'][:6] for r in hv)})")
        inp["pages_hv_uncapped"] = _inp([r["pages_6h"] for r in hv], "measured", "страниц за 6 ч у этих адресов без лимита")
        outs = sorted(r["out"] for r in ordinary)
        dist = [(r["out"], r["distinct_out"]) for r in ordinary if r["distinct_out"]]
        inp["out_transfers_ordinary_median"] = _inp(outs[len(outs) // 2] if outs else None, "measured",
                                                    "медиана исходящих USDT-переводов обычного адреса case-001 в окне")
        inp["transfers_per_new_counterparty"] = _inp(
            round(sum(a for a, _ in dist) / sum(b for _, b in dist), 3) if dist else None, "measured",
            "исходящие переводы / различные получатели у обычных адресов case-001")
        hot = (pi.get("pagination") or {}).get("hot_wallet_desc") or {}
        inp["hot_wallet_rows_per_hour"] = _inp(hot.get("rows_per_hour"), "measured",
                                               f"{src_ts}: pagination.hot_wallet_desc (TWBPGL, {hot.get('pages')} стр.)")

        # --- case-001 reference run
        st3 = timings.get("step3_reference") or {}
        by = st3.get("by_provider") or {}
        edges = (ref.get("result") or {}).get("edges") or []
        inp["case001_requests_total"] = _inp(st3.get("total_requests"), "measured", f"{case_run}/timings.json step3_reference")
        inp["case001_requests_trongrid"] = _inp((by.get("trongrid") or {}).get("requests"), "measured",
                                                f"{case_run}/timings.json step3_reference.by_provider")
        inp["case001_addresses"] = _inp(12, "measured",
                                        "docs/stage-2/case-001-reference-run.md, раздел 7: 7 на маршруте, 4 получателя выходов хаба, 1 источник TRX")
        inp["case001_edges"] = _inp(len(edges), "measured", f"{case_run}/step3-reference-run.json result.edges "
                                    f"({sum(1 for e in edges if e.get('chain') == 'tron')} TRON, "
                                    f"{sum(1 for e in edges if e.get('chain') != 'tron')} Ethereum)")
        inp["case001_wall_s"] = _inp(st3.get("wall_s"), "measured", f"{case_run}/timings.json step3_reference.wall_s")
        steps = {s["step"]: s for s in st3.get("steps") or []}
        bridge = [s for k, s in steps.items() if k.startswith(("3.3", "3.4", "3.5"))]
        inp["bridge_crossing_requests"] = _inp([{"step": s["step"], "requests": s["requests"],
                                                  "by_provider": {k: v["requests"] for k, v in s["by_provider"].items()}}
                                                 for s in bridge], "measured", f"{case_run}/timings.json")

        # --- event index / completeness facts that remove or keep terms of the model
        ei = ts.get("event_index") or {}
        comp = (ts.get("completeness") or {}).get("by_source") or {}
        inp["event_index_equals_receipt_ordinal"] = _inp(
            {k: {"checked": v.get("transfer_events"), "equal": v.get("equal"), "differ": v.get("differ")}
             for k, v in ei.items() if isinstance(v, dict) and "equal" in v}, "measured", f"{src_ts}: event_index")
        inp["v1_vs_node_logs"] = _inp({k: {"node": v["node_transfers"], "v1": v["v1_transfers_same_windows"],
                                          "matched": v["matched"], "only_v1": v["only_v1"], "only_node": v["only_node"]}
                                      for k, v in comp.items()}, "measured", f"{src_ts}: completeness.by_source")
        inp["publicnode_receipt_depth"] = _inp({"oldest_block_utc": (ts.get("publicnode_depth") or {}).get("oldest_served_utc"),
                                                "receipt_oldest_utc": (ts.get("publicnode_depth") or {}).get("receipt_oldest_served_utc"),
                                                "depth_days_blocks": (ts.get("publicnode_depth") or {}).get("depth_days")},
                                               "measured", f"{src_ts}: publicnode_depth")
        for k, (v, origin, source) in DOC.items():
            inp[k] = _inp(v, origin, source)
        return inp

    # ------------------------------------------------------------ model
    @staticmethod
    def p_bar(profile: list[dict[str, Any]], share_hv: float, cap: int) -> float:
        """Mean history pages per address: ordinary 1 page, high-volume = mean(min(pages, cap))."""
        hv = [min(r["pages_6h"], cap) for r in profile if r["pages_6h"] > 1]
        hv_mean = sum(hv) / len(hv) if hv else 1.0
        return (1 - share_hv) * 1.0 + share_hv * hv_mean

    def scenarios(self, inp: dict[str, Any]) -> list[dict[str, Any]]:
        prof = inp["address_history_profile"]["value"]
        share_case = inp["share_high_volume_case"]["value"] or 0.0
        k_meas = inp["transfers_per_new_counterparty"]["value"] or 1.0
        k_case = round(inp["case001_edges"]["value"] / inp["case001_addresses"]["value"], 3)
        return [
            {"id": "low", "title": "нижняя оценка",
             "params": {
                 "share_hv": _inp(0.05, "assumed", "5% адресов с большой историей (допущение)"),
                 "page_cap": _inp(5, "documented", "лимит страниц базового алгоритма THRESHOLDS['max_pages']=5"),
                 "k": _inp(k_case, "measured", "рёбер на разобранный адрес в эталонном прогоне case-001 (13/12)"),
                 "f_ctx": _inp(0.0, "assumed", "контекст энергии не запрашивается"),
                 "c": _inp(2, "assumed", "2 запроса контекста на адрес (Этап 1)"),
                 "r_ev": _inp(0, "measured", "event_index = порядковый номер лога квитанции: события v1 на ребро не нужны"),
                 "a": _inp(0, "assumed", "проверка счёта/контракта на узле не нужна (реестр, кэш)")}},
            {"id": "base", "title": "базовая оценка",
             "params": {
                 "share_hv": _inp(share_case, "measured", "доля адресов case-001 с историей >1 страницы за 6 ч"),
                 "page_cap": _inp(5, "documented", "лимит страниц базового алгоритма THRESHOLDS['max_pages']=5"),
                 "k": _inp(max(k_meas, k_case), "measured",
                           "переводов на нового получателя у обычных адресов case-001 (не меньше 13/12 эталонного прогона)"),
                 "f_ctx": _inp(0.3, "assumed", "контекст энергии и источника TRX — только для адресов на пути отчёта (30%)"),
                 "c": _inp(2, "assumed", "2 запроса контекста на адрес (Этап 1)"),
                 "r_ev": _inp(0, "measured", "event_index = порядковый номер лога квитанции"),
                 "a": _inp(1, "assumed", "одна проверка счёта/контракта на независимом узле на адрес")}},
            {"id": "high", "title": "верхняя оценка (допущения Этапа 1)",
             "params": {
                 "share_hv": _inp(share_case, "measured", "доля адресов case-001 с историей >1 страницы за 6 ч"),
                 "page_cap": _inp(10, "assumed", "лимит страниц поднят до 10"),
                 "k": _inp(4, "assumed", "4 TXID на адрес (верх диапазона Этапа 1: 3 000–4 000 TXID на 1 000 адресов)"),
                 "f_ctx": _inp(1.0, "assumed", "контекст для всех адресов (Этап 1: ≈2 000 из 3 300)"),
                 "c": _inp(2, "assumed", "2 запроса контекста на адрес (Этап 1)"),
                 "r_ev": _inp(1, "assumed", "запрос событий v1 на каждое ребро (вариант Этапа 1; по замеру не нужен)"),
                 "a": _inp(1, "assumed", "одна проверка счёта/контракта на узле на адрес")}},
        ]

    def compute(self, inp: dict[str, Any], sc: dict[str, Any], n: int) -> dict[str, Any]:
        p = {k: v["value"] for k, v in sc["params"].items()}
        prof = inp["address_history_profile"]["value"]
        pbar = self.p_bar(prof, p["share_hv"], p["page_cap"])
        e = n * p["k"]
        r_hist = n * pbar
        r_ctx = n * p["f_ctx"] * p["c"]
        r_ev = e * p["r_ev"]
        r_tg = r_hist + r_ctx + r_ev
        r_node = e + n * p["a"]
        out: dict[str, Any] = {
            "n": n, "p_bar": round(pbar, 3), "edges": round(e), "trongrid": {
                "history": round(r_hist), "context": round(r_ctx), "v1_events": round(r_ev), "total": round(r_tg)},
            "node": {"receipts": round(e), "account_checks": round(n * p["a"]), "total": round(r_node)},
            "total_requests": round(r_tg + r_node),
        }
        # time at rates
        rates = {
            "trongrid_keyless_measured": inp["rps_trongrid_keyless"]["value"],
            "trongrid_keyless_declared": (inp.get("declared_limit_trongrid_keyless") or {}).get("value"),
            "trongrid_key_measured": inp["rps_trongrid_key"]["value"],
            "trongrid_key_declared": (inp.get("declared_limit_trongrid_key") or {}).get("value"),
        }
        out["time_trongrid_s"] = {k: (round(r_tg / v, 1) if v else None) for k, v in rates.items()}
        node_rates = {
            "publicnode_measured": inp["rps_publicnode"]["value"],
            "chainstack_developer_25": DOC["chainstack_dev_rps"][0],
            "chainstack_growth_250": DOC["chainstack_growth_rps"][0],
            "paid_rpc_measured": inp["rps_paid_rpc"]["value"],
        }
        out["time_node_s"] = {k: (round(r_node / v, 1) if v else None) for k, v in node_rates.items()}
        out["needed_trongrid_rps"] = {"in_240_s": round(r_tg / 240, 1), "in_300_s": round(r_tg / 300, 1)}
        out["needed_node_rps"] = {"in_240_s": round(r_node / 240, 1)}
        lat = (inp.get("latency_trongrid_key") or {}).get("value") or {}
        if lat.get("p50") and inp["rps_trongrid_key"]["value"]:
            out["concurrency_for_measured_key_rps"] = round(inp["rps_trongrid_key"]["value"] * lat["p50"] / 1000, 1)
        q = DOC["trongrid_basic_quota_day"][0]
        out["trongrid_quota"] = {"share_of_daily_quota": round(r_tg / q, 4), "fits": r_tg <= q,
                                 "graphs_per_day": math.floor(q / r_tg) if r_tg else None}
        # costs
        ru_arch = DOC["chainstack_ru_archive"][0]
        ru_full = DOC["chainstack_ru_full"][0]
        growth_price, growth_ru = DOC["chainstack_growth_price_usd"][0], DOC["chainstack_growth_ru_month"][0]
        over = DOC["chainstack_overage_usd_per_m_ru"][0]
        ru_graph_arch = _d(r_node) * ru_arch
        out["cost"] = {
            "trongrid_basic": {"usd": "0", "note": "в пределах 100 000 запросов в сутки" if r_tg <= q else
                               "не помещается в суточную квоту: платного тарифа с ценой нет (Custom по заявке)"},
            "publicnode": {"usd": "0", "note": "только разработка; квитанции не старше ≈8.5 сут; условия не подтверждены"},
            "chainstack_developer": {"usd": "0", "ru_per_graph": int(_d(r_node) * ru_full),
                                     "graphs_per_month_in_plan": math.floor(DOC["chainstack_dev_ru_month"][0] / (r_node * ru_full)),
                                     "note": "архива нет (документировано): квитанции старых транзакций, вероятно, недоступны; не измерено — нет ключа"},
            "chainstack_growth_archive": {
                "ru_per_graph": int(ru_graph_arch),
                "usd_amortized": _money(ru_graph_arch * growth_price / growth_ru),
                "usd_overage_rate": _money(ru_graph_arch * over / Decimal(1_000_000)),
                "graphs_per_month_in_plan": math.floor(growth_ru / (r_node * ru_arch)),
                "note": "$49/мес; 2 RU за архивный запрос; сверх 20 млн RU — $15 за 1 млн RU"},
            "getblock_starter": {"usd": None, "note": "не рассчитано: вес методов TRON в CU не опубликован"},
            "nodit_basic": {"usd": None, "note": "не рассчитано: Node API для TRON не подтверждён"},
            "own_node": {"usd": None, "note": OWN_NODE["server_price"]},
        }
        return out

    # ------------------------------------------------------------ run
    def run(self) -> int:
        inp = self.build_inputs()
        scs = self.scenarios(inp)
        results = []
        for sc in scs:
            results.append({"id": sc["id"], "title": sc["title"], "params": sc["params"],
                            "n1000": self.compute(inp, sc, N_MAIN), "n40": self.compute(inp, sc, N_STANDARD)})
        self.ctx.write_json("inputs.json", inp)
        self.ctx.write_json("scenarios.json", results)
        self.ctx.write_json("own-node.json", OWN_NODE)
        summary = {"run_id": self.ctx.run_id, "inputs_from": inp["_runs"],
                   "scenarios": {r["id"]: {"trongrid": r["n1000"]["trongrid"]["total"], "node": r["n1000"]["node"]["total"],
                                           "graphs_per_day": r["n1000"]["trongrid_quota"]["graphs_per_day"],
                                           "time_trongrid_s": r["n1000"]["time_trongrid_s"],
                                           "time_node_s": r["n1000"]["time_node_s"],
                                           "needed_trongrid_rps": r["n1000"]["needed_trongrid_rps"],
                                           "cost": r["n1000"]["cost"]} for r in results},
                   "stage1": STAGE1}
        self.ctx.finish(summary, self.markdown(inp, results))
        print(f"[{AREA}] results: {self.ctx.rel_dir}", flush=True)
        return 0

    def markdown(self, inp: dict[str, Any], results: list[dict[str, Any]]) -> str:
        def v(name: str) -> Any:
            return (inp.get(name) or {}).get("value")

        L = [f"# Расчёт графа на {N_MAIN} адресов — прогон {self.ctx.run_id}", "",
             f"Входные данные: `{inp['_runs']['tron_sources']}` (замер источников TRON), `{inp['_runs']['case001']}` "
             "(эталонный прогон case-001), тарифы — docs/stage-2/accounts-and-keys.md.", "",
             "## Измеренные скорости", "",
             "| Источник | Устойчиво, успешных зап/с | Первый 429 на ступени, зап/с |", "|---|---|---|"]
        for name in ("trongrid_keyless", "trongrid_key", "publicnode", "paid_rpc"):
            L.append(f"| {name} | {v('rps_' + name)} | {v('first_429_' + name)} |")
        L += ["", "## Сценарии (N = 1 000)", "",
              "| | " + " | ".join(r["title"] for r in results) + " |", "|---|" + "---|" * len(results)]

        def row(label: str, fn) -> None:
            L.append(f"| {label} | " + " | ".join(str(fn(r["n1000"])) for r in results) + " |")

        row("p̄, страниц истории на адрес", lambda x: x["p_bar"])
        row("рёбер (квитанций)", lambda x: x["edges"])
        row("TronGrid: история", lambda x: x["trongrid"]["history"])
        row("TronGrid: контекст", lambda x: x["trongrid"]["context"])
        row("TronGrid: события v1", lambda x: x["trongrid"]["v1_events"])
        row("**TronGrid всего**", lambda x: x["trongrid"]["total"])
        row("**Узел всего**", lambda x: x["node"]["total"])
        row("Графов в сутки на квоте 100 000", lambda x: x["trongrid_quota"]["graphs_per_day"])
        row("TronGrid без ключа, с", lambda x: x["time_trongrid_s"]["trongrid_keyless_measured"])
        row("TronGrid без ключа при заявленных 3 зап/с, с", lambda x: x["time_trongrid_s"]["trongrid_keyless_declared"])
        row("TronGrid с ключом (замер), с", lambda x: x["time_trongrid_s"]["trongrid_key_measured"])
        row("TronGrid с ключом при заявленных 15 зап/с, с", lambda x: x["time_trongrid_s"]["trongrid_key_declared"])
        row("Нужно зап/с к TronGrid за 240 с", lambda x: x["needed_trongrid_rps"]["in_240_s"])
        row("Узел: PublicNode (замер), с", lambda x: x["time_node_s"]["publicnode_measured"])
        row("Узел: Chainstack Growth 250 зап/с, с", lambda x: x["time_node_s"]["chainstack_growth_250"])
        row("Chainstack Growth, $ за граф (из абонплаты)", lambda x: x["cost"]["chainstack_growth_archive"]["usd_amortized"])
        row("Chainstack Growth, $ за граф (сверх лимита)", lambda x: x["cost"]["chainstack_growth_archive"]["usd_overage_rate"])
        L += ["", f"Этап 1 для сравнения: TronGrid {STAGE1['trongrid_requests']}; {STAGE1['graphs_per_day']} графов в сутки; "
              f"{STAGE1['rps_5_min']} за 5 минут; {STAGE1['rps_240_s']} за 240 с.", ""]
        return "\n".join(L)


def run(args: argparse.Namespace) -> int:
    _tron_sources_pointer()  # fail before a run folder is created
    return Projection(args).run()
