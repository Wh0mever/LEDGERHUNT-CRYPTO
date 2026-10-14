# case-001: перевыгрузка, сверка фактов и эталонный прогон (запуск 20261014T114222Z, режим HTTP: replay)

## Итог

- Шаг 1, перевыгрузка: 296 запросов, ошибок 1, время 0.2 с.
- Шаг 2, сверка фактов: всего 271; подтверждено 245, расхождений 3, не проверяемо 23.
- Шаг 3, эталонный прогон без AI: маршрут из 7 адресов, переходов между сетями 3, выходов на биржу 2, запросов 40, время 0.1 с.
- Шаг 4, сравнение с ground_truth: совпадает — 12, частично — 3.
- Совпадение с сохранённым ожидаемым результатом: matches.

## Сравнение с ground_truth

| Пункт | Эталон | Эталонный прогон | Итог | Примечание |
|---|---|---|---|---|
| route (addresses in order) | ["TNakrL7VUMLNN4EEpi64HKjj5YqafR5tUx", "TYGdh7qysHLr3A4gVGivcRwSg79PpVzgNn", "TYn3YpDxmduw6fuKmFE3qkRHEoE2zeCfx3", "TUrQNNez22bPosc9NUuNvu7pxVWbziKFYU", "0x4079047990917F3150353FBd8A13b05b6286926d", … | ["TNakrL7VUMLNN4EEpi64HKjj5YqafR5tUx", "TYGdh7qysHLr3A4gVGivcRwSg79PpVzgNn", "TYn3YpDxmduw6fuKmFE3qkRHEoE2zeCfx3", "TUrQNNez22bPosc9NUuNvu7pxVWbziKFYU", "0x4079047990917F3150353FBd8A13b05b6286926d", "0xdA392553ec3602D3e650a725f847C10d04E122C0", "TYHeH2HQn7pM5… | совпадает |  |
| route: bridge labels on cross-chain hops | {"0x4079047990917F3150353FBd8A13b05b6286926d": "USDT0/LayerZero", "0xdA392553ec3602D3e650a725f847C10d04E122C0": "Rango->NEAR Intents"} | {"0x4079047990917F3150353FBd8A13b05b6286926d": "USDT0/LayerZero", "0xdA392553ec3602D3e650a725f847C10d04E122C0": "Rango", "TYHeH2HQn7pM5fe6aYwGabz9x4yizJbwp6": "Rango->NEAR Intents"} | частично | the reference run labels each address with the hop that delivered funds INTO it; the fixture may place a label on a neighbouring address |
| side branch: TDii6v... energy fees (5.137122 + 5.486343) | ["5.137122", "5.486343"] | {"5.137122": "victim-side outflow signed with the victim key in the theft window", "5.486343": "side outflow (fee-like)"} | совпадает |  |
| side branch: TRUJEt... 1% (130.356401) | ["130.356401"] | {"130.356401": "exact 1% cut"} | совпадает |  |
| side branch: Rango affiliate 0xDDdb9a... 19.352116 | ["19.352116"] | {"19.352116": "Rango affiliate fee"} | совпадает |  |
| side branch: bridge fees | bridge fees on each bridge hop | ["USDT0 (LayerZero OFT): 3.871584", "NEAR Intents 1Click: 3.603982"] | совпадает |  |
| cross-chain: USDT0 OFT TRON->Ethereum (dstEid 30101) | dstEid 30101, tron->ethereum | dstEid 30101, tron->ethereum, recipient 0x4079047990917F3150353FBd8A13b05b6286926d, LayerZero Scan DELIVERED | совпадает |  |
| cross-chain: Rango destinationChainId=1414680398 ('TRON') and ASCII receiver | 1414680398 / TRON / ASCII receiver | 1414680398 / TRON / TYHeH2HQn7pM5fe6aYwG | совпадает | the ASCII receiver holds only the first 20 characters of the TRON address; the full recipient comes from the NEAR Intents 1Click status |
| cross-chain: NEAR Intents 1Click deposit address | 0xdA392553ec3602D3e650a725f847C10d04E122C0 | 0xdA392553ec3602D3e650a725f847C10d04E122C0 -> TYHeH2HQn7pM5fe6aYwGabz9x4yizJbwp6 (dst tx d3cd82b7c1ea0a828066f5bb732dd480262e5df6f4ce02f7dfe0791ff65f74c1) | совпадает |  |
| exchange exits: WhiteBIT via deposit addresses TNJSC23... and TCiwRN... (commingled hub o… | ["TNJSC23", "TCiwRN"] | {"TNJSC23": "WhiteBIT via TWBPGLwQw2EbqYLLw1DJnTDt2ZQ9yJW1JJ (forward 201 s, tx 1258e508eff1)", "TCiwRN": "WhiteBIT via TWBPGLwQw2EbqYLLw1DJnTDt2ZQ9yJW1JJ (forward 171 s, tx 3cceeee9edb9)"} | совпадает | commingled hub outflows; exchange identity comes from the labelled hot wallet (TronScan tag, pending written consent) |
| extra: hub outflows with a deposit-like pattern to an unlabelled address | not traced in the fixture (steps 20-21: 'Not traced further') | ["TWx6Z8roV3nWTqp8FjTKZSWdWLGbcJyxxw -> TDqSquXBgUCLYvYC4XZgrprLK589dkhSCf 14760.000000 after 504 s"] | частично | new observation, not a contradiction: destination is not labelled, so no exchange is attributed |
| freeze candidate | TYHeH2HQn7pM5fe6aYwGabz9x4yizJbwp6 (USDT-TRC20, commingled) | ["TYHeH2HQn7pM5fe6aYwGabz9x4yizJbwp6 (USDT-TRC20, commingled)"] | совпадает |  |
| mechanism | Transactions signed with victim's own owner key (no permission change); key/seed compromise | signatures=1, signer=['TNakrL7VUMLNN4EEpi64HKjj5YqafR5tUx'], permission=owner, permission updates=0, owner keys=['TNakrL7VUMLNN4EEpi64HKjj5YqafR5tUx'] | совпадает |  |
| total_fees_lost_before_hub | 162.94587 | 162.945870 | совпадает | components reconcile: True |
| common TRX funder (likely same operator, with confidence) | TVNMa2ZrUWE9sdBawJoQ8aN6LPFjv9ZppZ funds ['TYn3YpDxmduw6fuKmFE3qkRHEoE2zeCfx3', 'TUrQNNez22bPosc9NUuNvu7pxVWbziKFYU', 'TYHeH2HQn7pM5fe6aYwGabz9x4yizJbwp6']; fixture confidence: high (common funder) | TVNMa2ZrUWE9sdBawJoQ8aN6LPFjv9ZppZ funds ['TYn3YpDxmduw6fuKmFE3qkRHEoE2zeCfx3', 'TUrQNNez22bPosc9NUuNvu7pxVWbziKFYU', 'TYHeH2HQn7pM5fe6aYwGabz9x4yizJbwp6']; confidence medium (score 2; funder fan-out 80 distinct TRX recipients) | частично | funder fan-out (distinct TRX recipients) lowers the score: the funder also tops up many other addresses, as a funding service would |

## Маршрут эталонного прогона

| № | Сеть | Адрес | Роль | Пришло | Время UTC | Через |
|---|---|---|---|---|---|---|
| 1 | tron | `TNakrL7VUMLNN4EEpi64HKjj5YqafR5tUx` | victim |  |  |  |
| 2 | tron | `TYGdh7qysHLr3A4gVGivcRwSg79PpVzgNn` | holder | 13041.400772 | 2026-09-21 11:32:39 |  |
| 3 | tron | `TYn3YpDxmduw6fuKmFE3qkRHEoE2zeCfx3` | holder | 13035.640112 | 2026-09-21 11:35:33 |  |
| 4 | tron | `TUrQNNez22bPosc9NUuNvu7pxVWbziKFYU` | holder | 12905.283711 | 2026-09-21 11:41:18 |  |
| 5 | ethereum | `0x4079047990917F3150353FBd8A13b05b6286926d` | holder | 12901.408416 | 2026-09-21 11:52:59 | USDT0/LayerZero |
| 6 | ethereum | `0xdA392553ec3602D3e650a725f847C10d04E122C0` | bridge deposit address | 12882.058884 | 2026-09-21 11:56:35 | Rango |
| 7 | tron | `TYHeH2HQn7pM5fe6aYwGabz9x4yizJbwp6` | hub (stop) | 12878.454902 | 2026-09-21 11:58:09 | Rango->NEAR Intents |

## Рёбра (переводы, на которые опирается прогон)

| № | Сеть | TXID | От | Кому | Сумма | Время UTC | Тип | Квитанция |
|---|---|---|---|---|---|---|---|---|
| 1 | tron | `98f3ffca9d141f2172d28f46905c08e5f32fc6ce8d23f9a37b731fe2a6c1d1bb` | `TNakrL7VUMLNN4EEpi64HKjj5YqafR5tUx` | `TYGdh7qysHLr3A4gVGivcRwSg79PpVzgNn` | 13041.400772 | 2026-09-21 11:32:39 | theft |  |
| 2 | tron | `2e2e2fb81522ef16fffca4a24735487e11029acb66aba04cef6e303570de2b94` | `TNakrL7VUMLNN4EEpi64HKjj5YqafR5tUx` | `TDii6vao7xyWg2rKPbCPWVRpSmne8xcqYx` | 5.137122 | 2026-09-21 11:32:39 | victim_side_outflow |  |
| 3 | tron | `0a195e40d736d3e789fe6c9bf8c4d6d7eb451d76247910515d59c70e4c3dacec` | `TYGdh7qysHLr3A4gVGivcRwSg79PpVzgNn` | `TDii6vao7xyWg2rKPbCPWVRpSmne8xcqYx` | 5.486343 | 2026-09-21 11:35:33 | side |  |
| 4 | tron | `36edd3fb822ecb39954bd46b41b1181b7694dd9cc9da30a020b75e70ef8fe3f6` | `TYGdh7qysHLr3A4gVGivcRwSg79PpVzgNn` | `TYn3YpDxmduw6fuKmFE3qkRHEoE2zeCfx3` | 13035.640112 | 2026-09-21 11:35:33 | hop | True |
| 5 | tron | `f2c69962f47bdaeaa64bd848adf01158341f09edefd70719a478a3c062e98cbe` | `TYn3YpDxmduw6fuKmFE3qkRHEoE2zeCfx3` | `TUrQNNez22bPosc9NUuNvu7pxVWbziKFYU` | 12905.283711 | 2026-09-21 11:41:18 | hop | True |
| 6 | tron | `1c5e7b5d4b50b14ab58965be47b624bc6a11b2719ee33718685a27bf0c1e3f76` | `TYn3YpDxmduw6fuKmFE3qkRHEoE2zeCfx3` | `TRUJEtAFzBWReAUu5L83wFRvxWtrVw3sAz` | 130.356401 | 2026-09-21 11:43:45 | exact_cut |  |
| 7 | tron | `b49b0157d5327ca4b25683d2100d77c9b0c2c13584fdc96deea17a8c93057f6f` | `TUrQNNez22bPosc9NUuNvu7pxVWbziKFYU` | `TFG4wBaDQ8sHWWP1ACeSGnoNR6RRzevLPt` | 12905.280000 | 2026-09-21 11:50:54 | bridge_out | True |
| 8 | ethereum | `0x8ea2bdef31c5eefb89569a239d5208cdff99a7bb9a7fe2f48c168b16b9d73c15` | `0x1F748c76dE468e9D11bd340fA9D5CBADf315dFB0` | `0x4079047990917F3150353FBd8A13b05b6286926d` | 12901.408416 | 2026-09-21 11:52:59 | bridge_in | True |
| 9 | tron | `1cad8478b278e63da6ea9c1f8d9824bba060fadf77aac353bfad2003cb2a4452` | `TUrQNNez22bPosc9NUuNvu7pxVWbziKFYU` | `TMU9a6ZWhxJNfZen7YRZ81cvVx2Go1xZTA` | 0.009778 | 2026-09-21 11:56:15 | remainder_dust |  |
| 10 | ethereum | `0x41bac088520409376e60709fd7114b7b3d670abeedfb01a68b7ee42a84ec515a` | `0x4079047990917F3150353FBd8A13b05b6286926d` | `0x69460570c93f9DE5E2edbC3052bf10125f0Ca22d` | 12901.411000 | 2026-09-21 11:56:35 | bridge_out | True |
| 11 | ethereum | `0x41bac088520409376e60709fd7114b7b3d670abeedfb01a68b7ee42a84ec515a` | `0x69460570c93f9DE5E2edbC3052bf10125f0Ca22d` | `0xdA392553ec3602D3e650a725f847C10d04E122C0` | 12882.058884 | 2026-09-21 11:56:35 | aggregator_forward |  |
| 12 | ethereum | `0x224f3859d03f8a26fc697b7b2978d4a701cf3db1d280dbd911e18b508b54e762` | `0xdA392553ec3602D3e650a725f847C10d04E122C0` | `0x2CfF890f0378a11913B6129B2E97417a2c302680` | 12882.058884 | 2026-09-21 11:57:35 | bridge_deposit_sweep |  |
| 13 | tron | `d3cd82b7c1ea0a828066f5bb732dd480262e5df6f4ce02f7dfe0791ff65f74c1` | `TX5XiRXdyz7sdFwF5mnhT1QoGCpbkncpke` | `TYHeH2HQn7pM5fe6aYwGabz9x4yizJbwp6` | 12878.454902 | 2026-09-21 11:58:09 | bridge_in | True |

## Боковые ветки

| Ветка | TXID | Кому | Сумма | Входит в потери |
|---|---|---|---|---|
| victim-side outflow signed with the victim key in the theft window | `2e2e2fb81522ef16fffca4a24735487e11029acb66aba04cef6e303570de2b94` | `TDii6vao7xyWg2rKPbCPWVRpSmne8xcqYx` | 5.137122 | нет |
| side outflow (fee-like) | `0a195e40d736d3e789fe6c9bf8c4d6d7eb451d76247910515d59c70e4c3dacec` | `TDii6vao7xyWg2rKPbCPWVRpSmne8xcqYx` | 5.486343 | да |
| exact 1% cut | `1c5e7b5d4b50b14ab58965be47b624bc6a11b2719ee33718685a27bf0c1e3f76` | `TRUJEtAFzBWReAUu5L83wFRvxWtrVw3sAz` | 130.356401 | да |
| bridge fee | `b49b0157d5327ca4b25683d2100d77c9b0c2c13584fdc96deea17a8c93057f6f` | `` | 3.871584 | да |
| remainder dust after the drain | `1cad8478b278e63da6ea9c1f8d9824bba060fadf77aac353bfad2003cb2a4452` | `TMU9a6ZWhxJNfZen7YRZ81cvVx2Go1xZTA` | 0.009778 | нет |
| Rango affiliate fee | `0x41bac088520409376e60709fd7114b7b3d670abeedfb01a68b7ee42a84ec515a` | `0xDDdb9a95E443A204EB8650D5EA578ed707Fe2123` | 19.352116 | да |
| bridge fee | `d3cd82b7c1ea0a828066f5bb732dd480262e5df6f4ce02f7dfe0791ff65f74c1` | `` | 3.603982 | да |

## Учёт стоимости до хаба

Украдено 13041.400772, пришло на хаб 12878.454902, потеряно 162.945870; сумма составляющих 162.945870 (сходится: True).

| Составляющая | Где | Сумма |
|---|---|---|
| side outflow (side) | tron:TYGdh7qysHLr3A4gVGivcRwSg79PpVzgNn | 5.486343 |
| left on holder (not moved in the follow window) | tron:TYGdh7qysHLr3A4gVGivcRwSg79PpVzgNn | 0.274317 |
| side outflow (exact_cut) | tron:TYn3YpDxmduw6fuKmFE3qkRHEoE2zeCfx3 | 130.356401 |
| bridge fee (USDT0/LayerZero OFT: amountSentLD - amountReceivedLD) | USDT0 (LayerZero OFT) b49b0157d5327ca4b25683d2100d77c9b0c2c13584fdc96deea17a8c93057f6f | 3.871584 |
| left on holder (not moved in the follow window) | tron:TUrQNNez22bPosc9NUuNvu7pxVWbziKFYU | 0.003711 |
| Rango side transfer (affiliate fee) | 0x41bac088520409376e60709fd7114b7b3d670abeedfb01a68b7ee42a84ec515a | 19.352116 |
| holder sent more than the tainted arrival (pre-existing balance mixed in) | ethereum:0x4079047990917F3150353FBd8A13b05b6286926d | -0.002584 |
| NEAR Intents 1Click: deposit - on-chain payout | 0xdA392553ec3602D3e650a725f847C10d04E122C0 | 3.603982 |

## Проверка выходов хаба

| Выход хаба (TXID) | Время UTC | Сумма | Получатель | Переслал | Задержка, с | Куда | Итог |
|---|---|---|---|---|---|---|---|
| `09bb9e02b1f37428d1b49a9a0a9670aba307b910b4b42298f50cd17dc07473a8` | 2026-09-21 13:41:15 | 150000.000000 | `TNJSC23oMcb5ws9tppANFTGtEDcKQgQBYQ` | 150000.000000 | 201 | TWBPGLwQw2EbqYLLw1DJnTDt2ZQ9yJW1JJ | exchange_exit (WhiteBIT) |
| `9cfd1cad95e60b5651d9ed59805772c6d67e1cd639d96b8c5f305baea5a22a96` | 2026-09-21 15:14:45 | 14760.000000 | `TWx6Z8roV3nWTqp8FjTKZSWdWLGbcJyxxw` | 14760.000000 | 504 | TDqSquXBgUCLYvYC4XZgrprLK589dkhSCf | deposit_pattern_unlabelled_destination |
| `284c7baae14411a7dac814ca4c12588244158c415e90aed3ca3707a6e78f2ca7` | 2026-09-21 15:18:42 | 21000.000000 | `TP5KYiUg6pT6LF6ar88UpCV2Q6wnFSgHdE` | 0.000000 |  |  | no_deposit_pattern |
| `9be4de8659dc02cfbd96b3812ab075594ae4d22e8493ba1b68606b01e8f959aa` | 2026-09-22 08:25:00 | 250000.000000 | `TCiwRNyeUK7JwkEgF5W3AExFpZ2ErRZG4C` | 250000.000000 | 171 | TWBPGLwQw2EbqYLLw1DJnTDt2ZQ9yJW1JJ | exchange_exit (WhiteBIT) |

## Связи

- shared_funder_with_victim: `TUSYcK5yf8Et4xNTiUcpfZwmhFsxfdoooo` → `TYGdh7qysHLr3A4gVGivcRwSg79PpVzgNn`; also funded the victim: treated as a service (activation/top-up), not as an operator link
- common_trx_funder: `TVNMa2ZrUWE9sdBawJoQ8aN6LPFjv9ZppZ` → `TYn3YpDxmduw6fuKmFE3qkRHEoE2zeCfx3`, `TUrQNNez22bPosc9NUuNvu7pxVWbziKFYU`, `TYHeH2HQn7pM5fe6aYwGabz9x4yizJbwp6`; уверенность: medium (балл 2, разных получателей TRX у спонсора: 80)

## Охват транзакций эталона

| Шаг | TXID | Вид | Как достигнут | Отличия |
|---|---|---|---|---|
| 1 | `7472e1e059d44b5fb3…` | incoming_payment | theft context (victim side) |  |
| 2 | `6be9eabf7568fe67f4…` | incoming_test_payment | not reached (not needed by the rules) |  |
| 3 | `90b28da07b6ea4eeec…` | energy_delegation | theft context (victim side) |  |
| 4 | `a241b856691236d3ed…` | trx_topup | theft context (victim side) |  |
| 5 | `2e2e2fb81522ef16ff…` | theft_fee_energy_rental | edge 2 (victim_side_outflow) |  |
| 6 | `98f3ffca9d141f2172…` | THEFT | edge 1 (theft) |  |
| 7 | `0a195e40d736d3e789…` | fee_energy_rental | edge 3 (side) |  |
| 8 | `36edd3fb822ecb3995…` | hop | edge 4 (hop) |  |
| 9 | `f2c69962f47bdaeaa6…` | hop_99pct | edge 5 (hop) |  |
| 10 | `1c5e7b5d4b50b14ab5…` | fee_1pct | edge 6 (exact_cut) |  |
| 11 | `12039abce0c3c27bf5…` | approve | not reached (not needed by the rules) |  |
| 12 | `b49b0157d5327ca4b2…` | bridge_out_USDT0_LayerZero | edge 7 (bridge_out) |  |
| 13 | `1cad8478b278e63da6…` | dust | edge 9 (remainder_dust) |  |
| 14 | `0x8ea2bdef31c5eefb…` | bridge_in_USDT0 | edge 8 (bridge_in) |  |
| 15 | `0x41bac08852040937…` | bridge_out_Rango | edge 11 (aggregator_forward) | from: fixture 0x4079047990917F3150353FBd8A13b05b6286926d vs reference 0x69460570c93f9DE5E2edbC3052bf10125f0Ca22d; to: fixture 0x69460570c93f9DE5E2edbC3052bf10125f0Ca22d vs reference 0xdA392553ec3602D… |
| 16 | `0x224f3859d03f8a26…` | near_intents_deposit | edge 12 (bridge_deposit_sweep) |  |
| 17 | `d3cd82b7c1ea0a8280…` | bridge_in_NEAR_Intents | edge 13 (bridge_in) |  |
| 18 | `09bb9e02b1f37428d1…` | hub_outflow_commingled | hub outflow check: exchange_exit |  |
| 19 | `1258e508eff11fa898…` | exchange_sweep | hub outflow check: exchange_exit |  |
| 20 | `9cfd1cad95e60b5651…` | hub_outflow_commingled | hub outflow check: deposit_pattern_unlabelled_destination | timestamp_utc: fixture 2026-09-21 13:54:45 vs reference 2026-09-21 15:14:45 |
| 21 | `284c7baae14411a7da…` | hub_outflow_commingled | hub outflow check: no_deposit_pattern | timestamp_utc: fixture 2026-09-21 13:58:42 vs reference 2026-09-21 15:18:42 |
| 22 | `9be4de8659dc02cfbd…` | hub_outflow_commingled | hub outflow check: exchange_exit |  |
| 23 | `3cceeee9edb9773581…` | exchange_sweep | hub outflow check: exchange_exit |  |

## Время и запросы эталонного прогона

| Шаг | Запросов | Из записи | Время, мс | По источникам (запросов / сумма задержек, мс / ожидание лимита, мс) |
|---|---|---|---|---|
| 1 start: theft transaction | 2 | 2 | 6.7 | trongrid: 2 / 1344.5 / 0.0 |
| 2 victim: mechanism and theft context | 5 | 5 | 32.9 | trongrid: 5 / 1137.1 / 0.0 |
| 3.1 holder tron:TYGdh7qysHLr3A4gVGivcRwSg79PpVzgNn | 2 | 2 | 2.1 | trongrid: 2 / 325.7 / 0.0 |
| 3.2 holder tron:TYn3YpDxmduw6fuKmFE3qkRHEoE2zeCfx3 | 2 | 2 | 1.8 | trongrid: 2 / 310.7 / 0.0 |
| 3.3 holder tron:TUrQNNez22bPosc9NUuNvu7pxVWbziKFYU | 7 | 7 | 4.8 | blockscout_eth: 2 / 592.8 / 0.0; eth_publicnode: 1 / 293.9 / 0.0; layerzero_scan: 1 / 670.9 / 0.0; trongrid: 3 / 453.9 / 0.0 |
| 3.4 holder ethereum:0x4079047990917F3150353FBd8A13b05b6286926d | 4 | 4 | 7.3 | blockscout_eth: 2 / 935.8 / 0.0; eth_publicnode: 1 / 128.2 / 0.0; near_intents_1click: 1 / 378.2 / 0.0 |
| 3.5 holder ethereum:0xdA392553ec3602D3e650a725f847C10d04E122C0 | 3 | 3 | 2.2 | blockscout_eth: 1 / 563.4 / 0.0; near_intents_1click: 1 / 116.2 / 0.0; trongrid: 1 / 129.3 / 0.0 |
| 3.6 holder tron:TYHeH2HQn7pM5fe6aYwGabz9x4yizJbwp6 | 1 | 1 | 0.7 | trongrid: 1 / 519.2 / 0.0 |
| 4 hub outflows: exchange exit heuristic | 7 | 7 | 3.5 | trongrid: 7 / 1436.4 / 0.0 |
| 5 common TRX funder | 6 | 6 | 11.1 | trongrid: 6 / 2896.0 / 0.0 |
| 6 freeze candidate: live balance (informational) | 1 | 1 | 1.2 | trongrid: 1 / 107.4 / 0.0 |

## Сверка фактов (все строки)

| № | Группа | Объект | Поле | Эталон | Сырые данные | Итог | Второй источник | Примечание |
|---|---|---|---|---|---|---|---|---|
| 1 | transactions | step 1 7472e1e059 | from | TBY9jt5TJJQnJNWudTm3AGPJ3e2FcevgQL | TBY9jt5TJJQnJNWudTm3AGPJ3e2FcevgQL | подтверждено | PublicNode TRON (independent java-tron node): {} - no data for this tx (node is not archival) | TronGrid node receipt log; TronGrid v1 events agree |
| 2 | transactions | step 1 7472e1e059 | to | TNakrL7VUMLNN4EEpi64HKjj5YqafR5tUx | TNakrL7VUMLNN4EEpi64HKjj5YqafR5tUx | подтверждено | PublicNode TRON (independent java-tron node): {} - no data for this tx (node is not archival) |  |
| 3 | transactions | step 1 7472e1e059 | amount | 12937.000000 | 12937.000000 | подтверждено | PublicNode TRON (independent java-tron node): {} - no data for this tx (node is not archival) |  |
| 4 | transactions | step 1 7472e1e059 | asset | USDT-TRC20 | USDT-TRC20 | подтверждено |  | token contract TR7NHqjeKQxGTCi8q8ZY4pL8otSzgjLj6t |
| 5 | transactions | step 1 7472e1e059 | timestamp_utc | 2026-09-21 11:31:54 | 2026-09-21 11:31:54 | подтверждено |  | block timestamp from gettransactioninfobyid |
| 6 | transactions | step 1 7472e1e059 | status | fact | contractRet=SUCCESS | подтверждено |  | 'fact' = the transaction exists and succeeded on chain |
| 7 | transactions | step 2 6be9eabf75 | from | TBY9jt5TJJQnJNWudTm3AGPJ3e2FcevgQL | TBY9jt5TJJQnJNWudTm3AGPJ3e2FcevgQL | подтверждено | PublicNode TRON (independent java-tron node): {} - no data for this tx (node is not archival) | TronGrid node receipt log; TronGrid v1 events agree |
| 8 | transactions | step 2 6be9eabf75 | to | TNakrL7VUMLNN4EEpi64HKjj5YqafR5tUx | TNakrL7VUMLNN4EEpi64HKjj5YqafR5tUx | подтверждено | PublicNode TRON (independent java-tron node): {} - no data for this tx (node is not archival) |  |
| 9 | transactions | step 2 6be9eabf75 | amount | 20.000000 | 20.000000 | подтверждено | PublicNode TRON (independent java-tron node): {} - no data for this tx (node is not archival) |  |
| 10 | transactions | step 2 6be9eabf75 | asset | USDT-TRC20 | USDT-TRC20 | подтверждено |  | token contract TR7NHqjeKQxGTCi8q8ZY4pL8otSzgjLj6t |
| 11 | transactions | step 2 6be9eabf75 | timestamp_utc | 2026-09-21 10:48:33 | 2026-09-21 10:48:33 | подтверждено |  | block timestamp from gettransactioninfobyid |
| 12 | transactions | step 2 6be9eabf75 | status | fact | contractRet=SUCCESS | подтверждено |  | 'fact' = the transaction exists and succeeded on chain |
| 13 | transactions | step 3 90b28da07b | kind | energy_delegation (DelegateResourceContract) | energy_delegation (DelegateResourceContract) | подтверждено |  |  |
| 14 | transactions | step 3 90b28da07b | from | TQvhNtVLyJy3PfuZQieRd5PSeH8mEpgva1 | TQvhNtVLyJy3PfuZQieRd5PSeH8mEpgva1 | подтверждено |  |  |
| 15 | transactions | step 3 90b28da07b | to | TNakrL7VUMLNN4EEpi64HKjj5YqafR5tUx | TNakrL7VUMLNN4EEpi64HKjj5YqafR5tUx | подтверждено |  |  |
| 16 | transactions | step 3 90b28da07b | amount (TRX staked behind the delegated energy) | 20424 | 20424.000000 | подтверждено |  | resource=ENERGY |
| 17 | transactions | step 3 90b28da07b | timestamp_utc | 2026-09-21 11:32:36 | 2026-09-21 11:32:36 | подтверждено |  | block timestamp from gettransactioninfobyid |
| 18 | transactions | step 3 90b28da07b | status | fact | contractRet=SUCCESS | подтверждено |  | 'fact' = the transaction exists and succeeded on chain |
| 19 | transactions | step 4 a241b85669 | kind | TRX transfer (TransferContract) | TRX transfer (TransferContract) | подтверждено |  |  |
| 20 | transactions | step 4 a241b85669 | from | TUSYcK5yf8Et4xNTiUcpfZwmhFsxfdoooo | TUSYcK5yf8Et4xNTiUcpfZwmhFsxfdoooo | подтверждено |  |  |
| 21 | transactions | step 4 a241b85669 | to | TNakrL7VUMLNN4EEpi64HKjj5YqafR5tUx | TNakrL7VUMLNN4EEpi64HKjj5YqafR5tUx | подтверждено |  |  |
| 22 | transactions | step 4 a241b85669 | amount (TRX) | 0.8 | 0.800000 | подтверждено |  |  |
| 23 | transactions | step 4 a241b85669 | timestamp_utc | 2026-09-21 11:32:39 | 2026-09-21 11:32:39 | подтверждено |  | block timestamp from gettransactioninfobyid |
| 24 | transactions | step 4 a241b85669 | status | fact | contractRet=SUCCESS | подтверждено |  | 'fact' = the transaction exists and succeeded on chain |
| 25 | transactions | step 5 2e2e2fb815 | from | TNakrL7VUMLNN4EEpi64HKjj5YqafR5tUx | TNakrL7VUMLNN4EEpi64HKjj5YqafR5tUx | подтверждено | PublicNode TRON (independent java-tron node): {} - no data for this tx (node is not archival) | TronGrid node receipt log; TronGrid v1 events agree |
| 26 | transactions | step 5 2e2e2fb815 | to | TDii6vao7xyWg2rKPbCPWVRpSmne8xcqYx | TDii6vao7xyWg2rKPbCPWVRpSmne8xcqYx | подтверждено | PublicNode TRON (independent java-tron node): {} - no data for this tx (node is not archival) |  |
| 27 | transactions | step 5 2e2e2fb815 | amount | 5.137122 | 5.137122 | подтверждено | PublicNode TRON (independent java-tron node): {} - no data for this tx (node is not archival) |  |
| 28 | transactions | step 5 2e2e2fb815 | asset | USDT-TRC20 | USDT-TRC20 | подтверждено |  | token contract TR7NHqjeKQxGTCi8q8ZY4pL8otSzgjLj6t |
| 29 | transactions | step 5 2e2e2fb815 | timestamp_utc | 2026-09-21 11:32:39 | 2026-09-21 11:32:39 | подтверждено |  | block timestamp from gettransactioninfobyid |
| 30 | transactions | step 5 2e2e2fb815 | status | fact | contractRet=SUCCESS | подтверждено |  | 'fact' = the transaction exists and succeeded on chain |
| 31 | transactions | step 5 2e2e2fb815 | signed by (recovered from signature) | ["TNakrL7VUMLNN4EEpi64HKjj5YqafR5tUx"] | ["TNakrL7VUMLNN4EEpi64HKjj5YqafR5tUx"] | подтверждено |  | signatures=1, Permission_id=absent (0 = owner), txID==sha256(raw_data): True |
| 32 | transactions | step 6 98f3ffca9d | from | TNakrL7VUMLNN4EEpi64HKjj5YqafR5tUx | TNakrL7VUMLNN4EEpi64HKjj5YqafR5tUx | подтверждено | PublicNode TRON (independent java-tron node): {} - no data for this tx (node is not archival) | TronGrid node receipt log; TronGrid v1 events agree |
| 33 | transactions | step 6 98f3ffca9d | to | TYGdh7qysHLr3A4gVGivcRwSg79PpVzgNn | TYGdh7qysHLr3A4gVGivcRwSg79PpVzgNn | подтверждено | PublicNode TRON (independent java-tron node): {} - no data for this tx (node is not archival) |  |
| 34 | transactions | step 6 98f3ffca9d | amount | 13041.400772 | 13041.400772 | подтверждено | PublicNode TRON (independent java-tron node): {} - no data for this tx (node is not archival) |  |
| 35 | transactions | step 6 98f3ffca9d | asset | USDT-TRC20 | USDT-TRC20 | подтверждено |  | token contract TR7NHqjeKQxGTCi8q8ZY4pL8otSzgjLj6t |
| 36 | transactions | step 6 98f3ffca9d | timestamp_utc | 2026-09-21 11:32:39 | 2026-09-21 11:32:39 | подтверждено |  | block timestamp from gettransactioninfobyid |
| 37 | transactions | step 6 98f3ffca9d | block | 86439360 | 86439360 | подтверждено |  |  |
| 38 | transactions | step 6 98f3ffca9d | status | fact | contractRet=SUCCESS | подтверждено |  | 'fact' = the transaction exists and succeeded on chain |
| 39 | transactions | step 6 98f3ffca9d | signed by (recovered from signature) | ["TNakrL7VUMLNN4EEpi64HKjj5YqafR5tUx"] | ["TNakrL7VUMLNN4EEpi64HKjj5YqafR5tUx"] | подтверждено |  | signatures=1, Permission_id=absent (0 = owner), txID==sha256(raw_data): True |
| 40 | transactions | step 7 0a195e40d7 | from | TYGdh7qysHLr3A4gVGivcRwSg79PpVzgNn | TYGdh7qysHLr3A4gVGivcRwSg79PpVzgNn | подтверждено | PublicNode TRON (independent java-tron node): {} - no data for this tx (node is not archival) | TronGrid node receipt log; TronGrid v1 events agree |
| 41 | transactions | step 7 0a195e40d7 | to | TDii6vao7xyWg2rKPbCPWVRpSmne8xcqYx | TDii6vao7xyWg2rKPbCPWVRpSmne8xcqYx | подтверждено | PublicNode TRON (independent java-tron node): {} - no data for this tx (node is not archival) |  |
| 42 | transactions | step 7 0a195e40d7 | amount | 5.486343 | 5.486343 | подтверждено | PublicNode TRON (independent java-tron node): {} - no data for this tx (node is not archival) |  |
| 43 | transactions | step 7 0a195e40d7 | asset | USDT-TRC20 | USDT-TRC20 | подтверждено |  | token contract TR7NHqjeKQxGTCi8q8ZY4pL8otSzgjLj6t |
| 44 | transactions | step 7 0a195e40d7 | timestamp_utc | 2026-09-21 11:35:33 | 2026-09-21 11:35:33 | подтверждено |  | block timestamp from gettransactioninfobyid |
| 45 | transactions | step 7 0a195e40d7 | status | fact | contractRet=SUCCESS | подтверждено |  | 'fact' = the transaction exists and succeeded on chain |
| 46 | transactions | step 8 36edd3fb82 | from | TYGdh7qysHLr3A4gVGivcRwSg79PpVzgNn | TYGdh7qysHLr3A4gVGivcRwSg79PpVzgNn | подтверждено | PublicNode TRON (independent java-tron node): {} - no data for this tx (node is not archival) | TronGrid node receipt log; TronGrid v1 events agree |
| 47 | transactions | step 8 36edd3fb82 | to | TYn3YpDxmduw6fuKmFE3qkRHEoE2zeCfx3 | TYn3YpDxmduw6fuKmFE3qkRHEoE2zeCfx3 | подтверждено | PublicNode TRON (independent java-tron node): {} - no data for this tx (node is not archival) |  |
| 48 | transactions | step 8 36edd3fb82 | amount | 13035.640112 | 13035.640112 | подтверждено | PublicNode TRON (independent java-tron node): {} - no data for this tx (node is not archival) |  |
| 49 | transactions | step 8 36edd3fb82 | asset | USDT-TRC20 | USDT-TRC20 | подтверждено |  | token contract TR7NHqjeKQxGTCi8q8ZY4pL8otSzgjLj6t |
| 50 | transactions | step 8 36edd3fb82 | timestamp_utc | 2026-09-21 11:35:33 | 2026-09-21 11:35:33 | подтверждено |  | block timestamp from gettransactioninfobyid |
| 51 | transactions | step 8 36edd3fb82 | status | fact | contractRet=SUCCESS | подтверждено |  | 'fact' = the transaction exists and succeeded on chain |
| 52 | transactions | step 9 f2c69962f4 | from | TYn3YpDxmduw6fuKmFE3qkRHEoE2zeCfx3 | TYn3YpDxmduw6fuKmFE3qkRHEoE2zeCfx3 | подтверждено | PublicNode TRON (independent java-tron node): {} - no data for this tx (node is not archival) | TronGrid node receipt log; TronGrid v1 events agree |
| 53 | transactions | step 9 f2c69962f4 | to | TUrQNNez22bPosc9NUuNvu7pxVWbziKFYU | TUrQNNez22bPosc9NUuNvu7pxVWbziKFYU | подтверждено | PublicNode TRON (independent java-tron node): {} - no data for this tx (node is not archival) |  |
| 54 | transactions | step 9 f2c69962f4 | amount | 12905.283711 | 12905.283711 | подтверждено | PublicNode TRON (independent java-tron node): {} - no data for this tx (node is not archival) |  |
| 55 | transactions | step 9 f2c69962f4 | asset | USDT-TRC20 | USDT-TRC20 | подтверждено |  | token contract TR7NHqjeKQxGTCi8q8ZY4pL8otSzgjLj6t |
| 56 | transactions | step 9 f2c69962f4 | timestamp_utc | 2026-09-21 11:41:18 | 2026-09-21 11:41:18 | подтверждено |  | block timestamp from gettransactioninfobyid |
| 57 | transactions | step 9 f2c69962f4 | status | fact | contractRet=SUCCESS | подтверждено |  | 'fact' = the transaction exists and succeeded on chain |
| 58 | transactions | step 9 f2c69962f4 | hop = parent - 1% cut | 12905.283711 | 12905.283711 | подтверждено |  | share of parent = 99.00000000% |
| 59 | transactions | step 10 1c5e7b5d4b | from | TYn3YpDxmduw6fuKmFE3qkRHEoE2zeCfx3 | TYn3YpDxmduw6fuKmFE3qkRHEoE2zeCfx3 | подтверждено | PublicNode TRON (independent java-tron node): {} - no data for this tx (node is not archival) | TronGrid node receipt log; TronGrid v1 events agree |
| 60 | transactions | step 10 1c5e7b5d4b | to | TRUJEtAFzBWReAUu5L83wFRvxWtrVw3sAz | TRUJEtAFzBWReAUu5L83wFRvxWtrVw3sAz | подтверждено | PublicNode TRON (independent java-tron node): {} - no data for this tx (node is not archival) |  |
| 61 | transactions | step 10 1c5e7b5d4b | amount | 130.356401 | 130.356401 | подтверждено | PublicNode TRON (independent java-tron node): {} - no data for this tx (node is not archival) |  |
| 62 | transactions | step 10 1c5e7b5d4b | asset | USDT-TRC20 | USDT-TRC20 | подтверждено |  | token contract TR7NHqjeKQxGTCi8q8ZY4pL8otSzgjLj6t |
| 63 | transactions | step 10 1c5e7b5d4b | timestamp_utc | 2026-09-21 11:43:45 | 2026-09-21 11:43:45 | подтверждено |  | block timestamp from gettransactioninfobyid |
| 64 | transactions | step 10 1c5e7b5d4b | status | fact | contractRet=SUCCESS | подтверждено |  | 'fact' = the transaction exists and succeeded on chain |
| 65 | transactions | step 10 1c5e7b5d4b | exactly 1% of 13035.640112 (truncated to 6 decimals) | 130.356401 | 130.356401 | подтверждено |  | 1% of 13035.640112 = 130.35640112 |
| 66 | transactions | step 11 12039abce0 | from (owner) | TUrQNNez22bPosc9NUuNvu7pxVWbziKFYU | TUrQNNez22bPosc9NUuNvu7pxVWbziKFYU | подтверждено |  |  |
| 67 | transactions | step 11 12039abce0 | to (spender) | TFG4wBaDQ8sHWWP1ACeSGnoNR6RRzevLPt | TFG4wBaDQ8sHWWP1ACeSGnoNR6RRzevLPt | подтверждено |  |  |
| 68 | transactions | step 11 12039abce0 | amount (allowance) | 12905.280000 | 12905.280000 | подтверждено |  |  |
| 69 | transactions | step 11 12039abce0 | kind | approve | approve | подтверждено |  | calldata selector 095ea7b3 = approve(address,uint256); Approval event present |
| 70 | transactions | step 11 12039abce0 | timestamp_utc | 2026-09-21 11:50:54 | 2026-09-21 11:50:54 | подтверждено |  | block timestamp from gettransactioninfobyid |
| 71 | transactions | step 11 12039abce0 | status | fact | contractRet=SUCCESS | подтверждено |  | 'fact' = the transaction exists and succeeded on chain |
| 72 | transactions | step 12 b49b0157d5 | from | TUrQNNez22bPosc9NUuNvu7pxVWbziKFYU | TUrQNNez22bPosc9NUuNvu7pxVWbziKFYU | подтверждено | PublicNode TRON (independent java-tron node): {} - no data for this tx (node is not archival) | TronGrid node receipt log; TronGrid v1 events agree |
| 73 | transactions | step 12 b49b0157d5 | to | TFG4wBaDQ8sHWWP1ACeSGnoNR6RRzevLPt | TFG4wBaDQ8sHWWP1ACeSGnoNR6RRzevLPt | подтверждено | PublicNode TRON (independent java-tron node): {} - no data for this tx (node is not archival) |  |
| 74 | transactions | step 12 b49b0157d5 | amount | 12905.280000 | 12905.280000 | подтверждено | PublicNode TRON (independent java-tron node): {} - no data for this tx (node is not archival) |  |
| 75 | transactions | step 12 b49b0157d5 | asset | USDT-TRC20 | USDT-TRC20 | подтверждено |  | token contract TR7NHqjeKQxGTCi8q8ZY4pL8otSzgjLj6t |
| 76 | transactions | step 12 b49b0157d5 | timestamp_utc | 2026-09-21 11:50:54 | 2026-09-21 11:50:54 | подтверждено |  | block timestamp from gettransactioninfobyid |
| 77 | transactions | step 12 b49b0157d5 | block | 86439725 | 86439725 | подтверждено |  |  |
| 78 | transactions | step 12 b49b0157d5 | status | fact | contractRet=SUCCESS | подтверждено |  | 'fact' = the transaction exists and succeeded on chain |
| 79 | transactions | step 12 b49b0157d5 | kind (bridge event present) | OFTSent | OFTSent | подтверждено |  | raw TRON log topic0 = keccak(OFTSent(bytes32,uint32,address,uint256,uint256)) |
| 80 | layerzero | step 12 b49b0157d5 | guid | 0xba20537a6870e4ba2538d40ae16772f198f02d88d24c47d016b53863a7337bf8 | 0xba20537a6870e4ba2538d40ae16772f198f02d88d24c47d016b53863a7337bf8 | подтверждено | LayerZero Scan (independent indexer): agrees |  |
| 81 | layerzero | step 12 b49b0157d5 | srcEid | 30420 | 30420 | подтверждено |  | from LayerZero Scan pathway |
| 82 | layerzero | step 12 b49b0157d5 | dstEid | 30101 | 30101 | подтверждено | LayerZero Scan (independent indexer): dstEid 30101 |  |
| 83 | layerzero | step 12 b49b0157d5 | dst_chain | ethereum | ethereum | подтверждено |  |  |
| 84 | layerzero | step 12 b49b0157d5 | sendTo | 0x4079047990917f3150353fbd8a13b05b6286926d | 0x4079047990917f3150353fbd8a13b05b6286926d | подтверждено | Ethereum OFTReceived.toAddress: 0x4079047990917F3150353FBd8A13b05b6286926d | decoded from OFT send() calldata (SendParam.to) |
| 85 | layerzero | step 12 b49b0157d5 | amountReceivedLD | 12901.408416 | 12901.408416 | подтверждено | Ethereum OFTReceived.amountReceivedLD: 12901.408416 |  |
| 86 | layerzero | step 12 b49b0157d5 | status | DELIVERED | DELIVERED | подтверждено |  | by guid: DELIVERED |
| 87 | layerzero | step 12 b49b0157d5 | destination tx (fixture step 14) | 0x8ea2bdef31c5eefb89569a239d5208cdff99a7bb9a7fe2f48c168b16b9d73c15 | 0x8ea2bdef31c5eefb89569a239d5208cdff99a7bb9a7fe2f48c168b16b9d73c15 | подтверждено |  |  |
| 88 | transactions | step 13 1cad8478b2 | from | TUrQNNez22bPosc9NUuNvu7pxVWbziKFYU | TUrQNNez22bPosc9NUuNvu7pxVWbziKFYU | подтверждено | PublicNode TRON (independent java-tron node): {} - no data for this tx (node is not archival) | TronGrid node receipt log; TronGrid v1 events agree |
| 89 | transactions | step 13 1cad8478b2 | to | TMU9a6ZWhxJNfZen7YRZ81cvVx2Go1xZTA | TMU9a6ZWhxJNfZen7YRZ81cvVx2Go1xZTA | подтверждено | PublicNode TRON (independent java-tron node): {} - no data for this tx (node is not archival) |  |
| 90 | transactions | step 13 1cad8478b2 | amount | 0.009778 | 0.009778 | подтверждено | PublicNode TRON (independent java-tron node): {} - no data for this tx (node is not archival) |  |
| 91 | transactions | step 13 1cad8478b2 | asset | USDT-TRC20 | USDT-TRC20 | подтверждено |  | token contract TR7NHqjeKQxGTCi8q8ZY4pL8otSzgjLj6t |
| 92 | transactions | step 13 1cad8478b2 | timestamp_utc | 2026-09-21 11:56:15 | 2026-09-21 11:56:15 | подтверждено |  | block timestamp from gettransactioninfobyid |
| 93 | transactions | step 13 1cad8478b2 | status | fact | contractRet=SUCCESS | подтверждено |  | 'fact' = the transaction exists and succeeded on chain |
| 94 | transactions | step 14 0x8ea2bdef31 | from | 0x1f748c76de468e9d11bd340fa9d5cbadf315dfb0 | 0x1f748c76de468e9d11bd340fa9d5cbadf315dfb0 | подтверждено | public Ethereum RPC receipt: agrees |  |
| 95 | transactions | step 14 0x8ea2bdef31 | to | 0x4079047990917f3150353fbd8a13b05b6286926d | 0x4079047990917f3150353fbd8a13b05b6286926d | подтверждено |  |  |
| 96 | transactions | step 14 0x8ea2bdef31 | amount | 12901.408416 | 12901.408416 | подтверждено | public Ethereum RPC receipt: agrees |  |
| 97 | transactions | step 14 0x8ea2bdef31 | asset | USDT-ERC20 | USDT-ERC20 | подтверждено |  |  |
| 98 | transactions | step 14 0x8ea2bdef31 | timestamp_utc | 2026-09-21 11:52:59 | 2026-09-21 11:52:59 | подтверждено |  |  |
| 99 | transactions | step 14 0x8ea2bdef31 | block | 26025709 | 26025709 | подтверждено | receipt blockNumber 26025709 |  |
| 100 | transactions | step 14 0x8ea2bdef31 | status | fact | blockscout status=ok | подтверждено |  |  |
| 101 | transactions | step 15 0x41bac08852 | from | 0x4079047990917f3150353fbd8a13b05b6286926d | 0x4079047990917f3150353fbd8a13b05b6286926d | подтверждено | public Ethereum RPC receipt: agrees |  |
| 102 | transactions | step 15 0x41bac08852 | to | 0x69460570c93f9de5e2edbc3052bf10125f0ca22d | 0x69460570c93f9de5e2edbc3052bf10125f0ca22d | подтверждено |  |  |
| 103 | transactions | step 15 0x41bac08852 | amount | 12901.411000 | 12901.411000 | подтверждено | public Ethereum RPC receipt: agrees |  |
| 104 | transactions | step 15 0x41bac08852 | asset | USDT-ERC20 | USDT-ERC20 | подтверждено |  |  |
| 105 | transactions | step 15 0x41bac08852 | timestamp_utc | 2026-09-21 11:56:35 | 2026-09-21 11:56:35 | подтверждено |  |  |
| 106 | transactions | step 15 0x41bac08852 | block | 26025727 | 26025727 | подтверждено | receipt blockNumber 26025727 |  |
| 107 | transactions | step 15 0x41bac08852 | status | fact | blockscout status=ok | подтверждено |  |  |
| 108 | rango | step 15 0x41bac08852 | dAppName | MoonGate | MoonGate | подтверждено |  |  |
| 109 | rango | step 15 0x41bac08852 | dAppTag | 1662 | 1662 | подтверждено |  |  |
| 110 | rango | step 15 0x41bac08852 | bridgeId | 60 | 60 | подтверждено |  |  |
| 111 | rango | step 15 0x41bac08852 | destinationChainId | 1414680398 | 1414680398 | подтверждено |  |  |
| 112 | rango | step 15 0x41bac08852 | destinationChainId_ascii | TRON | TRON | подтверждено |  |  |
| 113 | rango | step 15 0x41bac08852 | receiver_bytes_ascii | TYHeH2HQn7pM5fe6aYwG | TYHeH2HQn7pM5fe6aYwG | подтверждено |  | 20 'address' bytes of RangoBridgeInitiated.receiver read as ASCII: only the first 20 characters of the TRON address fit |
| 114 | rango | step 15 0x41bac08852 | affiliate | 0xdddb9a95e443a204eb8650d5ea578ed707fe2123 | 0xdddb9a95e443a204eb8650d5ea578ed707fe2123 | подтверждено |  |  |
| 115 | rango | step 15 0x41bac08852 | affiliateFee | 19.352116 | 19.352116 | подтверждено | USDT Transfer Diamond->affiliate: 19.352116 |  |
| 116 | rango | step 15 0x41bac08852 | forwarded_to | 0xda392553ec3602d3e650a725f847c10d04e122c0 | 0xda392553ec3602d3e650a725f847c10d04e122c0 | подтверждено |  |  |
| 117 | rango | step 15 0x41bac08852 | forwarded_amount | 12882.058884 | 12882.058884 | подтверждено |  |  |
| 118 | rango | step 15 0x41bac08852 | second source: RangoBridgeInitiated in public RPC receipt (bridgeAmount) | 12882.058884 | 12882.058884 | подтверждено |  |  |
| 119 | transactions | step 16 0x224f3859d0 | from | 0xda392553ec3602d3e650a725f847c10d04e122c0 | 0xda392553ec3602d3e650a725f847c10d04e122c0 | подтверждено | public Ethereum RPC receipt: agrees |  |
| 120 | transactions | step 16 0x224f3859d0 | to | 0x2cff890f0378a11913b6129b2e97417a2c302680 | 0x2cff890f0378a11913b6129b2e97417a2c302680 | подтверждено |  |  |
| 121 | transactions | step 16 0x224f3859d0 | amount | 12882.058884 | 12882.058884 | подтверждено | public Ethereum RPC receipt: agrees |  |
| 122 | transactions | step 16 0x224f3859d0 | asset | USDT-ERC20 | USDT-ERC20 | подтверждено |  |  |
| 123 | transactions | step 16 0x224f3859d0 | timestamp_utc | 2026-09-21 11:57:35 | 2026-09-21 11:57:35 | подтверждено |  |  |
| 124 | transactions | step 16 0x224f3859d0 | status | fact | blockscout status=ok | подтверждено |  |  |
| 125 | near_intents | step 16 0x224f3859d0 | status | SUCCESS | SUCCESS | подтверждено |  |  |
| 126 | near_intents | step 16 0x224f3859d0 | recipient_tron | TYHeH2HQn7pM5fe6aYwGabz9x4yizJbwp6 | TYHeH2HQn7pM5fe6aYwGabz9x4yizJbwp6 | подтверждено |  |  |
| 127 | near_intents | step 16 0x224f3859d0 | refundTo | 0x4079047990917f3150353fbd8a13b05b6286926d | 0x4079047990917f3150353fbd8a13b05b6286926d | подтверждено |  |  |
| 128 | near_intents | step 16 0x224f3859d0 | intentHash | ["HFxzg5Cz5BCP2ocKGbcSRbh9Skt4fr5QbbqirPL7rHqq"] | ["HFxzg5Cz5BCP2ocKGbcSRbh9Skt4fr5QbbqirPL7rHqq"] | подтверждено |  |  |
| 129 | near_intents | step 16 0x224f3859d0 | near_tx | ["HgECtUbDx8sahjUaDXRe4Q2vb2bgGm8c9HAHv8rMJmZR", "AjeZCFUWRHddcCDsaERWaPB9RDFsAFxnKmC2zARaWtAw"] | ["HgECtUbDx8sahjUaDXRe4Q2vb2bgGm8c9HAHv8rMJmZR", "AjeZCFUWRHddcCDsaERWaPB9RDFsAFxnKmC2zARaWtAw"] | подтверждено |  |  |
| 130 | near_intents | step 16 0x224f3859d0 | destination_tx | ["d3cd82b7c1ea0a828066f5bb732dd480262e5df6f4ce02f7dfe0791ff65f74c1"] | ["d3cd82b7c1ea0a828066f5bb732dd480262e5df6f4ce02f7dfe0791ff65f74c1"] | подтверждено |  |  |
| 131 | near_intents | step 16 0x224f3859d0 | deposit address (quote.depositAddress) | 0xda392553ec3602d3e650a725f847c10d04e122c0 | 0xda392553ec3602d3e650a725f847c10d04e122c0 | подтверждено |  |  |
| 132 | transactions | step 17 d3cd82b7c1 | from | TX5XiRXdyz7sdFwF5mnhT1QoGCpbkncpke | TX5XiRXdyz7sdFwF5mnhT1QoGCpbkncpke | подтверждено | PublicNode TRON (independent java-tron node): {} - no data for this tx (node is not archival) | TronGrid node receipt log; TronGrid v1 events agree |
| 133 | transactions | step 17 d3cd82b7c1 | to | TYHeH2HQn7pM5fe6aYwGabz9x4yizJbwp6 | TYHeH2HQn7pM5fe6aYwGabz9x4yizJbwp6 | подтверждено | PublicNode TRON (independent java-tron node): {} - no data for this tx (node is not archival) |  |
| 134 | transactions | step 17 d3cd82b7c1 | amount | 12878.454902 | 12878.454902 | подтверждено | PublicNode TRON (independent java-tron node): {} - no data for this tx (node is not archival) |  |
| 135 | transactions | step 17 d3cd82b7c1 | asset | USDT-TRC20 | USDT-TRC20 | подтверждено |  | token contract TR7NHqjeKQxGTCi8q8ZY4pL8otSzgjLj6t |
| 136 | transactions | step 17 d3cd82b7c1 | timestamp_utc | 2026-09-21 11:58:09 | 2026-09-21 11:58:09 | подтверждено |  | block timestamp from gettransactioninfobyid |
| 137 | transactions | step 17 d3cd82b7c1 | block | 86439870 | 86439870 | подтверждено |  |  |
| 138 | transactions | step 17 d3cd82b7c1 | status | fact | contractRet=SUCCESS | подтверждено |  | 'fact' = the transaction exists and succeeded on chain |
| 139 | transactions | step 17 d3cd82b7c1 | listed by NEAR Intents 1Click as destination tx | True | True | подтверждено | NEAR Intents 1Click status API (independent of TronGrid) |  |
| 140 | transactions | step 17 d3cd82b7c1 | note: 1Click amountOut vs on-chain transfer | 1Click amountOut 12878.410167; on-chain 12878.454902 | 1Click amountOut 12878.410167; on-chain 12878.454902 | подтверждено |  | difference on-chain - amountOut = 0.044735 |
| 141 | transactions | step 18 09bb9e02b1 | from | TYHeH2HQn7pM5fe6aYwGabz9x4yizJbwp6 | TYHeH2HQn7pM5fe6aYwGabz9x4yizJbwp6 | подтверждено | PublicNode TRON (independent java-tron node): {} - no data for this tx (node is not archival) | TronGrid node receipt log; TronGrid v1 events agree |
| 142 | transactions | step 18 09bb9e02b1 | to | TNJSC23oMcb5ws9tppANFTGtEDcKQgQBYQ | TNJSC23oMcb5ws9tppANFTGtEDcKQgQBYQ | подтверждено | PublicNode TRON (independent java-tron node): {} - no data for this tx (node is not archival) |  |
| 143 | transactions | step 18 09bb9e02b1 | amount | 150000.000000 | 150000.000000 | подтверждено | PublicNode TRON (independent java-tron node): {} - no data for this tx (node is not archival) |  |
| 144 | transactions | step 18 09bb9e02b1 | asset | USDT-TRC20 | USDT-TRC20 | подтверждено |  | token contract TR7NHqjeKQxGTCi8q8ZY4pL8otSzgjLj6t |
| 145 | transactions | step 18 09bb9e02b1 | timestamp_utc | 2026-09-21 13:41:15 | 2026-09-21 13:41:15 | подтверждено |  | block timestamp from gettransactioninfobyid |
| 146 | transactions | step 18 09bb9e02b1 | block | 86441930 | 86441930 | подтверждено |  |  |
| 147 | transactions | step 18 09bb9e02b1 | status | fact (taint share = hypothesis) | contractRet=SUCCESS | подтверждено |  | 'fact' = the transaction exists and succeeded on chain |
| 148 | transactions | step 19 1258e508ef | from | TNJSC23oMcb5ws9tppANFTGtEDcKQgQBYQ | TNJSC23oMcb5ws9tppANFTGtEDcKQgQBYQ | подтверждено | PublicNode TRON (independent java-tron node): {} - no data for this tx (node is not archival) | TronGrid node receipt log; TronGrid v1 events agree |
| 149 | transactions | step 19 1258e508ef | to | TWBPGLwQw2EbqYLLw1DJnTDt2ZQ9yJW1JJ | TWBPGLwQw2EbqYLLw1DJnTDt2ZQ9yJW1JJ | подтверждено | PublicNode TRON (independent java-tron node): {} - no data for this tx (node is not archival) |  |
| 150 | transactions | step 19 1258e508ef | amount | 150000.000000 | 150000.000000 | подтверждено | PublicNode TRON (independent java-tron node): {} - no data for this tx (node is not archival) |  |
| 151 | transactions | step 19 1258e508ef | asset | USDT-TRC20 | USDT-TRC20 | подтверждено |  | token contract TR7NHqjeKQxGTCi8q8ZY4pL8otSzgjLj6t |
| 152 | transactions | step 19 1258e508ef | timestamp_utc | 2026-09-21 13:44:36 | 2026-09-21 13:44:36 | подтверждено |  | block timestamp from gettransactioninfobyid |
| 153 | transactions | step 19 1258e508ef | status | fact | contractRet=SUCCESS | подтверждено |  | 'fact' = the transaction exists and succeeded on chain |
| 154 | addresses | step 19 1258e508ef | TronScan tag 'WhiteBIT' | WhiteBIT | HTTP 401 (TronScan API requires an API key; keyless lookup refused) | не проверяемо |  | TronScan, pending written consent, not stored in any label store; one lookup, development verification only |
| 155 | transactions | step 20 9cfd1cad95 | from | TYHeH2HQn7pM5fe6aYwGabz9x4yizJbwp6 | TYHeH2HQn7pM5fe6aYwGabz9x4yizJbwp6 | подтверждено | PublicNode TRON (independent java-tron node): {} - no data for this tx (node is not archival) | TronGrid node receipt log; TronGrid v1 events agree |
| 156 | transactions | step 20 9cfd1cad95 | to | TWx6Z8roV3nWTqp8FjTKZSWdWLGbcJyxxw | TWx6Z8roV3nWTqp8FjTKZSWdWLGbcJyxxw | подтверждено | PublicNode TRON (independent java-tron node): {} - no data for this tx (node is not archival) |  |
| 157 | transactions | step 20 9cfd1cad95 | amount | 14760.000000 | 14760.000000 | подтверждено | PublicNode TRON (independent java-tron node): {} - no data for this tx (node is not archival) |  |
| 158 | transactions | step 20 9cfd1cad95 | asset | USDT-TRC20 | USDT-TRC20 | подтверждено |  | token contract TR7NHqjeKQxGTCi8q8ZY4pL8otSzgjLj6t |
| 159 | transactions | step 20 9cfd1cad95 | timestamp_utc | 2026-09-21 13:54:45 | 2026-09-21 15:14:45 | РАСХОЖДЕНИЕ |  | block timestamp from gettransactioninfobyid |
| 160 | transactions | step 20 9cfd1cad95 | status | fact (not traced) | contractRet=SUCCESS | подтверждено |  | 'fact' = the transaction exists and succeeded on chain |
| 161 | transactions | step 21 284c7baae1 | from | TYHeH2HQn7pM5fe6aYwGabz9x4yizJbwp6 | TYHeH2HQn7pM5fe6aYwGabz9x4yizJbwp6 | подтверждено | PublicNode TRON (independent java-tron node): {} - no data for this tx (node is not archival) | TronGrid node receipt log; TronGrid v1 events agree |
| 162 | transactions | step 21 284c7baae1 | to | TP5KYiUg6pT6LF6ar88UpCV2Q6wnFSgHdE | TP5KYiUg6pT6LF6ar88UpCV2Q6wnFSgHdE | подтверждено | PublicNode TRON (independent java-tron node): {} - no data for this tx (node is not archival) |  |
| 163 | transactions | step 21 284c7baae1 | amount | 21000.000000 | 21000.000000 | подтверждено | PublicNode TRON (independent java-tron node): {} - no data for this tx (node is not archival) |  |
| 164 | transactions | step 21 284c7baae1 | asset | USDT-TRC20 | USDT-TRC20 | подтверждено |  | token contract TR7NHqjeKQxGTCi8q8ZY4pL8otSzgjLj6t |
| 165 | transactions | step 21 284c7baae1 | timestamp_utc | 2026-09-21 13:58:42 | 2026-09-21 15:18:42 | РАСХОЖДЕНИЕ |  | block timestamp from gettransactioninfobyid |
| 166 | transactions | step 21 284c7baae1 | status | fact (not traced) | contractRet=SUCCESS | подтверждено |  | 'fact' = the transaction exists and succeeded on chain |
| 167 | transactions | step 22 9be4de8659 | from | TYHeH2HQn7pM5fe6aYwGabz9x4yizJbwp6 | TYHeH2HQn7pM5fe6aYwGabz9x4yizJbwp6 | подтверждено | PublicNode TRON (independent java-tron node): {} - no data for this tx (node is not archival) | TronGrid node receipt log; TronGrid v1 events agree |
| 168 | transactions | step 22 9be4de8659 | to | TCiwRNyeUK7JwkEgF5W3AExFpZ2ErRZG4C | TCiwRNyeUK7JwkEgF5W3AExFpZ2ErRZG4C | подтверждено | PublicNode TRON (independent java-tron node): {} - no data for this tx (node is not archival) |  |
| 169 | transactions | step 22 9be4de8659 | amount | 250000.000000 | 250000.000000 | подтверждено | PublicNode TRON (independent java-tron node): {} - no data for this tx (node is not archival) |  |
| 170 | transactions | step 22 9be4de8659 | asset | USDT-TRC20 | USDT-TRC20 | подтверждено |  | token contract TR7NHqjeKQxGTCi8q8ZY4pL8otSzgjLj6t |
| 171 | transactions | step 22 9be4de8659 | timestamp_utc | 2026-09-22 08:25:00 | 2026-09-22 08:25:00 | подтверждено |  | block timestamp from gettransactioninfobyid |
| 172 | transactions | step 22 9be4de8659 | block | 86464399 | 86464399 | подтверждено |  |  |
| 173 | transactions | step 22 9be4de8659 | status | fact | contractRet=SUCCESS | подтверждено |  | 'fact' = the transaction exists and succeeded on chain |
| 174 | transactions | step 23 3cceeee9ed | from | TCiwRNyeUK7JwkEgF5W3AExFpZ2ErRZG4C | TCiwRNyeUK7JwkEgF5W3AExFpZ2ErRZG4C | подтверждено | PublicNode TRON (independent java-tron node): {} - no data for this tx (node is not archival) | TronGrid node receipt log; TronGrid v1 events agree |
| 175 | transactions | step 23 3cceeee9ed | to | TWBPGLwQw2EbqYLLw1DJnTDt2ZQ9yJW1JJ | TWBPGLwQw2EbqYLLw1DJnTDt2ZQ9yJW1JJ | подтверждено | PublicNode TRON (independent java-tron node): {} - no data for this tx (node is not archival) |  |
| 176 | transactions | step 23 3cceeee9ed | amount | 250000.000000 | 250000.000000 | подтверждено | PublicNode TRON (independent java-tron node): {} - no data for this tx (node is not archival) |  |
| 177 | transactions | step 23 3cceeee9ed | asset | USDT-TRC20 | USDT-TRC20 | подтверждено |  | token contract TR7NHqjeKQxGTCi8q8ZY4pL8otSzgjLj6t |
| 178 | transactions | step 23 3cceeee9ed | timestamp_utc | 2026-09-22 08:27:51 | 2026-09-22 08:27:51 | подтверждено |  | block timestamp from gettransactioninfobyid |
| 179 | transactions | step 23 3cceeee9ed | status | fact | contractRet=SUCCESS | подтверждено |  | 'fact' = the transaction exists and succeeded on chain |
| 180 | addresses | step 23 3cceeee9ed | TronScan tag 'WhiteBIT' | WhiteBIT | HTTP 401 (TronScan API requires an API key; keyless lookup refused) | не проверяемо |  | TronScan, pending written consent, not stored in any label store; one lookup, development verification only |
| 181 | theft | theft | block | 86439360 | 86439360 | подтверждено |  |  |
| 182 | theft | theft | energy used (note: 130,285 energy) | 130285 | 130285 | подтверждено |  |  |
| 183 | theft | theft | TRX burned (note: 0.345 TRX) | 0.345000 | 0.345000 | подтверждено |  | fee=345000 sun, net_fee=345000, energy_fee=0: the 0.345 TRX is the bandwidth fee; energy came from the delegation (step 3) |
| 184 | theft | theft | seconds_after_incoming_payment | 45 | 45 | подтверждено |  | incoming 7472e1e059 12937.000000 USDT |
| 185 | theft | victim | USDT balance before the large payment (step 2 note: 109.79) | 109.79 | 109.794750 | подтверждено |  | sum of all USDT transfers of the victim before 2026-09-21 11:31:54 (complete history) |
| 186 | mechanism | theft | single signature | 1 | 1 | подтверждено |  |  |
| 187 | mechanism | theft | no Permission_id (owner permission) | absent | absent | подтверждено |  | raw_data.contract[0] has no Permission_id -> permission 0 (owner) |
| 188 | mechanism | theft | signer = victim owner key (recovered from signature) | ["TNakrL7VUMLNN4EEpi64HKjj5YqafR5tUx"] | ["TNakrL7VUMLNN4EEpi64HKjj5YqafR5tUx"] | подтверждено |  | txID==sha256(raw_data): True |
| 189 | mechanism | victim | owner/active key = itself, threshold 1 (TronGrid, current state) | owner/active = itself, threshold 1 | {"owner_threshold": 1, "owner_keys": ["TNakrL7VUMLNN4EEpi64HKjj5YqafR5tUx"], "active": [[1, ["TNakrL7VUMLNN4EEpi64HKjj5YqafR5tUx"]]]} | подтверждено |  |  |
| 190 | mechanism | victim | owner/active key = itself, threshold 1 (PublicNode, current state) | owner/active = itself, threshold 1 | {"owner_threshold": 1, "owner_keys": ["TNakrL7VUMLNN4EEpi64HKjj5YqafR5tUx"], "active": [[1, ["TNakrL7VUMLNN4EEpi64HKjj5YqafR5tUx"]]]} | подтверждено | PublicNode getaccount (independent node) |  |
| 191 | mechanism | victim | permissions never changed (no AccountPermissionUpdateContract) | never changed | 0 permission updates in 8 outgoing txs (history complete: True) | подтверждено |  |  |
| 192 | addresses | TNakrL7VUM (victim (Trust Wallet)) | USDT balance now | 0.023623 | TronGrid 0.023623; PublicNode 0.023623 | подтверждено | PublicNode balanceOf agrees | live value read at the time of the re-fetch |
| 193 | addresses | TBY9jt5TJJ (payer of incoming payment (claimed by vi) | role (interpretation) | payer of incoming payment (claimed by victim) [claimed by victim] |  | не проверяемо |  | a role/intent label, not an on-chain fact; on-chain facts behind it are checked in the other rows |
| 194 | addresses | TDii6vao7x (energy-rental fee collector used by Trus) | role (interpretation) | energy-rental fee collector used by Trust Wallet ('Energy Rental') [medium-high (inferred)] |  | не проверяемо |  | a role/intent label, not an on-chain fact; on-chain facts behind it are checked in the other rows |
| 195 | addresses | TUSYcK5yf8 (TRX top-up/activation service used in th) | role (interpretation) | TRX top-up/activation service used in the same rental flow [medium (inferred)] |  | не проверяемо |  | a role/intent label, not an on-chain fact; on-chain facts behind it are checked in the other rows |
| 196 | addresses | TYGdh7qysH (thief hop 1 (fresh, activated 11:35:27)) | USDT balance now | ~0.274317 | TronGrid 0.274317; PublicNode 0.274317 | подтверждено | PublicNode balanceOf agrees | live value read at the time of the re-fetch |
| 197 | addresses | TYGdh7qysH (thief hop 1 (fresh, activated 11:35:27)) | activated 11:35:27 (activation transfer) | 2026-09-21 11:35:27 | 2026-09-21 11:35:27 | подтверждено |  | activation tx 945e074f0124 from TUSYcK5yf8Et4xNTiUcpfZwmhFsxfdoooo (0.800000 TRX); getaccount create_time = 2026-09-21 11:35:24: java-tron stamps create_time w… |
| 198 | addresses | TYGdh7qysH (thief hop 1 (fresh, activated 11:35:27)) | fresh (no activity before the theft) | fresh | 0 inbound native txs before the theft; create_time 2026-09-21 11:35:24 | подтверждено |  |  |
| 199 | addresses | TYn3YpDxmd (thief hop 2 / splitter 99%/1%) | USDT balance now | 0 | TronGrid 0.000000; PublicNode 0.000000 | подтверждено | PublicNode balanceOf agrees | live value read at the time of the re-fetch |
| 200 | addresses | TYn3YpDxmd (thief hop 2 / splitter 99%/1%) | role (interpretation) | thief hop 2 / splitter 99%/1% [high] |  | не проверяемо |  | a role/intent label, not an on-chain fact; on-chain facts behind it are checked in the other rows |
| 201 | addresses | TUrQNNez22 (launderer bridge-out wallet (reused sinc) | USDT balance now | ~0 | TronGrid 0.000000; PublicNode 0.000000 | подтверждено | PublicNode balanceOf agrees | live value read at the time of the re-fetch |
| 202 | addresses | TUrQNNez22 (launderer bridge-out wallet (reused sinc) | role (interpretation) | launderer bridge-out wallet (reused since 2026-08-26) [high] |  | не проверяемо |  | a role/intent label, not an on-chain fact; on-chain facts behind it are checked in the other rows |
| 203 | addresses | TRUJEtAFzB (1% fee collector (laundering service?)) | USDT net inflow since the window start | ~11.26 (from 2026-09-21 onward window) | net of 10 USDT transfers since 2026-09-21 00:00:00 = 11.263438 | подтверждено |  |  |
| 204 | addresses | TRUJEtAFzB (1% fee collector (laundering service?)) | role (interpretation) | 1% fee collector (laundering service?) [medium] |  | не проверяемо |  | a role/intent label, not an on-chain fact; on-chain facts behind it are checked in the other rows |
| 205 | addresses | TVNMa2ZrUW (operator gas wallet: funds TYn3Yp, TUrQN) | TRX balance | 505.05 | 364.228674 | не проверяемо |  | live value; the fixture gives no time for it and the current value differs |
| 206 | addresses | TVNMa2ZrUW (operator gas wallet: funds TYn3Yp, TUrQN) | role (interpretation) | operator gas wallet: funds TYn3Yp, TUrQNN, TYHeH2 [high (common funder)] |  | не проверяемо |  | a role/intent label, not an on-chain fact; on-chain facts behind it are checked in the other rows |
| 207 | addresses | TFG4wBaDQ8 (USDT0 OFT contract (LayerZero)) | contract name | UsdtOFT | UsdtOFT | подтверждено |  |  |
| 208 | addresses | 0x1F748c76 (USDT0 OFT adapter (Ethereum)) | Etherscan name tag | USDT0 OFT adapter (Ethereum) | HTTP 200: Sorry, it looks like you are trying to access an API Exclusive endpoint. Contact us to upgrade your API plan. | не проверяемо |  | Etherscan did not return a tag with the available key (name tags are an API Pro feature) |
| 209 | addresses | 0x1F748c76 (USDT0 OFT adapter (Ethereum)) | Blockscout contract name | UsdtOFT | UsdtOFT | подтверждено |  | public tags: none |
| 210 | addresses | 0x40790479 (launderer Ethereum transit EOA (reused A) | EOA reused Aug-Oct 2026 | reused Aug-Oct 2026 | is_contract=False; USDT transfers 36 from 2026-06-04 13:41:11 to 2026-10-13 16:27:11; 18 of them before August 2026 (first: 0x2CfF890f0378a11913B6129B2E97417a2… | РАСХОЖДЕНИЕ |  |  |
| 211 | addresses | 0x40790479 (launderer Ethereum transit EOA (reused A) | USDT balance ~0 | ~0 | net of all USDT transfers = 0.009086 (listing complete: True) | подтверждено |  |  |
| 212 | addresses | 0x40790479 (launderer Ethereum transit EOA (reused A) | role (interpretation) | launderer Ethereum transit EOA (reused Aug-Oct 2026) [high] |  | не проверяемо |  | a role/intent label, not an on-chain fact; on-chain facts behind it are checked in the other rows |
| 213 | addresses | 0x69460570 (Rango Diamond (aggregator)) | Etherscan name tag | Rango Diamond (aggregator) | HTTP 200: Sorry, it looks like you are trying to access an API Exclusive endpoint. Contact us to upgrade your API plan. | не проверяемо |  | Etherscan did not return a tag with the available key (name tags are an API Pro feature) |
| 214 | addresses | 0x69460570 (Rango Diamond (aggregator)) | Blockscout contract name | RangoDiamond | RangoDiamond | подтверждено |  | public tags: none |
| 215 | addresses | 0xDDdb9a95 (Rango affiliate of dApp 'MoonGate' (0.15) | Rango affiliate of dApp 'MoonGate' with a 0.15% fee | MoonGate, 0.15% | FeeInfo.affiliator=0xDDdb9a95E443A204EB8650D5EA578ed707Fe2123, dAppTag=1662, dAppName=MoonGate, fee=19.352116 = 0.150000% of 12901.411000 | подтверждено |  |  |
| 216 | addresses | 0xdA392553 (NEAR Intents 1Click one-time deposit add) | 1Click status API knows it as a deposit address | SUCCESS | SUCCESS | подтверждено |  |  |
| 217 | addresses | 0xdA392553 (NEAR Intents 1Click one-time deposit add) | role (interpretation) | NEAR Intents 1Click one-time deposit address [high (1Click status API)] |  | не проверяемо |  | a role/intent label, not an on-chain fact; on-chain facts behind it are checked in the other rows |
| 218 | addresses | 0x2CfF890f (NEAR Intents vault) | Etherscan name tag | NEAR Intents vault | HTTP 200: Sorry, it looks like you are trying to access an API Exclusive endpoint. Contact us to upgrade your API plan. | не проверяемо |  | Etherscan did not return a tag with the available key (name tags are an API Pro feature) |
| 219 | addresses | 0x2CfF890f (NEAR Intents vault) | explorer tag | NEAR Intents vault | {"name": null, "public_tags": []} | не проверяемо |  | Blockscout shows no name or public tag for this address; the tag probably comes from another explorer (Etherscan), which needs an API key |
| 220 | addresses | TX5XiRXdyz (NEAR Intents TRON payout wallet) | sender of the 1Click destination tx | TX5XiRXdyz7sdFwF5mnhT1QoGCpbkncpke | TX5XiRXdyz7sdFwF5mnhT1QoGCpbkncpke | подтверждено |  | that it is 'the NEAR Intents payout wallet' is an inference from this single swap |
| 221 | addresses | TX5XiRXdyz (NEAR Intents TRON payout wallet) | role (interpretation) | NEAR Intents TRON payout wallet [high] |  | не проверяемо |  | a role/intent label, not an on-chain fact; on-chain facts behind it are checked in the other rows |
| 222 | addresses | TYHeH2HQn7 (FINAL HUB: high-volume USDT wallet (OTC/) | USDT balance | 238766.644069 at ~2026-10-14 09:00 UTC (changes constantly) | now: TronGrid 248905.892432 | не проверяемо |  | the claim is tied to a past moment/window; only the current value can be read |
| 223 | addresses | TYHeH2HQn7 (FINAL HUB: high-volume USDT wallet (OTC/) | role (interpretation) | FINAL HUB: high-volume USDT wallet (OTC/laundering hub), same TRX funder as thief hops [high (destination); medium-high… |  | не проверяемо |  | a role/intent label, not an on-chain fact; on-chain facts behind it are checked in the other rows |
| 224 | addresses | TNJSC23oMc (WhiteBIT deposit address) | deposit pattern: full and quick forward to the WhiteBIT-tagged wallet | WhiteBIT deposit address | received 150000.000000 at 2026-09-21 13:41:15, forwarded 150000.000000 to TWBPGLwQw2EbqYLLw1DJnTDt2ZQ9yJW1JJ after 201 s | подтверждено |  | attribution to WhiteBIT rests on the hot-wallet label (TronScan, pending written consent) |
| 225 | addresses | TNJSC23oMc (WhiteBIT deposit address) | role (interpretation) | WhiteBIT deposit address [high] |  | не проверяемо |  | a role/intent label, not an on-chain fact; on-chain facts behind it are checked in the other rows |
| 226 | addresses | TCiwRNyeUK (WhiteBIT deposit address) | deposit pattern: full and quick forward to the WhiteBIT-tagged wallet | WhiteBIT deposit address | received 250000.000000 at 2026-09-22 08:25:00, forwarded 250000.000000 to TWBPGLwQw2EbqYLLw1DJnTDt2ZQ9yJW1JJ after 171 s | подтверждено |  | attribution to WhiteBIT rests on the hot-wallet label (TronScan, pending written consent) |
| 227 | addresses | TCiwRNyeUK (WhiteBIT deposit address) | role (interpretation) | WhiteBIT deposit address [high] |  | не проверяемо |  | a role/intent label, not an on-chain fact; on-chain facts behind it are checked in the other rows |
| 228 | addresses | TWBPGLwQw2 (WhiteBIT wallet (TronScan tag)) | TronScan tag 'WhiteBIT' | WhiteBIT | HTTP 401 (TronScan API requires an API key; keyless lookup refused) | не проверяемо |  | TronScan, pending written consent, not stored in any label store; one lookup, development verification only |
| 229 | addresses | TWBPGLwQw2 (WhiteBIT wallet (TronScan tag)) | role (interpretation) | WhiteBIT wallet (TronScan tag) [high (third-party tag)] |  | не проверяемо |  | a role/intent label, not an on-chain fact; on-chain facts behind it are checked in the other rows |
| 230 | links | funder->TYn3YpDxmd | TRX transfer 3248034386 | TVNMa2ZrUWE9sdBawJoQ8aN6LPFjv9ZppZ->TYn3YpDxmduw6fuKmFE3qkRHEoE2zeCfx3 | TransferContract TVNMa2ZrUWE9sdBawJoQ8aN6LPFjv9ZppZ->TYn3YpDxmduw6fuKmFE3qkRHEoE2zeCfx3 0.000100 TRX at 2026-09-21 11:38:51 | подтверждено | PublicNode TRON (independent java-tron node): {} - no data for this tx (node is not archival) |  |
| 231 | links | funder->TYn3YpDxmd | TRX transfer dbbae16c6e | TVNMa2ZrUWE9sdBawJoQ8aN6LPFjv9ZppZ->TYn3YpDxmduw6fuKmFE3qkRHEoE2zeCfx3 | TransferContract TVNMa2ZrUWE9sdBawJoQ8aN6LPFjv9ZppZ->TYn3YpDxmduw6fuKmFE3qkRHEoE2zeCfx3 6.529400 TRX at 2026-09-21 11:39:57 | подтверждено | PublicNode TRON (independent java-tron node): {} - no data for this tx (node is not archival) |  |
| 232 | links | funder->TYn3YpDxmd | TRX transfer e181937194 | TVNMa2ZrUWE9sdBawJoQ8aN6LPFjv9ZppZ->TYn3YpDxmduw6fuKmFE3qkRHEoE2zeCfx3 | TransferContract TVNMa2ZrUWE9sdBawJoQ8aN6LPFjv9ZppZ->TYn3YpDxmduw6fuKmFE3qkRHEoE2zeCfx3 7.021500 TRX at 2026-09-21 11:42:24 | подтверждено | PublicNode TRON (independent java-tron node): {} - no data for this tx (node is not archival) |  |
| 233 | links | funder->TUrQNNez22 | TRX transfer 3599ac1465 | TVNMa2ZrUWE9sdBawJoQ8aN6LPFjv9ZppZ->TUrQNNez22bPosc9NUuNvu7pxVWbziKFYU | TransferContract TVNMa2ZrUWE9sdBawJoQ8aN6LPFjv9ZppZ->TUrQNNez22bPosc9NUuNvu7pxVWbziKFYU 0.000100 TRX at 2026-08-27 07:29:33 | подтверждено | PublicNode TRON (independent java-tron node): {} - no data for this tx (node is not archival) |  |
| 234 | links | funder->TUrQNNez22 | TRX transfer 77655efb4e | TVNMa2ZrUWE9sdBawJoQ8aN6LPFjv9ZppZ->TUrQNNez22bPosc9NUuNvu7pxVWbziKFYU | TransferContract TVNMa2ZrUWE9sdBawJoQ8aN6LPFjv9ZppZ->TUrQNNez22bPosc9NUuNvu7pxVWbziKFYU 69.407295 TRX at 2026-09-21 11:49:51 | подтверждено | PublicNode TRON (independent java-tron node): {} - no data for this tx (node is not archival) |  |
| 235 | links | return TUrQNNez22->funder | TRX transfer 48eca492ee | TUrQNNez22bPosc9NUuNvu7pxVWbziKFYU->TVNMa2ZrUWE9sdBawJoQ8aN6LPFjv9ZppZ | TransferContract TUrQNNez22bPosc9NUuNvu7pxVWbziKFYU->TVNMa2ZrUWE9sdBawJoQ8aN6LPFjv9ZppZ 29.600000 TRX at 2026-08-27 07:46:12 | подтверждено | PublicNode TRON (independent java-tron node): {} - no data for this tx (node is not archival) |  |
| 236 | links | return TUrQNNez22->funder | TRX transfer 9ab7c48183 | TUrQNNez22bPosc9NUuNvu7pxVWbziKFYU->TVNMa2ZrUWE9sdBawJoQ8aN6LPFjv9ZppZ | TransferContract TUrQNNez22bPosc9NUuNvu7pxVWbziKFYU->TVNMa2ZrUWE9sdBawJoQ8aN6LPFjv9ZppZ 30.100000 TRX at 2026-08-31 11:57:57 | подтверждено | PublicNode TRON (independent java-tron node): {} - no data for this tx (node is not archival) |  |
| 237 | links | return TUrQNNez22->funder | TRX transfer 1f61852704 | TUrQNNez22bPosc9NUuNvu7pxVWbziKFYU->TVNMa2ZrUWE9sdBawJoQ8aN6LPFjv9ZppZ | TransferContract TUrQNNez22bPosc9NUuNvu7pxVWbziKFYU->TVNMa2ZrUWE9sdBawJoQ8aN6LPFjv9ZppZ 30.300000 TRX at 2026-09-21 11:52:57 | подтверждено | PublicNode TRON (independent java-tron node): {} - no data for this tx (node is not archival) |  |
| 238 | links | funder->TYHeH2HQn7 | TRX transfer b44d60c46a | TVNMa2ZrUWE9sdBawJoQ8aN6LPFjv9ZppZ->TYHeH2HQn7pM5fe6aYwGabz9x4yizJbwp6 | TransferContract TVNMa2ZrUWE9sdBawJoQ8aN6LPFjv9ZppZ->TYHeH2HQn7pM5fe6aYwGabz9x4yizJbwp6 0.000100 TRX at 2026-08-06 17:47:57 | подтверждено | PublicNode TRON (independent java-tron node): {} - no data for this tx (node is not archival) |  |
| 239 | links | funder->TYHeH2HQn7 | TRX transfer 5c1b1a5466 | TVNMa2ZrUWE9sdBawJoQ8aN6LPFjv9ZppZ->TYHeH2HQn7pM5fe6aYwGabz9x4yizJbwp6 | TransferContract TVNMa2ZrUWE9sdBawJoQ8aN6LPFjv9ZppZ->TYHeH2HQn7pM5fe6aYwGabz9x4yizJbwp6 13.129400 TRX at 2026-08-06 17:49:00 | подтверждено | PublicNode TRON (independent java-tron node): {} - no data for this tx (node is not archival) |  |
| 240 | links | funder->TYHeH2HQn7 | TRX transfer 8386c0b118 | TVNMa2ZrUWE9sdBawJoQ8aN6LPFjv9ZppZ->TYHeH2HQn7pM5fe6aYwGabz9x4yizJbwp6 | TransferContract TVNMa2ZrUWE9sdBawJoQ8aN6LPFjv9ZppZ->TYHeH2HQn7pM5fe6aYwGabz9x4yizJbwp6 13.621495 TRX at 2026-08-06 17:53:57 | подтверждено | PublicNode TRON (independent java-tron node): {} - no data for this tx (node is not archival) |  |
| 241 | links | funder->TYHeH2HQn7 | TRX transfer bdd5c283f7 | TVNMa2ZrUWE9sdBawJoQ8aN6LPFjv9ZppZ->TYHeH2HQn7pM5fe6aYwGabz9x4yizJbwp6 | TransferContract TVNMa2ZrUWE9sdBawJoQ8aN6LPFjv9ZppZ->TYHeH2HQn7pM5fe6aYwGabz9x4yizJbwp6 13.362500 TRX at 2026-08-06 18:39:54 | подтверждено | PublicNode TRON (independent java-tron node): {} - no data for this tx (node is not archival) |  |
| 242 | links | funder->TYHeH2HQn7 | TRX transfer b617d75b6c | TVNMa2ZrUWE9sdBawJoQ8aN6LPFjv9ZppZ->TYHeH2HQn7pM5fe6aYwGabz9x4yizJbwp6 | TransferContract TVNMa2ZrUWE9sdBawJoQ8aN6LPFjv9ZppZ->TYHeH2HQn7pM5fe6aYwGabz9x4yizJbwp6 0.211998 TRX at 2026-08-06 20:51:42 | подтверждено | PublicNode TRON (independent java-tron node): {} - no data for this tx (node is not archival) |  |
| 243 | links | TYHeH2HQn7 | activation (note) | activated by funder at 2026-08-06 17:47:57 | activated by funder at 2026-08-06 17:47:57 | подтверждено |  |  |
| 244 | links | TVNMa2ZrUW | funder created (note: 17:22:48) | 2026-08-06 17:22:48 | 2026-08-06 17:22:48 | подтверждено |  |  |
| 245 | links | upstream TMGtBUqWev->funder | TRX transfer 673c0f9f0c | TMGtBUqWevfE2y1XpvzTsHEkLpSDi4bW51->TVNMa2ZrUWE9sdBawJoQ8aN6LPFjv9ZppZ 918 TRX | TransferContract TMGtBUqWevfE2y1XpvzTsHEkLpSDi4bW51->TVNMa2ZrUWE9sdBawJoQ8aN6LPFjv9ZppZ 918.000000 TRX at 2026-08-06 17:22:51 | подтверждено | PublicNode TRON (independent java-tron node): {} - no data for this tx (node is not archival) |  |
| 246 | links | upstream TSm7vUxW9D->funder | TRX transfer d88f4a8b58 | TSm7vUxW9DvKiwwDRcaR36X8vBjKc99Sxe->TVNMa2ZrUWE9sdBawJoQ8aN6LPFjv9ZppZ 849.68 TRX | TransferContract TSm7vUxW9DvKiwwDRcaR36X8vBjKc99Sxe->TVNMa2ZrUWE9sdBawJoQ8aN6LPFjv9ZppZ 849.680000 TRX at 2026-08-08 09:36:15 | подтверждено | PublicNode TRON (independent java-tron node): {} - no data for this tx (node is not archival) |  |
| 247 | links | TMGtBUqWev upstream | funded by TSm7vUxW9D | TSm7vUxW9DvKiwwDRcaR36X8vBjKc99Sxe | ["TSm7vUxW9DvKiwwDRcaR36X8vBjKc99Sxe"] | подтверждено |  | senders of >= 1 TRX among its earliest 50 inbound transactions |
| 248 | links | TSm7vU | active since 2024-11 (unlabelled service) | since 2024-11 | create_time 2024-11-15 08:26:42 | подтверждено |  | 'high-volume' and 'likely a service' are interpretations, not checked |
| 249 | links | reused route tx 71ef4785df | USDT transfer on the path | path TF8uqg->TU6UZP->TUrQNN | TJtEySoVuA->TF8uqgGbCB 2831.357916 at 2026-08-26 14:00:21 | подтверждено |  |  |
| 250 | links | reused route tx b2eddd6b61 | USDT transfer on the path | path TF8uqg->TU6UZP->TUrQNN | TF8uqgGbCB->TU6UZPz6dw 2825.357916 at 2026-08-26 14:05:18 | подтверждено |  |  |
| 251 | links | reused route tx 94eae208ce | USDT transfer on the path | path TF8uqg->TU6UZP->TUrQNN | TU6UZPz6dw->TUrQNNez22 2797.104337 at 2026-08-26 14:11:30 | подтверждено |  |  |
| 252 | links | reused route tx 86266ede6d | USDT transfer on the path | path TF8uqg->TU6UZP->TUrQNN | TU6UZPz6dw->TRUJEtAFzB 28.253579 at 2026-08-26 14:14:00 | подтверждено |  |  |
| 253 | links | reused route tx c49b60019a | USDT transfer on the path | path TF8uqg->TU6UZP->TUrQNN | TUrQNNez22->TFG4wBaDQ8 2397.100000 at 2026-08-27 07:37:15 | подтверждено |  |  |
| 254 | links | reused route via TU6UZPz6dw | 99% to TUrQNN + exactly 1% to TRUJEt | 99%/1% split | TU6UZPz6dw received 2825.357916, sent 2797.104337 to TUrQNNez22 and 28.253579 to TRUJEt (2026-08-26 14:11:30); 1% of the input at 6 decimals, rounding: floor | подтверждено |  |  |
| 255 | links | reused route tx 836def7fc1 | USDT transfer on the path | path TFBsTj->TX7WP5->TUrQNN | TJtEySoVuA->TFBsTj5U1B 3095.264374 at 2026-08-30 09:21:24 | подтверждено |  |  |
| 256 | links | reused route tx 7793df5456 | USDT transfer on the path | path TFBsTj->TX7WP5->TUrQNN | TFBsTj5U1B->TX7WP5CptZ 3089.264374 at 2026-08-30 09:23:48 | подтверждено |  |  |
| 257 | links | reused route tx e1f1f323c4 | USDT transfer on the path | path TFBsTj->TX7WP5->TUrQNN | TX7WP5CptZ->TUrQNNez22 3058.371730 at 2026-08-30 09:28:54 | подтверждено |  |  |
| 258 | links | reused route tx aaf6fc63d9 | USDT transfer on the path | path TFBsTj->TX7WP5->TUrQNN | TX7WP5CptZ->TRUJEtAFzB 30.892644 at 2026-08-30 09:32:24 | подтверждено |  |  |
| 259 | links | reused route tx b1627342e9 | USDT transfer on the path | path TFBsTj->TX7WP5->TUrQNN | TUrQNNez22->TFG4wBaDQ8 2658.370000 at 2026-08-31 11:55:51 | подтверждено |  |  |
| 260 | links | reused route via TX7WP5CptZ | 99% to TUrQNN + exactly 1% to TRUJEt | 99%/1% split | TX7WP5CptZ received 3089.264374, sent 3058.371730 to TUrQNNez22 and 30.892644 to TRUJEt (2026-08-30 09:28:54); 1% of the input at 6 decimals, rounding: half-up | подтверждено |  |  |
| 261 | links | 0x4079 other inbound bridges | 2026-08-27 2396.380870 | 2026-08-27 2396.380870 | 2026-08-27 07:39:11 2396.380870 from 0x1F748c76 tx 0x62fc9f96e6 | подтверждено |  |  |
| 262 | links | 0x4079 other inbound bridges | 2026-08-31 2657.572489 | 2026-08-31 2657.572489 | 2026-08-31 11:57:59 2657.572489 from 0x1F748c76 tx 0x7660f34300 | подтверждено |  |  |
| 263 | links | 0x4079 other inbound bridges | 2026-10-01 25364.038505 | 2026-10-01 25364.038505 | 2026-10-01 06:50:35 25364.038505 from 0x1F748c76 tx 0x98d966b899 | подтверждено |  |  |
| 264 | links | 0x4079 other inbound bridges | 2026-10-12 4669.518724 | 2026-10-12 4669.518724 | 2026-10-12 19:23:59 4669.518724 from 0x1F748c76 tx 0x8cd1cf45ef | подтверждено |  |  |
| 265 | links | 0x4079 other inbound bridges | 2026-10-13 2095.951026 | 2026-10-13 2095.951026 | 2026-10-13 16:19:23 2095.951026 from 0x1F748c76 tx 0x5eb3b297db | подтверждено |  |  |
| 266 | ground_truth | arithmetic | total_fees_lost_before_hub = 13041.400772 - 12878.454902 | 162.94587 | 162.945870 | подтверждено |  | fixture amounts; both endpoints are confirmed on chain in the transaction rows |
| 267 | ground_truth | arithmetic | fee components reconcile to total_fees_lost_before_hub | 162.94587 | {"energy fee TYGdh7->TDii6v (step 7)": "5.486343", "left on TYGdh7 (13041.400772 - 5.486343 - 13035.640112)": "0.274317", "1% to TRUJEt (step 10)": "130.356401… | подтверждено |  |  |
| 268 | ground_truth | arithmetic | step 15 = affiliateFee + forwarded_amount | 12901.411000 | 12901.411000 | подтверждено |  |  |
| 269 | ground_truth | arithmetic | step 16 amount = Rango forwarded_amount | 12882.058884 | 12882.058884 | подтверждено |  |  |
| 270 | ground_truth | arithmetic | step 14 amount = USDT0 amountReceivedLD | 12901.408416 | 12901.408416 | подтверждено |  |  |
| 271 | ground_truth | arithmetic | step 8 + step 7 + residual = theft | 13041.400772 | 13041.400772 | подтверждено |  |  |

## Наблюдения (не расхождения)

- step 16 0x224f3859d0: 1Click originChainTxHashes = ["0x41bac088520409376e60709fd7114b7b3d670abeedfb01a68b7ee42a84ec515a"]; 1Click lists the tx that paid INTO the deposit address (the Rango tx) as the origin tx; fixture step 16 is the sweep OUT of the deposit address to 0x2CfF. Both transactions are real and the fixture does not claim otherwise: an observation, not a mismatch.

Ключи при перевыгрузке (только наличие): TRONGRID_API_KEY=***, TRON_RPC_URL=нет, BLOCKSCOUT_API_KEY=***, NEAR_INTENTS_JWT=***, TRONSCAN_API_KEY=***, ETHERSCAN_API_KEY=***
