# 4.6 Тестовые сценарии — итог прогона

- Набор для разработки: 54 синтетических сценариев + эталон case-001; категорий 9, по 6–6 в каждой.
- Генерация: 18.49 с; файлов 3010, объём 9155947 байт; изменения относительно прошлой версии: None.
- Проверка набора для разработки: прошли 55 из 55 (ошибок 0); проверка воспроизведения через клиентов фундамента в режиме replay включена.
- Самопроверка оценщика (эталон как кандидат): сценариев засчитано 45 из 45, полнота фактов 1.0, ложных фактов 0; сценариев с отказом источника 9 (вне знаменателя).
- Отложенный набор: 27 сценариев; хеши файлов совпали 1695 из 1695; повторная генерация: identical; структурная проверка: 27 из 27. Содержимое отложенного набора в отчёт не выводится.

## Сверка форматов с реальными ответами (data/http-store)

| Источник | Эндпоинт | Реальных | Синтетических | Нет в синтетике | Лишнее в синтетике |
|---|---|---|---|---|---|
| trongrid | `v1/accounts/{address}/transactions/trc20` | 9 | 497 | — | — |
| trongrid | `v1/accounts/{address}/transactions` | 2 | 499 | meta.fingerprint, meta.links, meta.links.next | data[].raw_data.fee_limit |
| trongrid | `v1/transactions/{hash}/events` | 9 | 444 | — | data[].result.owner, data[].result.spender, data[].result_type.owner, data[].result_type.spender |
| trongrid | `wallet/gettransactionbyid` | 3 | 456 | — | — |
| trongrid | `walletsolidity/gettransactioninfobyid` | 9 | 456 | — | receipt.net_usage, resMessage, result |
| trongrid | `wallet/triggerconstantcontract` | 2 | 499 | — | — |
| layerzero_scan | `v1/messages/tx/{hash}` | 8 | 5 | — | — |

Подробности: `raw/` в папке прогона; описание набора — docs/stage-2/test-scenarios.md.
