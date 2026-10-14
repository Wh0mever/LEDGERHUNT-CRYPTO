# 4.6 Тестовые сценарии — итог прогона

- Набор для разработки: 54 синтетических сценариев + эталон case-001; категорий 9, по 6–6 в каждой.
- Генерация: 26.28 с; файлов 3010, объём 9155947 байт; изменения относительно прошлой версии: False.
- Проверка набора для разработки: прошли 55 из 55 (ошибок 0); проверка воспроизведения через клиентов фундамента в режиме replay включена.
- Самопроверка оценщика (эталон как кандидат): сценариев засчитано 45 из 45, полнота фактов 1.0, ложных фактов 0; сценариев с отказом источника 9 (вне знаменателя).
- Проверка оценщика на всём наборе: пустой результат — засчитано 0 сценариев; один выдуманный факт в идеальном результате — засчитано 0, ложных фактов 54.
- Отложенный набор: 27 сценариев; хеши файлов совпали 1695 из 1695; повторная генерация: identical; структурная проверка: 27 из 27. Содержимое отложенного набора в отчёт не выводится.

## Сверка форматов с реальными ответами (data/http-store)

| Источник | Эндпоинт | Реальных | Синтетических | Нет в синтетике | Лишнее в синтетике |
|---|---|---|---|---|---|
| trongrid | `v1/accounts/{address}/transactions/trc20` | 346 | 497 | — | — |
| trongrid | `v1/accounts/{address}/transactions` | 2 | 499 | meta.fingerprint, meta.links, meta.links.next | data[].raw_data.fee_limit |
| trongrid | `v1/transactions/{hash}/events` | 393 | 444 | data[].result.amount, data[].result.token, data[].result_type.amount, data[].result_type.token | data[].result.owner, data[].result.spender, data[].result_type.owner, data[].result_type.spender |
| trongrid | `wallet/gettransactionbyid` | 111 | 456 | raw_data.contract[].Permission_id | — |
| trongrid | `walletsolidity/gettransactioninfobyid` | 400 | 456 | receipt.origin_energy_usage | resMessage, result |
| trongrid | `wallet/triggerconstantcontract` | 2 | 499 | — | — |
| layerzero_scan | `v1/messages/tx/{hash}` | 65 | 5 | — | — |

Подробности: `raw/` в папке прогона; описание набора — docs/stage-2/test-scenarios.md.
