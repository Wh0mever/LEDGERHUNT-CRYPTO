"""Russian Markdown for case-001: MANIFEST.md of the raw fixture and the run report.

Only presentation lives here; every number comes from the step outputs.
"""

from __future__ import annotations

import json
from collections import Counter, defaultdict
from pathlib import Path
from typing import Any
from urllib.parse import urlsplit

VERDICT_RU = {"confirmed": "подтверждено", "mismatch": "РАСХОЖДЕНИЕ", "not_verifiable": "не проверяемо",
              "match": "совпадает", "partial": "частично", }


def _cell(v: Any, limit: int = 160) -> str:
    if isinstance(v, (dict, list)):
        v = json.dumps(v, ensure_ascii=False, default=str)
    s = "" if v is None else str(v)
    s = s.replace("|", "\\|").replace("\n", " ")
    return s if len(s) <= limit else s[: limit - 1] + "…"


def _request_label(row: dict[str, Any]) -> str:
    path = urlsplit(row.get("url") or "").path
    parts = [p for p in path.split("/") if p]
    tail = "/".join(parts[-2:]) if parts else ""
    if row.get("json_body"):
        body = row["json_body"]
        if isinstance(body, dict) and "method" in body:
            vals = body.get("params") or []
            return f"{body['method']} {json.dumps(vals, ensure_ascii=False)[:90]}"
        vals = [str(v) for k, v in sorted(body.items()) if k not in ("visible",)]
        return f"{tail} " + " ".join(vals)[:110]
    params = " ".join(f"{k}={v}" for k, v in row.get("params") or [] if k not in ("contract_address",))
    return f"{tail} {params}".strip()[:150]


def read_index(store: Path) -> list[dict[str, Any]]:
    p = store / "index.jsonl"
    if not p.is_file():
        return []
    return [json.loads(line) for line in p.read_text(encoding="utf-8").splitlines() if line.strip()]


def manifest_md(stores: list[tuple[str, Path]], *, generated_utc: str, run_id: str, keys_present: dict[str, bool],
                tronscan_store_rel: str) -> str:
    lines = [
        "# case-001: сырые ответы источников (MANIFEST)",
        "",
        f"Сформирован: {generated_utc} (запуск `{run_id}`). Файл создаётся командой "
        "`python -m ledgerhunt stage2 case001` при живом прогоне; при офлайн-повторе (`--replay`) не меняется.",
        "",
        "## Что здесь лежит",
        "",
        "- `http-store/objects/<2 символа>/<sha256>` — тело ответа байт в байт, имя файла = sha256 тела;",
        "- `http-store/index.jsonl` — строка на каждый ответ: источник, метод, URL без секретов, параметры, JSON-тело "
        "запроса, статус, часть заголовков, задержка, sha256 тела, метка запуска;",
        f"- `{tronscan_store_rel}/` — единственный запрос к TronScan (метка адреса для проверки при разработке). "
        "Статус: TronScan, ожидается письменное согласие на коммерческое использование API; метка не заносится "
        "ни в какое хранилище меток. Папку можно удалить целиком, если согласие не будет получено;",
        "- `expected/reference-run.json` — ожидаемый результат эталонного прогона (смысловая часть), с ним сверяется "
        "тест `tests/test_case001_replay.py` без сети.",
        "",
        "Офлайн-повтор всех шагов: `python -m ledgerhunt stage2 case001 --replay` (или "
        "`python run_stage2.py --only case001 --replay`).",
        "",
        "Ключи при выгрузке (только факт наличия): "
        + ", ".join(f"{k}={'да' if v else 'нет'}" for k, v in keys_present.items()) + ". "
        "Ключ передавался только тем источникам, у которых стоит «да» (TronGrid — заголовком, Etherscan — "
        "секретным параметром); в индекс и тела ключи не попадают.",
        "",
    ]
    for title, store in stores:
        rows = read_index(store)
        if not rows:
            continue
        by_src = Counter(r["provider"] for r in rows)
        size = sum(r.get("size") or 0 for r in rows)
        lines += [f"## {title}: `{store.as_posix().split('tests/fixtures/', 1)[-1]}`", "",
                  f"Ответов: {len(rows)}, объём тел: {size / 1024:.0f} КБ. По источникам: "
                  + ", ".join(f"{k} — {v}" for k, v in sorted(by_src.items())) + ".", ""]
        by_tag: dict[str, list[dict[str, Any]]] = defaultdict(list)
        for r in rows:
            by_tag[r.get("tag") or "-"].append(r)
        for tag, trs in by_tag.items():
            lines += [f"### Запуск `{tag}` ({len(trs)} ответов)", "",
                      "| № | Время UTC | Источник | Эндпоинт | Запрос | Статус | Байт | sha256 тела |",
                      "|---|---|---|---|---|---|---|---|"]
            for i, r in enumerate(trs, 1):
                lines.append(f"| {i} | {r['ts_utc'][:19].replace('T', ' ')} | {r['provider']} | {_cell(r['endpoint'], 60)} | "
                             f"{_cell(_request_label(r), 120)} | {r.get('status')} | {r.get('size')} | "
                             f"`{r.get('body_sha256') or '—'}` |")
            lines.append("")
    return "\n".join(lines) + "\n"


def report_md(*, run_id: str, mode: str, fact_summary: dict[str, Any], facts: list[dict[str, Any]],
              comparison: list[dict[str, Any]], coverage: list[dict[str, Any]], ref: dict[str, Any],
              step1: dict[str, Any], expected_check: dict[str, Any]) -> str:
    r = ref["result"]
    t = fact_summary["total"]
    L = [
        f"# case-001: перевыгрузка, сверка фактов и эталонный прогон (запуск {run_id}, режим HTTP: {mode})",
        "",
        "## Итог",
        "",
        f"- Шаг 1, перевыгрузка: {step1['requests']} запросов, ошибок {step1['errors']}, "
        f"время {step1['wall_s']} с.",
        f"- Шаг 2, сверка фактов: всего {fact_summary['facts']}; подтверждено {t['confirmed']}, "
        f"расхождений {t['mismatch']}, не проверяемо {t['not_verifiable']}.",
        f"- Шаг 3, эталонный прогон без AI: маршрут из {len(r['route'])} адресов, переходов между сетями "
        f"{len(r['cross_chain'])}, выходов на биржу {len(r['exchange_exits'])}, запросов "
        f"{ref['timings']['total_requests']}, время {ref['timings']['total_wall_ms'] / 1000:.1f} с.",
        f"- Шаг 4, сравнение с ground_truth: "
        + ", ".join(f"{VERDICT_RU.get(k, k)} — {v}" for k, v in Counter(c['verdict'] for c in comparison).items()) + ".",
        f"- Совпадение с сохранённым ожидаемым результатом: {expected_check.get('status')}.",
        "",
        "## Сравнение с ground_truth",
        "",
        "| Пункт | Эталон | Эталонный прогон | Итог | Примечание |",
        "|---|---|---|---|---|",
    ]
    for c in comparison:
        L.append(f"| {_cell(c['item'], 90)} | {_cell(c['expected'], 200)} | {_cell(c['observed'], 260)} | "
                 f"{VERDICT_RU.get(c['verdict'], c['verdict'])} | {_cell(c['note'], 200)} |")
    L += ["", "## Маршрут эталонного прогона", "", "| № | Сеть | Адрес | Роль | Пришло | Время UTC | Через |",
          "|---|---|---|---|---|---|---|"]
    for i, x in enumerate(r["route"], 1):
        L.append(f"| {i} | {x['chain']} | `{x['address']}` | {x['role']} | {x.get('arrived_amount') or ''} | "
                 f"{x.get('arrived_utc') or ''} | {x.get('via') or ''} |")
    L += ["", "## Рёбра (переводы, на которые опирается прогон)", "",
          "| № | Сеть | TXID | От | Кому | Сумма | Время UTC | Тип | Квитанция |", "|---|---|---|---|---|---|---|---|---|"]
    for e in r["edges"]:
        L.append(f"| {e['n']} | {e['chain']} | `{e['txid']}` | `{e['from']}` | `{e['to']}` | {e['amount']} | "
                 f"{e['timestamp_utc']} | {e['kind']} | {e['confirmed_by_receipt'] if e['confirmed_by_receipt'] is not None else ''} |")
    L += ["", "## Боковые ветки", "", "| Ветка | TXID | Кому | Сумма | Входит в потери |", "|---|---|---|---|---|"]
    for s in r["side_branches"]:
        L.append(f"| {_cell(s['branch'], 80)} | `{s.get('txid', '')}` | `{s.get('to') or ''}` | {s['amount']} | "
                 f"{'да' if s.get('counted_in_theft_loss') else 'нет'} |")
    va = r["value_accounting"]
    L += ["", "## Учёт стоимости до хаба", "", f"Украдено {va['stolen_amount']}, пришло на хаб {va['arrived_at_hub']}, "
          f"потеряно {va['total_lost_before_hub']}; сумма составляющих {va['components_sum']} "
          f"(сходится: {va['components_reconcile']}).", "", "| Составляющая | Где | Сумма |", "|---|---|---|"]
    for c in va["components"]:
        L.append(f"| {_cell(c['what'], 100)} | {_cell(c['at'], 90)} | {c['amount']} |")
    L += ["", "## Проверка выходов хаба", "",
          "| Выход хаба (TXID) | Время UTC | Сумма | Получатель | Переслал | Задержка, с | Куда | Итог |",
          "|---|---|---|---|---|---|---|---|"]
    for x in r["hub_outflow_checks"]:
        L.append(f"| `{x['hub_outflow_txid']}` | {x['hub_outflow_utc']} | {x['amount']} | `{x['recipient']}` | "
                 f"{x['forwarded_total_within_max_delay']} | {x['forward_delay_s'] if x['forward_delay_s'] is not None else ''} | "
                 f"{', '.join(x['forward_destinations'])} | {x['verdict']}{(' (' + x['exchange'] + ')') if x.get('exchange') else ''} |")
    L += ["", "## Связи", ""]
    for lk in r["links"]:
        L.append(f"- {lk['type']}: `{lk['funder']}` → {', '.join('`' + f['address'] + '`' for f in lk['funded'])}"
                 + (f"; уверенность: {lk['confidence']} (балл {lk['score']}, разных получателей TRX у спонсора: "
                    f"{lk['funder_fanout_distinct_trx_recipients']})" if lk.get("confidence") else
                    f"; {lk.get('interpretation', '')}"))
    L += ["", "## Охват транзакций эталона", "", "| Шаг | TXID | Вид | Как достигнут | Отличия |", "|---|---|---|---|---|"]
    for c in coverage:
        L.append(f"| {c['step']} | `{c['txid'][:18]}…` | {c['kind']} | {c['how']} | {_cell('; '.join(c['differences']), 200)} |")
    L += ["", "## Время и запросы эталонного прогона", "",
          "| Шаг | Запросов | Из записи | Время, мс | По источникам (запросов / сумма задержек, мс / ожидание лимита, мс) |",
          "|---|---|---|---|---|"]
    for s in ref["timings"]["steps"]:
        prov = "; ".join(f"{k}: {v['requests']} / {v['latency_ms']} / {v['rate_wait_ms']}" for k, v in s["by_provider"].items())
        L.append(f"| {_cell(s['step'], 80)} | {s['requests']} | {s['replayed']} | {s['wall_ms']} | {prov} |")
    L += ["", "## Сверка фактов (все строки)", "",
          "| № | Группа | Объект | Поле | Эталон | Сырые данные | Итог | Второй источник | Примечание |",
          "|---|---|---|---|---|---|---|---|---|"]
    for f in facts:
        L.append(f"| {f['n']} | {f['group']} | {_cell(f['subject'], 60)} | {_cell(f['field'], 90)} | {_cell(f['claim'], 120)} | "
                 f"{_cell(f['observed'], 160)} | {VERDICT_RU.get(f['verdict'], f['verdict'])} | "
                 f"{_cell(f['second_source'], 120)} | {_cell(f['note'], 160)} |")
    obs = fact_summary.get("observations") or []
    if obs:
        L += ["", "## Наблюдения (не расхождения)", ""]
        for o in obs:
            L.append(f"- {o['subject']}: {o['what']} = {_cell(o['observed'], 200)}; {o['note']}")
    if step1.get("keys_present"):
        L += ["", "Ключи при перевыгрузке (только наличие): "
              + ", ".join(f"{k}={'да' if v else 'нет'}" for k, v in step1["keys_present"].items()) + "."]
    if r["evidence_boundaries"]:
        L += ["", "## Границы доказательств", ""] + [f"- {b}" for b in r["evidence_boundaries"]]
    return "\n".join(L) + "\n"
