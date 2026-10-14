# Проверка эндпоинтов источников (foundation)

Запуск: `20261014T105339Z`, режим HTTP: `record`. Запросы без ключей, идентификаторы case-001.

| Проба | Статус | Проверка |
|---|---|---|
| trongrid.v1.trc20_transfers (limit=2, fingerprint pagination) | 200,200 | пройдена |
| trongrid.v1.account_transactions | 200 | пройдена |
| trongrid.v1.transaction_events | 200 | пройдена |
| trongrid.v1.contract_events (USDT Transfer, block 86439360) | 200 | пройдена |
| trongrid.wallet/gettransactionbyid | 200 | пройдена |
| trongrid.walletsolidity/gettransactioninfobyid | 200 | пройдена |
| trongrid.wallet/getaccount | 200 | пройдена |
| trongrid.wallet/triggerconstantcontract (USDT balanceOf hub) | 200 | пройдена |
| tron_publicnode.wallet/getaccount | 200 | пройдена |
| tron_publicnode.walletsolidity/getaccount | 200 | пройдена |
| tron_publicnode.walletsolidity/gettransactioninfobyid (case-001 theft, expected to be outside history) | 200 | пройдена |
| blockscout.transaction (Rango tx) | 200 | пройдена |
| blockscout.transaction_token_transfers | 200 | пройдена |
| blockscout.transaction_logs | 200 | пройдена |
| blockscout.address_token_transfers (1 page) | 200 | пройдена |
| eth_rpc.eth_getTransactionReceipt (USDT0 bridge-in) | 200 | пройдена |
| eth_rpc.eth_getTransactionByHash | 200 | пройдена |
| eth_rpc.eth_getBlockByNumber(26025709) | 200 | пройдена |
| layerzero_scan.messages_by_tx (TRON tx, 0x added) | 200 | пройдена |
| layerzero_scan.message_by_guid | 200 | пройдена |
| near_intents.status(depositAddress) | 200 | пройдена |

Итого: 21 из 21 проверок пройдены.
