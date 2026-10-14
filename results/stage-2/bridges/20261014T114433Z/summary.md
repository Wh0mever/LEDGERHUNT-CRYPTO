# Мосты и источники Ethereum — итог замера

Дата (UTC): 2026-10-14. Режим HTTP: record. Использованы ключи: Etherscan — да; Blockscout PRO — нет; платный ETH RPC — нет; ключ партнёра 1Click — нет; Rango — нет; TronGrid — да.

## Источники: доступность и задержка

| Источник | Вызовов | Успешно | Доля | HTTP-запросов | 429 | Повторы | p50, мс | p95, мс | max, мс |
|---|---|---|---|---|---|---|---|---|---|
| blockscout_eth | 99 | 97 | 0.9798 | 150 | 10 | 8 | 289.6 | 2057.9 | 3763.3 |
| eth_drpc | 47 | 47 | 1.0 | 47 | 0 | 0 | 226.9 | 267.2 | 287.1 |
| eth_publicnode | 58 | 53 | 0.9138 | 58 | 0 | 0 | 128.9 | 255.6 | 299.4 |
| eth_tenderly | 47 | 47 | 1.0 | 47 | 0 | 0 | 278.2 | 373.9 | 467.5 |
| etherscan_v2 | 27 | 27 | 1.0 | 27 | 0 | 0 | 623.4 | 794.0 | 1015.1 |
| etherscan_v2_keyless | 1 | 0 | 0.0 | 1 | 0 | 0 | 619.3 | 619.3 | 619.3 |
| layerzero_scan | 29 | 29 | 1.0 | 30 | 0 | 0 | 179.8 | 526.1 | 643.2 |
| near_intents_1click | 27 | 27 | 1.0 | 28 | 0 | 0 | 104.4 | 205.4 | 311.5 |
| trongrid | 23 | 23 | 1.0 | 23 | 0 | 0 | 242.0 | 580.2 | 686.7 |
| usdt0_docs | 1 | 1 | 1.0 | 1 | 0 | 0 | 1018.0 | 1018.0 | 1018.0 |

## Публичные Ethereum RPC (кандидаты)

| Провайдер | Пригоден | Квитанция 3-недельной давности | eth_getLogs 50 блоков | Пустой ответ вместо события | Ошибка |
|---|---|---|---|---|---|
| eth_publicnode | False | True | False | False | source_error: eth_publicnode eth_getLogs: HTTP 403: {"jsonrpc":"2.0","error":{"code":-3260 |
| eth_drpc | True | True | True | False |  |
| eth_tenderly | True | True | True | False |  |
| eth_nodies | True | True | True | False |  |
| eth_mevblocker | True | True | True | False |  |
| eth_1rpc | True | True | True | False |  |
| eth_flashbots | False | False | False | False | jsonrpc_error: {'code': 4444, 'message': 'pruned history unavailable'} |
| eth_cloudflare | False | False | False | False | jsonrpc_error: {'code': -32603, 'message': 'Internal error'} |
| eth_llamarpc | False | None | None | None | source_error: eth_llamarpc eth_chainId: HTTP 525: {"type":"https://developers.cloudflare.c |
| eth_ankr | False | None | None | None | jsonrpc_error: {'code': -32000, 'message': 'Unauthorized: You must authenticate your reque |
| eth_blockpi | False | None | None | None | source_error: eth_blockpi eth_chainId: HTTP 503: {"jsonrpc":"2.0","error":{"code":100021," |
| eth_merkle | False | None | None | None | source_error: eth_merkle eth_chainId: HTTP 429: {"id":null,"error":{"code":-32005,"message |
| eth_onfinality | False | None | None | None | source_error: eth_onfinality eth_chainId: HTTP 429: {"jsonrpc":"2.0","error":{"code":-3202 |

## Мосты

- USDT0/LayerZero (TRON → Ethereum): потоков 6; выход распознан по сырым логам TRON: 6; получатель совпал (LZ Scan и OFTReceived): 6; tx назначения найдена без LZ Scan и совпала: 6; суммы совпали: 6; комиссия, б.п.: ['3.00']; доставка, с: [116, 128, 125, 125, 128, 125]; запасной путь нашёл событие: {'blockscout_api': 4, 'eth_drpc': 6, 'eth_tenderly': 6, 'etherscan_v2': 6}.
- Rango: потоков 8; маршруты: {'near_intents_1click': 7, 'usdt0': 1}; событие RangoBridgeInitiated: 5; bridgeId и маршрут: ['51:usdt0', '60:near_intents_1click']; получатели: ['TH79bEmJTcU6iRhbB67bDz4QmE4f4CqAQp', 'TV7fPGpLvuxWKx7waYkcr6e615w3T8Q5mM', 'TYHeH2HQn7pM5fe6aYwGabz9x4yizJbwp6']; получатель начинается с префикса из события: 5; выплата совпала с получателем: 8; выплата минус amountOut 1Click: ['0.043506', '0.043445', '0.044735', '0.043488', '0.042558', '0.080423']; кошельки выплат: ['TX5XiRXdyz7sdFwF5mnhT1QoGCpbkncpke']; поиск без 1Click: попыток 6, один кандидат 6, совпал с 1Click 6; депозит переведён в хранилище NEAR Intents: 7; посторонних (не USDT) переводов с депозитных адресов: 1; наш декодер совпал с декодером Blockscout: 5 из 5.
- Согласие источников Ethereum: 17 из 21 транзакций совпали полностью; пустые квитанции: {'eth_publicnode': 4, 'eth_drpc': 0, 'eth_tenderly': 0, 'etherscan_v2': 0}; пропуски в token-transfers Blockscout: 1.

## Сверка с эталоном case-001

Фактов: 54, совпало: 54, расходится: 0, не проверено: 0.

Наблюдения (не расхождения с эталоном, а разный смысл полей):

- шаг 16, 1Click originChainTxHashes vs fixture step 16 tx (different meaning: deposit tx vs sweep): эталон `0x224f3859d03f8a26fc697b7b2978d4a701cf3db1d280dbd911e18b508b54e762`, наблюдение `0x41bac088520409376e60709fd7114b7b3d670abeedfb01a68b7ee42a84ec515a` (1Click originChainTxHashes)
- шаг 17, TRON payout amount vs 1Click amountOut (fixture note: differs): эталон `12878.454902`, наблюдение `12878.410167` (1Click swapDetails.amountOut)

## Не измерено

- платный Ethereum RPC — не измерено: нет ETH_RPC_URL; нужно: URL платного провайдера в .env (переменная ETH_RPC_URL)
- Blockscout PRO API (api.blockscout.com, с ключом) — не измерено: нет BLOCKSCOUT_API_KEY; нужно: бесплатный ключ PRO API (dev.blockscout.com) в .env
- статус 1Click с ключом партнёра — не измерено: нет NEAR_INTENTS_JWT; нужно: ключ из partners.near-intents.org в .env
- Rango status API (/basic/status) — не измерено: нет RANGO_API_KEY; нужно: ключ Rango (выдаётся через тикет в Discord) в .env под именем RANGO_API_KEY

Всего HTTP-запросов в прогоне: 442.
