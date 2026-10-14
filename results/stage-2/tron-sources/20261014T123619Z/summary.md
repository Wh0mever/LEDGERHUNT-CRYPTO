# tron_sources: замер источников TRON — прогон 20261014T123619Z

Режим HTTP: `record`. Ключи (только наличие): TRONGRID_API_KEY — есть, TRON_RPC_URL — нет, TRON_RPC_URL_2 — нет, TRONSCAN_API_KEY — нет.

## Нагрузка (ramp до первого 429, затем устойчивый прогон)

| Источник | Первый 429 на ступени, зап/с | Последняя чистая ступень | Пауза после 429: первый успех через, с | Устойчиво, зап/с (успешных) | Ошибки | p50 / p95, мс |
|---|---|---|---|---|---|---|
| trongrid_keyless | 4 | 3 | 5, 5 | 2.01 (план 2) | 0.0 | 189.0 / 418.2 |
| trongrid_key | 15 | 10 | 30 | 9.983 (план 10) | 0.0 | 196.4 / 469.0 |
| publicnode | нет до потолка ступеней | 10 | — | 10.002 (план 10) | 0.0 | 100.6 / 120.7 |

## Свежесть

| Источник | Отставание solidified, блоков (медиана) | секунд (медиана) |
|---|---|---|
| publicnode | 18.0 | 54.0 |
| trongrid_key | 18.0 | 54.0 |

Индекс TronGrid v1: последнее событие USDT отстаёт от головы на 1.0 блоков (медиана).

## Глубина истории PublicNode

Самый старый отдаваемый блок 86792411 (2026-10-03 17:51:21 UTC), глубина 10.78 сут. Квитанции (gettransactioninfobyid): примерно с блока 86857920 (2026-10-06 00:27:48 UTC). `eth_getLogs`: {"inside_receipt_history": {"range": [86858020, 86859019], "trongrid_key": {"logs": 21, "status": 200, "ref": {"store": "data/http-store", "body_sha256": "e5bfcbf0c214e546e57a5a0756bd2223de9a91de0880f092cff42c899ff023be", "key_sha256": "8b87230ed0519ad1a72520fb36cf98fa3dedce212ec67a7f9fa6c1edfb120c60", "object_path": "data/http-store/objects/e5/e5bfcbf0c214e546e57a5a0756bd2223de9a91de0880f092cff42c899ff023be"}}, "publicnode": {"logs": 21, "status": 200, "ref": {"store": "data/http-store", "body_sha256": "e5bfcbf0c214e546e57a5a0756bd2223de9a91de0880f092cff42c899ff023be", "key_sha256": "33ce5ebf.

## Полнота TRC20: v1 против логов узла

| Источник логов | Окон | Переводов в логах | В v1 | Совпало | Только v1 | Только логи |
|---|---|---|---|---|---|---|
| trongrid_key | 20 | 3788 | 3788 | 3788 | 0 | 0 |
| publicnode | 6 | 1640 | 1661 | 1640 | 21 | 0 |

## event_index против порядка логов в квитанции

- publicnode: {"txids": 90, "receipt_empty": 0, "transfer_events": 90, "equal": 90, "differ": 0, "missing_in_receipt": 0, "missing_in_v1": 0, "errors": 0}
- trongrid_key: {"txids": 229, "receipt_empty": 0, "transfer_events": 229, "equal": 229, "differ": 0, "missing_in_receipt": 0, "missing_in_v1": 0, "errors": 0}
- repeat_request_same_event_index: {"checked": 10, "same": 10}

## Совпадение транзакций между операторами

- case-001: {"publicnode": {"answered": 5, "empty_tx": 5, "empty_receipt": 5, "tx_compared": 0, "tx_equal": 0, "tx_bytes_equal": 0, "receipt_compared": 0, "receipt_equal": 0, "receipt_bytes_equal": 0, "diff_paths": []}}
- recent: {"publicnode": {"answered": 30, "empty_tx": 0, "empty_receipt": 0, "tx_compared": 30, "tx_equal": 30, "tx_bytes_equal": 30, "receipt_compared": 30, "receipt_equal": 30, "receipt_bytes_equal": 30, "diff_paths": []}}

## Постраничная выдача

| Цель | Страниц | Строк | Полная | Дубли | Нарушения порядка | Строк в час | p50, мс |
|---|---|---|---|---|---|---|---|
| hot_wallet_desc | 60 | 12000 | False | 0 | 0 | 377.2 | 627.9 |
| hub_asc | 12 | 2240 | True | 0 | 0 | 1.4 | 426.6 |

## Не измерено

- свежесть (отставание solidified): платный TRON RPC (TRON_RPC_URL): не измерено: нет ключа (TRON_RPC_URL не задан). Нужно: URL узла провайдера в .env как TRON_RPC_URL; код подхватит его сам
- свежесть (отставание solidified): платный TRON RPC (TRON_RPC_URL_2): не измерено: нет ключа (TRON_RPC_URL_2 не задан). Нужно: URL узла провайдера в .env как TRON_RPC_URL_2; код подхватит его сам
- глубина истории (архивность): платный TRON RPC (TRON_RPC_URL): не измерено: нет ключа (TRON_RPC_URL не задан). Нужно: URL узла провайдера в .env как TRON_RPC_URL; код подхватит его сам
- глубина истории (архивность): платный TRON RPC (TRON_RPC_URL_2): не измерено: нет ключа (TRON_RPC_URL_2 не задан). Нужно: URL узла провайдера в .env как TRON_RPC_URL_2; код подхватит его сам
- совпадение транзакций с TronGrid: платный TRON RPC (TRON_RPC_URL): не измерено: нет ключа (TRON_RPC_URL не задан). Нужно: URL узла провайдера в .env как TRON_RPC_URL; код подхватит его сам
- совпадение транзакций с TronGrid: платный TRON RPC (TRON_RPC_URL_2): не измерено: нет ключа (TRON_RPC_URL_2 не задан). Нужно: URL узла провайдера в .env как TRON_RPC_URL_2; код подхватит его сам
- полнота истории TRC20 (логи независимого архивного узла по окну case-001): платный TRON RPC (TRON_RPC_URL): не измерено: нет ключа (TRON_RPC_URL не задан). Нужно: URL узла провайдера в .env как TRON_RPC_URL; код подхватит его сам
- полнота истории TRC20 (логи независимого архивного узла по окну case-001): платный TRON RPC (TRON_RPC_URL_2): не измерено: нет ключа (TRON_RPC_URL_2 не задан). Нужно: URL узла провайдера в .env как TRON_RPC_URL_2; код подхватит его сам
- лимит, задержки, устойчивая скорость: платный TRON RPC (TRON_RPC_URL): не измерено: нет ключа (TRON_RPC_URL не задан). Нужно: URL узла провайдера в .env как TRON_RPC_URL; код подхватит его сам
- лимит, задержки, устойчивая скорость: платный TRON RPC (TRON_RPC_URL_2): не измерено: нет ключа (TRON_RPC_URL_2 не задан). Нужно: URL узла провайдера в .env как TRON_RPC_URL_2; код подхватит его сам
