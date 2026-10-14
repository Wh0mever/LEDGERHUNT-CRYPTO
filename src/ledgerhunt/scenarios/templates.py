"""Scenario templates: 9 categories x 6 variants. Each variant randomises amounts, hop counts,
branch counts, timing and noise from the scenario's own random stream.

Categories (Prompt 3 section 9 plus the owners' additions):
direct, fan_out, merge, long_chain, cycles, exchange, incomplete_data, bridge, source_failure.

A template receives a Builder, builds the world with ``theft``/``hop``/``split``/... and
closes every lot with ``end`` (or a helper that ends it). It returns a short Russian title
and an English description; both go to expected.json only (input.json stays neutral).
"""

from __future__ import annotations

from typing import Callable

from .builder import Builder, Path

Template = Callable[[Builder], tuple[str, str]]


def _parts(b: Builder, total: int, k: int, min_share: int = 5) -> list[int]:
    """Split ``total`` raw units into k positive parts (each at least min_share % of an equal share)."""
    weights = [b.rng.randint(min_share, 100) for _ in range(k)]
    s = sum(weights)
    parts = [total * w // s for w in weights]
    parts[-1] += total - sum(parts)
    return parts


def _energy_service(b: Builder) -> str:
    return b.label(b.addr(), "SynthEnergy Rent", "energy_rental_service")


def _energy_fee(b: Builder) -> int:
    return b.rng.randint(2_000_000, 9_000_000)


# ---------------------------------------------------------------- direct


def d_single(b: Builder) -> tuple[str, str]:
    p = b.theft()
    b.end(p, "funds_at_rest")
    return "Прямой перевод: кража на один адрес", "theft to a single address that keeps the funds"


def d_hops_energy_fee(b: Builder) -> tuple[str, str]:
    svc = _energy_service(b)
    p = b.theft()
    p = b.fee(p, svc, _energy_fee(b))
    p = b.chain(p, b.rng.randint(2, 4))
    b.end(p, "funds_at_rest")
    return "Прямая цепочка с комиссией за аренду энергии", "straight hops; the thief pays an energy-rental fee (side branch)"


def d_two_installments(b: Builder) -> tuple[str, str]:
    p = b.theft(payments=[b.rng.amount(1_000_000_000, 40_000_000_000), b.rng.amount(20_000_000, 900_000_000)])
    t2 = b.addr()
    x = p.amount * b.rng.randint(30, 70) // 100
    for q in b.split(p, [(t2, x), (t2, p.amount - x)]):
        b.end(q, "funds_at_rest")
    return "Два платежа жертве, кража всего баланса, перевод двумя частями", "two installments to the same address (two routes)"


def d_approval_phishing(b: Builder) -> tuple[str, str]:
    p = b.theft(via_spender=True)
    p = b.chain(p, b.rng.randint(1, 2))
    b.end(p, "funds_at_rest")
    return "Кража через ранее выданное разрешение (transferFrom)", "approval phishing: theft signed by a spender via transferFrom"


def d_gas_funding_noise(b: Builder) -> tuple[str, str]:
    gas = b.source()
    p = b.theft()
    for _ in range(b.rng.randint(2, 4)):
        b.trx(gas, p.holder, b.rng.randint(20, 80) * 1_000_000)
        p = b.hop(p)
    b.end(p, "funds_at_rest")
    return "Прямая цепочка с пополнением TRX для газа", "hops funded with TRX by a common gas wallet (native noise)"


def d_known_service(b: Builder) -> tuple[str, str]:
    merchant = b.label(b.addr(), "SynthPay merchant gateway", "payment_service")
    p = b.theft()
    p = b.chain(p, b.rng.randint(1, 2))
    p = b.hop(p, merchant)
    b.end(p, "known_service")
    return "Цепочка заканчивается на известном сервисе", "ends at a labelled payment service"


# ---------------------------------------------------------------- fan_out


def f_split_k(b: Builder) -> tuple[str, str]:
    p = b.theft()
    k = b.rng.randint(2, 5)
    for q in b.split(p, [(None, v) for v in _parts(b, p.amount, k)]):
        b.end(q, "funds_at_rest")
    return "Разветвление на несколько адресов", f"split into {k} separate transfers"


def f_two_level(b: Builder) -> tuple[str, str]:
    p = b.theft()
    left, right = b.split(p, [(None, v) for v in _parts(b, p.amount, 2, 30)])
    for q in b.split(left, [(None, v) for v in _parts(b, left.amount, b.rng.randint(2, 3))]):
        b.end(q, "funds_at_rest")
    right = b.chain(right, b.rng.randint(1, 2))
    b.end(right, "funds_at_rest")
    return "Двухуровневое дерево разветвлений", "two-level split tree"


def f_batch_one_txid(b: Builder) -> tuple[str, str]:
    p = b.theft()
    if b.rng.chance(1, 2):
        p = b.hop(p)
    k = b.rng.randint(3, 5)
    for q in b.batch_split(p, [(None, v) for v in _parts(b, p.amount, k)]):
        b.end(q, "funds_at_rest")
    return "Разветвление одной транзакцией (несколько Transfer в одном TXID)", f"batch contract emits {k} transfers in one txid"


def f_one_percent(b: Builder) -> tuple[str, str]:
    collector = b.addr()
    p = b.theft()
    p = b.hop(p)
    p = b.fee(p, collector, p.amount // 100)
    p = b.chain(p, b.rng.randint(1, 2))
    b.end(p, "funds_at_rest")
    return "Отщепление ровно 1% на сборщик комиссии", "exactly 1% to an unlabelled collector, 99% onward"


def f_diamond(b: Builder) -> tuple[str, str]:
    p = b.theft()
    d = b.addr()
    a, c = b.split(p, [(None, v) for v in _parts(b, p.amount, 2, 30)])
    a = b.hop(a, d)
    c = b.chain(c, b.rng.randint(0, 1))
    c = b.hop(c, d)
    for q in b.merge_hop([a, c]):
        b.end(q, "funds_at_rest")
    return "Разветвление и повторное слияние без чужих средств", "split and re-merge of the same theft (not commingled)"


def f_exchange_branch(b: Builder) -> tuple[str, str]:
    hot = b.exchange("SynthEx Alpha")
    b.background_sweeps(hot, b.rng.randint(2, 4))
    p = b.theft()
    branches = b.split(p, [(None, v) for v in _parts(b, p.amount, b.rng.randint(2, 3), 20)])
    b.deposit(branches[0], "SynthEx Alpha", hot)
    for q in branches[1:]:
        b.end(q, "funds_at_rest")
    b.sweep(next(iter(b.exchanges)))
    return "Разветвление, одна ветка уходит на биржу", "split; one branch goes to an exchange deposit"


# ---------------------------------------------------------------- merge


def _uncertain_outflows(b: Builder, hub: str, *, k: int | None = None) -> None:
    k = k or b.rng.randint(2, 3)
    bal = b.bal[hub]
    for v in _parts(b, bal * b.rng.randint(60, 95) // 100, k):
        b.uncertain_out(hub, None, v)


def m_prefunded_hub(b: Builder) -> tuple[str, str]:
    hub = b.addr()
    b.foreign_in(hub, b.rng.amount(5_000_000_000, 200_000_000_000))
    p = b.theft()
    p = b.chain(p, b.rng.randint(1, 2))
    b.commingle(p, hub)
    _uncertain_outflows(b, hub)
    return "Слияние с чужими средствами на ранее пополненном адресе", "stolen funds join a hub that already holds foreign funds"


def m_foreign_after_arrival(b: Builder) -> tuple[str, str]:
    hub = b.addr()
    p = b.theft()
    p = b.chain(p, b.rng.randint(1, 2))
    b.commingle(p, hub)
    b.foreign_in(hub, b.rng.amount(2_000_000_000, 90_000_000_000))
    _uncertain_outflows(b, hub)
    return "Чужие средства приходят после украденных, до вывода", "foreign funds arrive after the stolen funds but before outflows"


def m_foreign_after_departure(b: Builder) -> tuple[str, str]:
    hub = b.addr()
    p = b.theft()
    p = b.hop(p, hub)
    p = b.hop(p)
    b.end(p, "funds_at_rest")
    b.tick(3600, 20000)
    b.foreign_in(hub, b.rng.amount(1_000_000_000, 30_000_000_000))
    key = b.usdt_transfer(hub, b.addr(), b.bal[hub])
    b.trap(key[0], "foreign_outflow", 0)
    b.notes.append("foreign funds reach the hub only after the stolen funds left: not commingled")
    return "Чужие средства пришли после ухода украденных: слияния нет", "foreign funds arrive only after the stolen funds left"


def m_two_branches_hub(b: Builder) -> tuple[str, str]:
    hub = b.addr()
    b.foreign_in(hub, b.rng.amount(10_000_000_000, 300_000_000_000))
    p = b.theft()
    for q in b.split(p, [(None, v) for v in _parts(b, p.amount, 2, 30)]):
        q = b.chain(q, b.rng.randint(0, 1))
        b.commingle(q, hub)
    _uncertain_outflows(b, hub)
    return "Две ветки кражи сливаются на адресе с чужими средствами", "two branches of the theft enter a prefunded hub"


def m_spent_history(b: Builder) -> tuple[str, str]:
    hub = b.addr()
    src = b.source()
    k1 = b.usdt_transfer(src, hub, b.rng.amount(1_000_000_000, 50_000_000_000), owner=src)
    b.trap(k1[0], "pre_theft_history", 0)
    k2 = b.usdt_transfer(hub, b.addr(), b.bal[hub])
    b.trap(k2[0], "pre_theft_history", 0)
    b.tick(86_400, 600_000)
    p = b.theft()
    p = b.hop(p, hub)
    p = b.hop(p)
    b.end(p, "funds_at_rest")
    b.notes.append("the hub had foreign funds earlier but its balance was zero when the stolen funds arrived")
    return "Адрес с прошлой историей и нулевым балансом: слияния нет", "hub had earlier foreign funds, fully spent before"


def m_hub_to_exchange(b: Builder) -> tuple[str, str]:
    hot = b.exchange("SynthEx Beta")
    b.background_sweeps(hot, b.rng.randint(2, 3))
    hub = b.addr()
    b.foreign_in(hub, b.rng.amount(20_000_000_000, 200_000_000_000))
    p = b.theft()
    p = b.chain(p, b.rng.randint(1, 2))
    b.commingle(p, hub)
    dep = b.addr()
    value = b.bal[hub] * b.rng.randint(40, 80) // 100
    b.uncertain_out(hub, dep, value)
    from .builder import _Exchange

    b.exchanges[dep] = _Exchange("SynthEx Beta", hot, pending=value)
    b.uncertain_exchanges.add(dep)
    b.sweep(dep)
    return "Смешанные средства уходят на депозит биржи", "commingled hub sends to an exchange deposit (uncertain origin)"


# ---------------------------------------------------------------- long_chain


def l_relay(b: Builder) -> tuple[str, str]:
    n = b.rng.randint(9, 13)
    p = b.chain(b.theft(), n)
    b.end(p, "funds_at_rest")
    return "Длинная цепочка 10-14 переходов", f"relay chain of {n + 1} transfers"


def l_relay_fees(b: Builder) -> tuple[str, str]:
    b.max_depth = 30
    svc = _energy_service(b)
    p = b.theft()
    n = b.rng.randint(14, 24)
    for _ in range(n):
        if b.rng.chance(1, 4):
            p = b.fee(p, svc, _energy_fee(b))
        p = b.hop(p)
    b.end(p, "funds_at_rest")
    return "Длинная цепочка 15-25 переходов с комиссиями", f"relay chain of {n + 1} transfers with energy fees"


def l_peel(b: Builder) -> tuple[str, str]:
    p = b.theft()
    n = b.rng.randint(10, 14)
    for _ in range(n):
        peel = p.amount * b.rng.randint(1, 5) // 100
        p = b.fee(p, b.addr(), peel)
        p = b.hop(p)
    b.end(p, "funds_at_rest")
    return "Цепочка отщеплений (peel chain)", f"peel chain: {n} hops, each peels 1-5% to a fresh address"


def l_beyond_depth(b: Builder) -> tuple[str, str]:
    b.max_depth = 12
    n = b.rng.randint(24, 29)
    p = b.chain(b.theft(), n)
    b.end(p, "funds_at_rest")
    return "Цепочка длиннее заданной глубины (12)", f"{n + 1} transfers with max_depth 12"


def l_to_exchange(b: Builder) -> tuple[str, str]:
    hot = b.exchange("SynthEx Gamma")
    b.background_sweeps(hot, b.rng.randint(2, 3))
    p = b.theft()
    for _ in range(b.rng.randint(9, 12)):
        b.tick(60, 7200)
        p = b.hop(p)
    dep = b.deposit(p, "SynthEx Gamma", hot)
    b.sweep(dep, delay=(300, 5400))
    return "Длинная цепочка до депозита биржи", "long chain with time gaps ending at an exchange deposit"


def l_to_bridge(b: Builder) -> tuple[str, str]:
    p = b.chain(b.theft(), b.rng.randint(9, 11))
    b.oft_send(p, 30101)
    return "Длинная цепочка до выхода в мост USDT0", "long chain ending with a USDT0-like OFT send to Ethereum"


# ---------------------------------------------------------------- cycles


def c_loop_back(b: Builder) -> tuple[str, str]:
    p = b.theft()
    a = p.holder
    p = b.chain(p, b.rng.randint(2, 3))
    p = b.hop(p, a)
    p = b.hop(p)
    b.end(p, "funds_at_rest")
    return "Цикл: средства возвращаются на адрес вора и уходят дальше", "loop A->B->C->A->D"


def c_ping_pong(b: Builder) -> tuple[str, str]:
    p = b.theft()
    a, other = p.holder, b.addr()
    for _ in range(b.rng.randint(2, 3)):
        p = b.hop(p, other)
        p = b.hop(p, a)
    p = b.hop(p)
    b.end(p, "funds_at_rest")
    return "Пинг-понг между двумя адресами", "funds bounce between two addresses, then leave"


def c_reconverge(b: Builder) -> tuple[str, str]:
    p = b.theft()
    x = b.addr()
    for q in b.split(p, [(None, v) for v in _parts(b, p.amount, 2, 30)]):
        q = b.chain(q, b.rng.randint(0, 1))
        q = b.hop(q, x)
        b.end(q, "funds_at_rest")
    return "Ветки сходятся на одном адресе разными переводами", "two branches end at the same address via separate transfers"


def c_partial_return(b: Builder) -> tuple[str, str]:
    p = b.theft()
    a = p.holder
    p = b.hop(p)
    r = p.amount * b.rng.randint(20, 45) // 100
    back, fwd = b.split(p, [(a, r), (None, p.amount - r)])
    back = b.hop(back)
    b.end(back, "funds_at_rest")
    b.end(fwd, "funds_at_rest")
    return "Частичный возврат на предыдущий адрес", "part returns to the previous address and leaves again"


def c_revisit_fee(b: Builder) -> tuple[str, str]:
    svc = _energy_service(b)
    p = b.theft()
    p = b.hop(p)
    bb = p.holder
    p = b.hop(p)
    p = b.fee(p, svc, _energy_fee(b))
    p = b.hop(p, bb)
    p = b.hop(p)
    b.end(p, "funds_at_rest")
    return "Повторное посещение адреса с комиссией по пути", "A->B->C (fee)->B->D"


def c_return_to_victim(b: Builder) -> tuple[str, str]:
    p = b.theft()
    victim = b.victim
    small = p.amount * b.rng.randint(1, 5) // 100
    back, fwd = b.split(p, [(victim, small), (None, p.amount - small)])
    b.end(back, "funds_at_rest")
    fwd = b.hop(fwd)
    b.end(fwd, "funds_at_rest")
    return "Часть средств возвращается жертве", "a small part returns to the victim address"


# ---------------------------------------------------------------- exchange


def e_deposit_sweep(b: Builder) -> tuple[str, str]:
    hot = b.exchange("SynthEx Alpha")
    b.background_sweeps(hot, b.rng.randint(2, 4))
    p = b.chain(b.theft(), b.rng.randint(0, 2))
    dep = b.deposit(p, "SynthEx Alpha", hot)
    b.sweep(dep, delay=(60, 1800))
    return "Депозит биржи и свип на горячий кошелёк", "deposit address forwards in full to a known hot wallet"


def e_two_deposits_one_sweep(b: Builder) -> tuple[str, str]:
    hot = b.exchange("SynthEx Beta")
    b.background_sweeps(hot, b.rng.randint(2, 3))
    p = b.theft()
    dep = b.addr()
    for q in b.split(p, [(None, v) for v in _parts(b, p.amount, 2, 30)]):
        q = b.chain(q, b.rng.randint(0, 1))
        b.deposit(q, "SynthEx Beta", hot, deposit=dep)
    b.sweep(dep)
    return "Два депозита на один адрес биржи, один свип", "two deposits to one deposit address, one sweep"


def e_two_exchanges(b: Builder) -> tuple[str, str]:
    hot_a = b.exchange("SynthEx Alpha")
    hot_b = b.exchange("SynthEx Gamma")
    b.background_sweeps(hot_a, 2)
    b.background_sweeps(hot_b, 2)
    p = b.theft()
    left, right = b.split(p, [(None, v) for v in _parts(b, p.amount, 2, 30)])
    d1 = b.deposit(b.chain(left, b.rng.randint(0, 1)), "SynthEx Alpha", hot_a)
    d2 = b.deposit(b.chain(right, b.rng.randint(0, 1)), "SynthEx Gamma", hot_b)
    b.sweep(d1)
    b.sweep(d2)
    return "Две ветки на две разные биржи", "two branches to two different exchanges"


def e_fast_forwarder(b: Builder) -> tuple[str, str]:
    hot = b.exchange("SynthEx Alpha")
    b.background_sweeps(hot, 2)
    p = b.theft()
    p = b.hop(p)
    b.tick(30, 180)
    p = b.hop(p)  # full and fast forward, but NOT to a known hot wallet
    b.end(p, "funds_at_rest")
    b.notes.append("the intermediate address forwards everything within minutes to an unlabelled address: not an exchange")
    return "Быстрая полная пересылка на неизвестный адрес: не биржа", "hard negative: fast full forward to an unknown address"


def e_direct_hot_wallet(b: Builder) -> tuple[str, str]:
    hot = b.exchange("SynthEx Gamma")
    b.background_sweeps(hot, 2)
    p = b.chain(b.theft(), b.rng.randint(1, 2))
    p = b.hop(p, hot)
    b.end(p, "exchange_hot_wallet")
    return "Перевод прямо на горячий кошелёк биржи", "transfer straight to a labelled exchange hot wallet"


def e_prior_activity(b: Builder) -> tuple[str, str]:
    hot = b.exchange("SynthEx Beta")
    dep = b.addr()
    user = b.source()
    for _ in range(b.rng.randint(1, 2)):  # the same deposit address was used before (earlier deposits and sweeps)
        k1 = b.usdt_transfer(user, dep, b.rng.amount(100_000_000, 5_000_000_000), owner=user)
        b.trap(k1[0], "unrelated", 0)
        b.tick(60, 1800)
        k2 = b.usdt_transfer(dep, hot, b.bal[dep])
        b.trap(k2[0], "exchange_internal", 0)
        b.tick(3600, 86_400)
    p = b.chain(b.theft(), b.rng.randint(1, 2))
    b.deposit(p, "SynthEx Beta", hot, deposit=dep)
    b.sweep(dep, delay=(3600, 14_400))
    return "Депозит с прошлой историей и задержанным свипом", "deposit address used before; sweep after hours"


# ---------------------------------------------------------------- incomplete_data


def i_poisoning(b: Builder) -> tuple[str, str]:
    p = b.theft()
    b.dust_to(b.victim, p.holder)
    for _ in range(b.rng.randint(2, 3)):
        nxt = b.addr()
        b.poison(p.holder, nxt)
        p = b.hop(p, nxt)
    b.poison(p.holder, b.addr())
    b.end(p, "funds_at_rest")
    return "Отравление адресов: нулевые переводы и пыль с похожих адресов", "zero-value poisoning and lookalike dust around the route"


def i_failed_then_success(b: Builder) -> tuple[str, str]:
    p = b.theft()
    for status in ("OUT_OF_ENERGY", "REVERT"):
        nxt = b.addr()
        b.failed(p.holder, nxt, p.amount, status)
        p = b.hop(p, nxt)
    b.end(p, "funds_at_rest")
    return "Неуспешные транзакции перед успешными", "failed transfers (OUT_OF_ENERGY, REVERT) before successful ones"


def i_missing_page_cut(b: Builder) -> tuple[str, str]:
    h = b.addr()
    b.spam(h, b.rng.randint(215, 240))
    b.tick(3600, 40_000)
    p = b.theft()
    p = b.hop(p, h)
    p = b.chain(p, b.rng.randint(1, 2))
    b.end(p, "funds_at_rest")
    b.outage("trongrid_v1", "trc20", h, status=500, page=2)
    return "Пропущенная страница: продолжение маршрута на недоступной странице", "page 2 of a busy hop fails; the onward transfer is on it"


def i_missing_page_continue(b: Builder) -> tuple[str, str]:
    p = b.theft()
    p = b.hop(p)
    h = p.holder
    p = b.hop(p)
    b.end(p, "funds_at_rest")
    b.tick(3600, 40_000)
    b.spam(h, b.rng.randint(215, 240))
    b.outage("trongrid_v1", "trc20", h, status=500, page=2)
    return "Пропущенная страница без потери маршрута", "page 2 fails but the route rows are on page 1"


def i_index_gap(b: Builder) -> tuple[str, str]:
    p = b.chain(b.theft(), b.rng.randint(1, 2))
    p = b.hop(p)
    b.hide(p.edges[-1])
    p = b.hop(p) if b.rng.chance(1, 2) else p
    b.end(p, "funds_at_rest")
    b.notes.append("one transfer is missing from the TronGrid v1 index; balanceOf shows the gap")
    return "Пробел в индексе: перевод не виден в списке TronGrid", "a transfer is missing from the v1 index (balance reveals it)"


def i_mixed_noise(b: Builder) -> tuple[str, str]:
    p = b.theft()
    for i in range(b.rng.randint(4, 6)):
        nxt = b.addr()
        noise = b.rng.randint(0, 2)
        if noise == 0:
            b.approve(p.holder, b.addr(), p.amount)
        elif noise == 1:
            b.poison(p.holder, nxt)
        else:
            b.failed(p.holder, nxt, p.amount)
        p = b.hop(p, nxt)
    b.end(p, "funds_at_rest")
    return "Смешанный шум: разрешения, отравление, неуспешные транзакции", "approvals, poisoning and failed txs along a chain"


# ---------------------------------------------------------------- bridge


def br_supported(b: Builder) -> tuple[str, str]:
    p = b.chain(b.theft(), b.rng.randint(1, 2))
    b.oft_send(p, 30101)
    return "Выход в мост USDT0 (OFT) в поддерживаемую сеть", "USDT0-like OFT send to Ethereum (supported, delivered)"


def br_unsupported_eid(b: Builder) -> tuple[str, str]:
    p = b.chain(b.theft(), b.rng.randint(1, 2))
    b.oft_send(p, 30110)
    return "Выход в мост USDT0 в неподдерживаемую сеть", "OFT send to an unsupported destination (evidence boundary)"


def br_not_indexed(b: Builder) -> tuple[str, str]:
    p = b.chain(b.theft(), b.rng.randint(1, 2))
    b.oft_send(p, 30101, indexed=False)
    return "Сообщение моста не найдено в LayerZero Scan", "OFT send whose message LayerZero Scan does not know (404)"


def br_unknown_bridge(b: Builder) -> tuple[str, str]:
    p = b.chain(b.theft(), b.rng.randint(1, 2))
    b.unknown_bridge(p, "SynthBridge X")
    return "Перевод в контракт неподдерживаемого моста", "transfer into a labelled bridge contract of an unsupported protocol"


def br_split_bridge_exchange(b: Builder) -> tuple[str, str]:
    hot = b.exchange("SynthEx Alpha")
    b.background_sweeps(hot, 2)
    p = b.theft()
    left, right = b.split(p, [(None, v) for v in _parts(b, p.amount, 2, 30)])
    b.oft_send(b.chain(left, b.rng.randint(0, 1)), 30101)
    dep = b.deposit(b.chain(right, b.rng.randint(0, 1)), "SynthEx Alpha", hot)
    b.sweep(dep)
    return "Одна ветка в мост, другая на биржу", "one branch bridges out, the other goes to an exchange"


def br_case001_like(b: Builder) -> tuple[str, str]:
    svc = _energy_service(b)
    collector = b.addr()
    p = b.theft()
    p = b.fee(p, svc, _energy_fee(b))
    p = b.hop(p)
    p = b.fee(p, collector, p.amount // 100)
    p = b.hop(p)
    b.oft_send(p, 30101)
    return "Схема как в case-001: комиссия, 1%, мост USDT0", "case-001 pattern: energy fee, 1% cut, OFT send to Ethereum"


# ---------------------------------------------------------------- source_failure


def s_listing_503(b: Builder) -> tuple[str, str]:
    p = b.chain(b.theft(), b.rng.randint(1, 2))
    h = p.holder
    p = b.chain(p, b.rng.randint(1, 2))
    b.end(p, "funds_at_rest")
    b.outage("trongrid_v1", "trc20", h, status=503)
    return "Список переводов адреса недоступен (503)", "TronGrid listing of a hop answers 503"


def s_listing_429_branch(b: Builder) -> tuple[str, str]:
    p = b.theft()
    left, right = b.split(p, [(None, v) for v in _parts(b, p.amount, 2, 30)])
    left = b.hop(left)
    b.end(left, "funds_at_rest")
    h = right.holder
    right = b.chain(right, b.rng.randint(1, 2))
    b.end(right, "funds_at_rest")
    b.outage("trongrid_v1", "trc20", h, status=429)
    return "Лимит запросов (429) на одной ветке", "persistent 429 on one branch holder's listing"


def s_secondary_down(b: Builder) -> tuple[str, str]:
    p = b.chain(b.theft(), b.rng.randint(2, 4))
    b.end(p, "funds_at_rest")
    b.outage("secondary_node", "gettransactioninfobyid", "*", status=503)
    return "Второй источник квитанций недоступен", "second receipt source down: transfers stay unverified"


def s_layerzero_down(b: Builder) -> tuple[str, str]:
    p = b.chain(b.theft(), b.rng.randint(1, 2))
    p = b.oft_send(p, 30101)
    b.outage("layerzero_scan", "*", p.edges[-1][0], status=503)
    return "LayerZero Scan недоступен при выходе в мост", "bridge API down at the OFT send"


def s_secondary_partial(b: Builder) -> tuple[str, str]:
    p = b.chain(b.theft(), b.rng.randint(3, 5))
    b.end(p, "funds_at_rest")
    for key in b.rng.sample(list(p.edges[1:]), b.rng.randint(1, 2)):
        b.outage("secondary_node", "gettransactioninfobyid", key[0], status=503)
    return "Второй источник не отдаёт часть квитанций", "second receipt source fails for 1-2 transactions"


def s_events_down(b: Builder) -> tuple[str, str]:
    p = b.chain(b.theft(), b.rng.randint(1, 2))
    for q in b.batch_split(p, [(None, v) for v in _parts(b, p.amount, b.rng.randint(2, 3))]):
        b.end(q, "funds_at_rest")
    b.outage("trongrid_v1", "events", "*", status=503)
    return "Эндпоинт событий TronGrid недоступен", "TronGrid events endpoint down (event_index from receipts)"


CATEGORIES: dict[str, list[tuple[str, Template]]] = {
    "direct": [("single", d_single), ("hops_energy_fee", d_hops_energy_fee), ("two_installments", d_two_installments),
               ("approval_phishing", d_approval_phishing), ("gas_funding_noise", d_gas_funding_noise),
               ("known_service", d_known_service)],
    "fan_out": [("split_k", f_split_k), ("two_level", f_two_level), ("batch_one_txid", f_batch_one_txid),
                ("one_percent", f_one_percent), ("diamond", f_diamond), ("exchange_branch", f_exchange_branch)],
    "merge": [("prefunded_hub", m_prefunded_hub), ("foreign_after_arrival", m_foreign_after_arrival),
              ("foreign_after_departure", m_foreign_after_departure), ("two_branches_hub", m_two_branches_hub),
              ("spent_history", m_spent_history), ("hub_to_exchange", m_hub_to_exchange)],
    "long_chain": [("relay", l_relay), ("relay_fees", l_relay_fees), ("peel", l_peel),
                   ("beyond_depth", l_beyond_depth), ("to_exchange", l_to_exchange), ("to_bridge", l_to_bridge)],
    "cycles": [("loop_back", c_loop_back), ("ping_pong", c_ping_pong), ("reconverge", c_reconverge),
               ("partial_return", c_partial_return), ("revisit_fee", c_revisit_fee),
               ("return_to_victim", c_return_to_victim)],
    "exchange": [("deposit_sweep", e_deposit_sweep), ("two_deposits_one_sweep", e_two_deposits_one_sweep),
                 ("two_exchanges", e_two_exchanges), ("fast_forwarder", e_fast_forwarder),
                 ("direct_hot_wallet", e_direct_hot_wallet), ("prior_activity", e_prior_activity)],
    "incomplete_data": [("poisoning", i_poisoning), ("failed_then_success", i_failed_then_success),
                        ("missing_page_cut", i_missing_page_cut), ("missing_page_continue", i_missing_page_continue),
                        ("index_gap", i_index_gap), ("mixed_noise", i_mixed_noise)],
    "bridge": [("oft_supported", br_supported), ("oft_unsupported_eid", br_unsupported_eid),
               ("oft_not_indexed", br_not_indexed), ("unknown_bridge", br_unknown_bridge),
               ("split_bridge_exchange", br_split_bridge_exchange), ("case001_like", br_case001_like)],
    "source_failure": [("listing_503", s_listing_503), ("listing_429_branch", s_listing_429_branch),
                       ("secondary_down", s_secondary_down), ("layerzero_down", s_layerzero_down),
                       ("secondary_partial", s_secondary_partial), ("events_down", s_events_down)],
}

__all__ = ["CATEGORIES", "Path"]
