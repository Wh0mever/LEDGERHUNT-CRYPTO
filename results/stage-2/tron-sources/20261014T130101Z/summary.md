# tron_sources: замер источников TRON — прогон 20261014T130101Z

Режим HTTP: `replay`. Ключи (только наличие): TRONGRID_API_KEY — есть, TRON_RPC_URL — нет, TRON_RPC_URL_2 — нет, TRONSCAN_API_KEY — нет.

Офлайн-повтор: фазы A, C, P пересчитаны из записанных ответов; F, D, L — из сырых строк живого прогона `results/stage-2/tron-sources/20261014T124823Z`.

## Нагрузка (ramp до первого 429, затем устойчивый прогон)

| Источник | Первый 429 на ступени, зап/с | Лимит / пауза в теле 429 | Последняя чистая ступень | Пауза после 429: первый успех через, с | Устойчиво, зап/с (успешных) | Ошибки | p50 / p95, мс |
|---|---|---|---|---|---|---|---|
| trongrid_keyless | 4 | 3 / 5 с | 3 | 5, 5 | 2.01 (план 2) | 0.0 | 191.5 / 427.5 |
| trongrid_key | 15 | 15 / 30 с | 10 | 30, 30 | 9.911 (план 10) | 0.0 | 200.4 / 500.7 |
| publicnode | нет до потолка ступеней | — / — с | 10 | — | 10.001 (план 10) | 0.0 | 101.1 / 134.6 |

## Свежесть

| Источник | Отставание solidified, блоков (медиана) | секунд (медиана) |
|---|---|---|
| publicnode | 18.0 | 54.0 |
| trongrid_key | 18.0 | 54.0 |

Индекс TronGrid v1: последнее событие USDT отстаёт от головы на 1.0 блоков (медиана).

## Глубина истории PublicNode

Самый старый отдаваемый блок 86792411 (2026-10-03 17:51:21 UTC), глубина 10.79 сут. Квитанции (gettransactioninfobyid): примерно с блока 86857908 (2026-10-06 00:27:12 UTC). `eth_getLogs` (USDT Transfer от TX5XiR…): inside_receipt_history [86858008, 86859007]: trongrid_key 22, publicnode 22; below_receipt_history [86856780, 86857779]: trongrid_key 36, publicnode 0.

## Полнота TRC20: v1 против логов узла

| Источник логов | Окон | Переводов в логах | В v1 | Совпало | Только v1 | Только логи |
|---|---|---|---|---|---|---|
| trongrid_key | 20 | 3794 | 3794 | 3794 | 0 | 0 |
| publicnode | 6 | 1646 | 1667 | 1646 | 21 | 0 |

## event_index против порядка логов в квитанции

- publicnode: {"txids": 89, "receipt_empty": 0, "transfer_events": 89, "equal": 89, "differ": 0, "missing_in_receipt": 0, "missing_in_v1": 0, "errors": 0}
- trongrid_key: {"txids": 228, "receipt_empty": 0, "transfer_events": 228, "equal": 228, "differ": 0, "missing_in_receipt": 0, "missing_in_v1": 0, "errors": 0}
- repeat_request_same_event_index: {"checked": 10, "same": 10}

## Совпадение транзакций между операторами

- case-001: {"publicnode": {"answered": 5, "empty_tx": 5, "empty_receipt": 5, "tx_compared": 0, "tx_equal": 0, "tx_bytes_equal": 0, "receipt_compared": 0, "receipt_equal": 0, "receipt_bytes_equal": 0, "diff_paths": []}}
- recent: {"publicnode": {"answered": 30, "empty_tx": 0, "empty_receipt": 0, "tx_compared": 30, "tx_equal": 30, "tx_bytes_equal": 30, "receipt_compared": 30, "receipt_equal": 30, "receipt_bytes_equal": 30, "diff_paths": []}}

## Постраничная выдача

| Цель | Страниц | Строк | Полная | Дубли | Нарушения порядка | Строк в час | p50, мс |
|---|---|---|---|---|---|---|---|
| hot_wallet_desc | 60 | 12000 | False | 0 | 0 | 377.2 | 548.4 |
| hub_asc | 12 | 2240 | True | 0 | 0 | 1.4 | 503.6 |

## Не измерено

- свежесть (отставание solidified): платный TRON RPC (TRON_RPC_URL): не измерено: нет ключа (TRON_RPC_URL не задан). Нужно: URL узла провайдера в .env как TRON_RPC_URL; код подхватит его сам
- свежесть (отставание solidified): платный TRON RPC (TRON_RPC_URL_2): не измерено: нет ключа (TRON_RPC_URL_2 не задан). Нужно: URL узла провайдера в .env как TRON_RPC_URL_2; код подхватит его сам
- совпадение транзакций с TronGrid: платный TRON RPC (TRON_RPC_URL): не измерено: нет ключа (TRON_RPC_URL не задан). Нужно: URL узла провайдера в .env как TRON_RPC_URL; код подхватит его сам
- совпадение транзакций с TronGrid: платный TRON RPC (TRON_RPC_URL_2): не измерено: нет ключа (TRON_RPC_URL_2 не задан). Нужно: URL узла провайдера в .env как TRON_RPC_URL_2; код подхватит его сам
- полнота истории TRC20 (логи независимого архивного узла по окну case-001): платный TRON RPC (TRON_RPC_URL): не измерено: нет ключа (TRON_RPC_URL не задан). Нужно: URL узла провайдера в .env как TRON_RPC_URL; код подхватит его сам
- полнота истории TRC20 (логи независимого архивного узла по окну case-001): платный TRON RPC (TRON_RPC_URL_2): не измерено: нет ключа (TRON_RPC_URL_2 не задан). Нужно: URL узла провайдера в .env как TRON_RPC_URL_2; код подхватит его сам
- лимит, задержки, устойчивая скорость: платный TRON RPC (TRON_RPC_URL): не измерено: нет ключа (TRON_RPC_URL не задан). Нужно: URL узла провайдера в .env как TRON_RPC_URL; код подхватит его сам
- лимит, задержки, устойчивая скорость: платный TRON RPC (TRON_RPC_URL_2): не измерено: нет ключа (TRON_RPC_URL_2 не задан). Нужно: URL узла провайдера в .env как TRON_RPC_URL_2; код подхватит его сам
