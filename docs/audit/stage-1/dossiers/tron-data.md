# AREA tron-data: TRON blockchain data sources for USDT (TRC20)

============================================================
PART 1 - VERIFIER REPORT (takes precedence over the researcher wherever they disagree)
============================================================

## VERIFIER SUMMARY
Аудит в основном точен по фактам: из 27 перепроверенных утверждений 17 подтверждены первичными данными, 8 требуют поправок, 1 опровергнуто, 1 непроверяемо. Но две из девяти рекомендаций не выдерживают ограничений MVP. Что
подтвердилось вживую: - **TronGrid:** 3 rps без ключа и пауза 5 с; страница до 200 строк; в строке нет номера блока. - **TronScan:** 3 rps и штраф 120 с; 50 строк на страницу; окно 10,000. - **Сверка двух источников:** на новом
окне совпали 393 из 393 переводов. - **Блэклист:** работают все три события, включая RemovedBlackList; история достижима с 2020-06-26. - **Лицензии и цены:** java-tron LGPL-3.0 v4.8.2.3, tronpy MIT, тарифы Chainstack, Bitquery и
QuickNode. Главные поправки: - **TronScan не годится как второй независимый источник.** ToS 2022 запрещает сторонние приложения без письменного согласия, а шлюз лимитов у него общий с TronGrid. - **TronGrid не единственный
адресный индекс.** Аудит пропустил trezor/blockbook с поддержкой TRON (AGPL-3.0, активен). - **Бесплатный Chainstack слабее, чем описано.** eth_getLogs ограничен 100 блоками, план «AS-IS» и может быть приостановлен. - **Нагрузка
занижена примерно в 2.5 раза.** Граф на 1,000 адресов — около 3,300 запросов TronGrid, а не 1,300. - **SQD дороже.** Публичный Portal — около 50 MB в месяц и без коммерческого использования. - **Нулевые Transfer-строки в истории
есть** (5 из 1,200) — фильтр обязателен. Вывод о стоимости данных ($0–$49 в месяц) остаётся верным. QPS ключа TronGrid никем не измерен, поэтому цель «1,000 адресов за 5 минут» пока не доказана. Лимит WebSearch был исчерпан: новых
участников 2025–2026 я искал только прямым чтением документации и API.

## BLOCKING RISKS
- Юридический блокер второго источника: TRONSCAN Terms of Service (2022-01-04) запрещает сторонние приложения без письменного согласия и исключает организации США, Сингапура, материкового Китая, Гонконга и Тайваня; отдельных API-
условий нет. Без письменного разрешения TronScan нельзя закладывать в коммерческий продукт ни сверку, ни теги.
- Мнимая независимость: TronGrid и TronScan возвращают дословно одинаковое тело ошибки 429 (allowed_rps(3), suspended for N s) — это общий шлюз и один оператор экосистемы TRON. Требование 'два независимых источника' парой TronGrid +
TronScan не выполняется; единственная реальная независимость в текущем плане — receipts у стороннего узла.
- Единственный оператор для адресного индекса и internal transactions: платные тарифы TronGrid недоступны для покупки ('???', 'Coming soon'), есть только BASIC 100,000 запросов/день и заявка на Custom; ToS разрешает менять лимиты и
условия в любой момент, SLA нет. QPS с ключом официально не опубликован и не измерен — цель '1,000 адресов за 5 минут' пока не доказана.
- Расчёт нагрузки занижен: с учётом собственной рекомендации аудита по энергии/TRX граф на 1,000 адресов требует около 3,300 запросов TronGrid (11 rps) и 3,000–4,000 запросов к узлу; суточной квоты BASIC хватает примерно на 30
больших графов.
- Chainstack на бесплатном плане не годится как опора: eth_getLogs ограничен 100 блоками (пакетная проверка из аудита не работает), сервис 'AS-IS' и может быть приостановлен по усмотрению провайдера, ToS ограничивает использование
'internal business purposes'; наличие internal_transactions в его receipts не проверено (у PublicNode их нет, у TronGrid есть).
- В ответе TronGrid trc20 нет номера блока и статуса: цель '100% фактов подтверждены TXID и первичными данными' достижима только при отдельном receipt-запросе на каждый перевод — это надо заложить в бюджет запросов и времени.
- В истории присутствуют нулевые Transfer-события (address poisoning: 5 из 1,200 строк в пробе), а TronScan transaction-info показывает 'перевод' для неуспешных транзакций — без фильтров и проверки receipt трассировщик построит
ложные рёбра.
- Горячие кошельки бирж не листаются целиком: 393 перевода за 3 минуты и 1,200 за 76 минут у Binance-Hot 7; окно TronScan в 10,000 строк покрывает около 1–2.5 часа. Без жёсткой остановки на помеченной границе бюджет запросов и $1 на
расследование будут сорваны.
- Реестр контрактов SunSwap, JustLend и мостов не собран — правило 'остановиться на понятной границе' пока нечем исполнять; в примере из аудита мост опознаётся только по событию RelayErc20Deposit.
- Путь масштабирования дороже заявленного: публичный SQD Portal — около 50 MB/мес и без коммерческого использования, Starter $99 — 25 GB/мес; полный индекс USDT потребует тарифа от $499/мес с расширениями либо собственного узла на
3.5–4 TB.
- Ограничение самой перепроверки: лимит WebSearch в этой сессии был исчерпан, поэтому поиск новых участников 2025–2026 велся только прямым чтением документации и API известных проектов; не исключены пропущенные кандидаты.

## VERIFIER VERDICTS ON RECOMMENDATIONS

### NEED: История TRC20-переводов USDT по адресу с полной обратной пагинацией
PRIMARY: TronGrid v1 /v1/accounts/{address}/transactions/trc20 с собственным API key (BASIC, 100,000 запросов/день)
STANDS: True
ISSUE: Выбор верный и подтверждён пробами (200 строк/страница, курсор без дублей на 6 страницах, окна по времени на горячем кошельке, полное совпадение с TronScan на 393 строках). Но: 1) утверждение 'единственный источник' неверно; 2)
платных тарифов купить нельзя ('???' / 'Coming soon'), рост только через заявку Custom, а ToS разрешает менять лимиты в любой момент; 3) QPS ключа не измерен; 4) в списке есть нулевые Transfer-строки (5 из 1,200) и нет номера
блока; 5) TronGrid и TronScan отдают идентичное тело 429 — это один шлюз/оператор, отказ затронет оба источника сразу.
SUGGESTED CHANGE: Оставить TronGrid основным, но до фиксации архитектуры: завести ключ и замерить фактический QPS и поведение при исчерпании квоты; сразу подать заявку на Custom plan, чтобы знать цену; хранить value=0 строки как отдельный класс
(poisoning), не как рёбра; спроектировать TransferHistoryProvider так, чтобы второй реализацией был НЕ TronScan, а индекс стороннего оператора (Bitquery Pro или Blockbook-TRON), см. missed_candidates.

### NEED: Второй независимый источник для кросс-валидации и контекст по адресам
PRIMARY: TronScan API с собственным ключом — при условии письменного подтверждения условий
STANDS: False
ISSUE: Технически работает (сверка 393/393), но как 'независимый второй источник' в коммерческом SaaS не проходит: ToS 2022 прямо запрещает сторонние приложения без письменного согласия и использование материалов без письменного
разрешения, исключает организации США, Сингапура, Китая, Гонконга, Тайваня; отдельных API-условий нет. Организационно и инфраструктурно это тот же оператор, что TronGrid (одинаковый шлюз лимитов). Документация обещает Retry-After,
которого в 429 нет; штраф 120 с; 50 строк/страница (8 страниц против 2).
SUGGESTED CHANGE: Понизить TronScan до необязательного обогащения (теги, transaction-info) и включать только после письменного согласия. Требование 'два независимых источника' закрывать так: (а) обязательный receipt узла у стороннего оператора для
каждого факта; (б) независимый адресный индекс для выборочной сверки полноты — пробный месяц Bitquery Pro ($99, коммерческая лицензия; помнить, что trial не даёт archive) или Blockbook-TRON через NOWNodes. Теги бирж брать из
источников соседней области аудита, а не строить на TronScan.

### NEED: Первичные данные по TXID и верификация каждого факта (receipt, event logs, комиссии, caller)
PRIMARY: java-tron HTTP API у Chainstack; fallback TronGrid; keyless-резерв PublicNode
STANDS: True
ISSUE: Идея (receipt у другого оператора, чем история) верна; цены и наличие TRON на Developer-плане подтверждены. Ошибки: 1) пакетная проверка одним eth_getLogs на 5,000 блоков на Developer невозможна (лимит 100 блоков); 2) ToS: 'solely
for Customer's internal business purposes', бесплатный план 'AS-IS' и может быть приостановлен по усмотрению Chainstack — для продукта с целью 99% успешных запросов это не основа; 3) internal_transactions в receipt есть у
TronGrid, отсутствуют у PublicNode и не проверены у Chainstack; 4) сервис не опробован вживую.
SUGGESTED CHANGE: Закладывать Chainstack Growth $49/мес с первого платного клиента (SLA-план, eth_getLogs до лимита java-tron 5,000), на Developer проверять по одному receipt на TXID. До выбора провайдера сделать пробу: возвращает ли он
internal_transactions и как тарифицирует TRON (1 или 2 RU). Internal transactions всегда брать с TronGrid. Держать второй недорогой узел в конфигурации (GetBlock Free 50,000 CU/день и 20 RPS, Ankr Freemium, Nodit Basic $10/мес).

### NEED: Статус блэклиста Tether для адресов графа
PRIMARY: Локальное зеркало AddedBlackList / RemovedBlackList / DestroyedBlackFunds из TronGrid events + подтверждающий isBlackListed
STANDS: True
ISSUE: Подтверждено полностью, включая то, что аудит не проверил: RemovedBlackList отдаётся, история достижима с самого первого события (2020-06-26, блок 20972943), isBlackListed для свежего адреса = true. Замечание: зеркало строится на
том же TronGrid, что и история, — для независимости нужна сверка вторым путём.
SUGGESTED CHANGE: Добавить независимую сверку зеркала: eth_getLogs по трём topic'ам у стороннего узла скользящим окном за последние N часов и итоговый isBlackListed на /walletsolidity у другого оператора, чем TronGrid. В отчёте хранить и блок
события, и блок constant call.

### NEED: Контекст TRX, энергии и комиссий как следственная связь
PRIMARY: Receipt узла + TronGrid /v1/accounts/{addr}/transactions (Delegate/UnDelegate, первый входящий TRX) + /wallet/getaccount
STANDS: True
ISSUE: Данные подтверждены (Delegate от чужих адресов видны в списке получателя; в примере 66 из 67 от одного владельца). Но стоимость в запросах в общем расчёте не учтена: +2 запроса v1 на адрес утраивают нагрузку на TronGrid для
больших графов.
SUGGESTED CHANGE: Сделать энергетический контекст ленивым: считать только для адресов, попавших на путь отчёта (десятки, а не тысяча), с отдельным бюджетом запросов; кэшировать активацию адреса бессрочно. Известных провайдеров аренды энергии вести
реестром и не строить по ним связи.

### NEED: Данные для распознавания свопов, лендинга, мостов и депозитных sweep-переводов
PRIMARY: Полный receipt (все log[]) + признак контракта у получателя + реестр контрактов; sweep-паттерн на помеченный hot wallet
STANDS: True
ISSUE: Механизм подтверждён: пример fb7b3a24… — это депозит в мост (событие RelayErc20Deposit контракта TXtEs6t2oUWQsNos7m68gbHdE9Q5n6x2oN плюс internal call), всё видно в /v1/transactions/{txid}/events и internal-transactions. Но
ключевая часть — реестр контрактов SunSwap/JustLend/мостов — в аудите отсутствует, а internal transactions доступны только у TronGrid, что усиливает зависимость от одного оператора.
SUGGESTED CHANGE: Выделить сбор и проверку реестра контрактов в отдельную задачу до старта трассировщика (источник, дата проверки, confidence на каждую запись). Для правила остановки использовать сигнатуры событий (например RelayErc20Deposit, Swap)
как первичный признак, а тег — как вторичный. Признак 'exchange deposit' по sweep-паттерну без тега не присваивать (ограничение 95% точности).

### NEED: Клиентская библиотека
PRIMARY: Собственный тонкий async-клиент на httpx + утилиты base58check/ABI; tronpy только как вспомогательная зависимость
STANDS: True
ISSUE: Подтверждено кодом: tronpy MIT 0.6.2 содержит 6 встроенных общих ключей и не покрывает /v1. Возражений нет.
SUGGESTED CHANGE: В контрактные тесты добавить найденные расхождения: 429 без Retry-After у обоих сервисов, 400 на start=10050 у TronScan, нулевые Transfer-строки, receipt без internal_transactions у части провайдеров.

### NEED: Производительность, кэш и тариф: 1,000 адресов за 5 минут; стоимость при 100 и 1,000 расследований в месяц
PRIMARY: TronGrid key (BASIC) + Chainstack Developer, затем Growth $49 + TronScan key; локальные кэши
STANDS: True
ISSUE: Вывод о стоимости ($0–$49/мес на данные, много меньше $1 на расследование) выдерживает проверку. Расчёт нагрузки занижен примерно в 2.5 раза: с энергетическим контекстом около 3,300 запросов TronGrid на граф (11 rps, около 30
графов в сутки на BASIC), 3,000–4,000 запросов к узлу без пакетирования. Достижимость 5 минут опирается на неизмеренный QPS ключа. Компонент 'TronScan key' юридически заблокирован.
SUGGESTED CHANGE: Пересчитать бюджет с реальными коэффициентами и провести нагрузочный прогон с ключом до принятия SLA. По умолчанию: энергетический контекст и теги — вне критического пути 5 минут; счётчик суточной квоты с переключением на
fallback; Growth $49 как базовая постоянная статья расходов.

### NEED: Масштабирование после MVP: собственный индекс переводов USDT
PRIMARY: Пробный проект на SQD Portal (tron-mainnet) с squid-sdk tron-processor; запасной путь — свой java-tron
STANDS: False
ISSUE: Оценка стоимости неверна по существу: публичный Portal — около 50 MB/мес и без коммерческого использования; Starter $99 — 25 GB/мес и 1 сеть; биллинг 'not live yet'. Backfill 3.7 млрд логов USDT потребует Growth $499 плюс
расширения данных (250 GB за $99), а расширение на Ethereum/BSC/Solana — доплаты за сети. Не рассмотрены более прямые альтернативы.
SUGGESTED CHANGE: Сравнить в пробе три пути: SQD Growth (с реальным объёмом в GB), Blockbook-TRON (готовый адресный индекс поверх java-tron, AGPL-3.0, запуск немодифицированным отдельным сервисом) и Goldsky Turbo (TRON raw logs). Решение принимать
по измеренному объёму данных и цене за полный backfill, а не по цене входного тарифа.

## VERIFIER FACT CHECKS

- [CONFIRMED] TronGrid v1 :: Без ключа: 3 rps, при превышении HTTP 429 и пауза 5 с
  CORRECT VALUE: 6 параллельных запросов -> 1x200 и 5x429, тело: 'request rate exceeded the allowed_rps(3), and the query server is suspended for 5 s'. Заголовков Retry-After / X-RateLimit в ответах нет (только X-Trace-Id).
  METHOD: API call made (burst 6 параллельных GET)
  EVIDENCE: https://api.trongrid.io/v1/accounts/TDqSquXBgUCLYvYC4XZgrprLK589dkhSCf/transactions/trc20?contract_address=TR7NHqjeKQxGTCi8q8ZY4pL8otSzgjLj6t&limit=1

- [CONFIRMED] TronGrid v1 :: Страница максимум 200; limit=201 -> HTTP 400 с пустым телом; в элементе trc20 нет номера блока, признака confirmed и contractRet
  CORRECT VALUE: limit=200 -> 200 строк за 0.74 с; limit=201 -> 400, тело пустое. Ключи элемента: block_timestamp, from, to, token_info, transaction_id, type, value. Следствие: каждый факт отчёта требует отдельного receipt-запроса ради
blockNumber.
  METHOD: API call made
  EVIDENCE: https://api.trongrid.io/v1/accounts/TDqSquXBgUCLYvYC4XZgrprLK589dkhSCf/transactions/trc20?contract_address=TR7NHqjeKQxGTCi8q8ZY4pL8otSzgjLj6t&limit=200

- [CORRECTED] TronGrid v1 :: Горячие кошельки можно листать по fingerprint и окнами по времени; глубже 2 страниц не проверялось; нулевые transferFrom (address poisoning) не проверялись
  CORRECT VALUE: Проверено 6 страниц подряд (1,200 строк) для Binance-Hot 7 с min_timestamp=2022-03-01 и order_by=block_timestamp,asc: 0 дублей, монотонность соблюдена, 0.67–0.91 с на страницу. Первый перевод USDT этого адреса — 2023-10-18
07:50:24 UTC (1,200 переводов уложились примерно в 76 минут). Нулевые Transfer-строки (value='0') В СПИСКЕ ЕСТЬ: 5 из 1,200 — фильтр обязателен, пункт из not_verified закрыт. Общий потолок глубины по fingerprint по-прежнему не
установлен.
  METHOD: API call made (6 страниц по fingerprint)
  EVIDENCE: https://api.trongrid.io/v1/accounts/TDqSquXBgUCLYvYC4XZgrprLK589dkhSCf/transactions/trc20?contract_address=TR7NHqjeKQxGTCi8q8ZY4pL8otSzgjLj6t&limit=200&min_timestamp=1646092800000&order_by=block_timestamp,asc

- [CONFIRMED] TronGrid v1 :: План BASIC: цена 0, 100,000 Requests/Day, 3 API Keys; TRIAL 500,000; Developer/Team/Business с ценой '???'
  CORRECT VALUE: В bundle.29481f13.js жёстко зашито plans=[{price:0,name:'BASIC',threshold:1e5,category:'FREE',capacity:3},{price:0,name:'TRIAL',threshold:5e5,category:'TRIAL',capacity:3}]; Custom — 'Custom Price'; Developer/Team/Business — price
'???', категория 'Charge', кнопка 'Coming soon'. То есть купить платный тариф сейчас нельзя: путь роста только через заявку на Custom.
  METHOD: чтение текста JS-bundle сайта (без исполнения)
  EVIDENCE: https://www.trongrid.io/bundle.29481f13.js

- [CONFIRMED] TronGrid v1 :: ToS: Last updated September 24, 2026; запрет 'resell, sublicense or provide unauthorized third-party access'; данные 'may be incomplete, delayed or inaccurate'; право Сингапура, SIAC; прямого запрета коммерческого использования
нет
  CORRECT VALUE: Все цитаты найдены дословно. Дополнительно в разделе Fees: 'We reserve the right to change the availability, features, pricing, rate limits, or plan terms of the Services at any time'. Запрет автоматизированного сбора относится к
'website content', не к API. Положений о кэшировании/хранении ответов API в ToS нет (ни разрешения, ни запрета).
  METHOD: чтение текста ToS, зашитого в JS-bundle сайта
  EVIDENCE: https://www.trongrid.io/bundle.29481f13.js

- [CORRECTED] TronGrid v1 :: Документация rate-limits обновлена 2026-07-21 и не содержит чисел; rate-limits-1 пишет 'such as 30 requests per second' и 'such as 1 request per second'
  CORRECT VALUE: /reference/rate-limits: updatedAt 2026-09-08 (чисел нет, есть 'Do not hard-code fixed limits into business logic'). /reference/rate-limits-1: updatedAt 2026-07-21, примеры '30 requests per second' и '1 request per second' после
исчерпания суточной квоты. Дата 2026-07-21 относится ко второй странице. QPS с ключом официально нигде не зафиксирован и вживую никем не проверен.
  METHOD: docs read (обе страницы)
  EVIDENCE: https://developers.tron.network/reference/rate-limits

- [REFUTED] TronGrid v1 :: Единственный публичный источник с индексом 'адрес -> TRC20-переводы' и окном по времени
  CORRECT VALUE: TronScan /api/token_trc20/transfers тоже принимает relatedAddress + start_timestamp/end_timestamp (моя проба: 393 строки за 8 страниц, полное совпадение с TronGrid). Кроме того, адресный индекс TRON есть в trezor/blockbook
(configs/coins/tron.json, docs/api-tron.md) и у Bitquery. TronGrid — самый удобный (200 строк/страница, курсор), но не единственный.
  METHOD: API call made + code read (trezor/blockbook через gh api)
  EVIDENCE: https://apilist.tronscanapi.com/api/token_trc20/transfers?limit=50&start=0&contract_address=TR7NHqjeKQxGTCi8q8ZY4pL8otSzgjLj6t&relatedAddress=TDqSquXBgUCLYvYC4XZgrprLK589dkhSCf&start_timestamp=1789473600000&end_timestamp=1789473780000

- [CONFIRMED] TronGrid v1 :: Internal transactions у публичных узлов отсутствуют; эндпоинт TronGrid /v1/transactions/{txid}/internal-transactions вживую не проверен
  CORRECT VALUE: Эндпоинт работает без ключа: для fb7b3a24…e877 вернул 1 internal tx (note 'call', rejected false). Важное дополнение: /walletsolidity/gettransactioninfobyid на TronGrid САМ возвращает поле internal_transactions, а тот же вызов на
PublicNode — нет. Значит receipt у стороннего оператора (Chainstack/PublicNode) может быть беднее, чем у TronGrid; для Chainstack это не проверено.
  METHOD: API call made (TronGrid и PublicNode, один и тот же TXID)
  EVIDENCE: https://api.trongrid.io/v1/transactions/fb7b3a2433596693d191d3211147a58e849bfeef24ac1a02d85118166cf0e877/internal-transactions

- [CORRECTED] TronScan API :: limit>50 молча обрезается до 50; total/rangeTotal всегда 10000; start=10000 возвращает 1 строку без ошибки
  CORRECT VALUE: limit=200 -> 50 строк, total=10000, rangeTotal=10000 — подтверждено. start=10000 -> 1 строка за 5.6 с — подтверждено. Уточнение: start=10050 уже даёт HTTP 400 {'message':'some parameters are invalid or out of range'}, то есть
усечение 'тихое' только ровно на границе 10,000.
  METHOD: API call made
  EVIDENCE: https://apilist.tronscanapi.com/api/token_trc20/transfers?limit=50&start=10050&contract_address=TR7NHqjeKQxGTCi8q8ZY4pL8otSzgjLj6t&relatedAddress=TDqSquXBgUCLYvYC4XZgrprLK589dkhSCf

- [CONFIRMED] TronScan API :: Без ключа: allowed_rps(3), HTTP 429 и блокировка 120 с; /api/accountv2 -> 401
  CORRECT VALUE: 5 параллельных запросов -> 2x429 с телом '…allowed_rps(3), and the query server is suspended for 120 s'; accountv2 -> 401. Расхождение с документацией: docs.tronscan.org (Last updated March 16, 2026) требует 'back off per Retry-
After', но заголовка Retry-After в ответе 429 нет. Формат тела 429 дословно совпадает с TronGrid — признак общего шлюза/оператора.
  METHOD: API call made (burst 5 параллельных GET) + docs read
  EVIDENCE: https://apilist.tronscanapi.com/api/account/tag?address=TDqSquXBgUCLYvYC4XZgrprLK589dkhSCf

- [CONFIRMED] TronScan API :: ToS от 2022-01-04: запрет 'Develop any third-party applications that interact with our Services without our prior written consent'; eligibility исключает материковый Китай, Тайвань, Гонконг, США и Сингапур; 'Excerpts and links may
be used, provided that full and clear credit is given to TRONSCAN.io'
  CORRECT VALUE: Все три цитаты найдены дословно в PDF (11 страниц, 'Last updated: January 4, 2022'). Дополнительно: запрет 'Use any robot, spider, crawler, scraper or other automated means or interface not provided by us to access our Services or
to extract data' и 'Unauthorized use and/or duplication of this material without express and written permission … is strictly prohibited'. Слов 'API' и 'commercial use' в документе нет вообще.
  METHOD: PDF скачан WebFetch, текст извлечён pypdf и прочитан
  EVIDENCE: https://static.tronscan.org/pdf/TRONSCAN_Terms_of_Service.pdf

- [CONFIRMED] TronScan API :: Числовые лимиты для ключа в документации не указаны; платных тарифов не найдено
  CORRECT VALUE: Страница common-network-auth (Last updated: March 16, 2026) прочитана целиком: 'API Key Tiers' — это категории эндпоинтов (Required / Strongly Recommended / Optional / Unsupported), а не тарифы. Чисел QPS/квот и цен нет; сказано
лишь 'An API Key is required for calling Mainnet endpoints' и 'Rate limiting is global (not per-endpoint)'. Объявление support.tronscan.org об обязательности ключа проверить не удалось (403).
  METHOD: docs read (HTML получен обычным GET, challenge не возникал)
  EVIDENCE: https://docs.tronscan.org/en/api/common-network-auth

- [CONFIRMED] TronGrid v1 vs TronScan :: Сверка на одном адресе и окне: 308 из 308 совпадений, расхождений по времени 0
  CORRECT VALUE: Независимо повторено на ДРУГОМ окне (Binance-Hot 7, 2026-09-15 12:00:00–12:03:00 UTC): TronGrid 393 строки за 2 страницы, TronScan 393 строки за 8 страниц; по ключу (txid, from, to, value) совпало 393/393, расхождений
block_timestamp 0. Границы окна у обоих включают одинаково.
  METHOD: API call made (2 запроса TronGrid + 8 TronScan, сравнение множеств в python)
  EVIDENCE: https://api.trongrid.io/v1/accounts/TDqSquXBgUCLYvYC4XZgrprLK589dkhSCf/transactions/trc20?contract_address=TR7NHqjeKQxGTCi8q8ZY4pL8otSzgjLj6t&limit=200&min_timestamp=1789473600000&max_timestamp=1789473780000

- [CONFIRMED] TronGrid / TronScan / node receipt :: Неуспешный перевод c74ec7aa…6cf6 (OUT_OF_ENERGY) отсутствует в trc20-списках, receipt без log; TronScan transaction-info всё равно заполняет trc20TransferInfo (фантомный перевод)
  CORRECT VALUE: Receipt: result FAILED, receipt.result OUT_OF_ENERGY, net_usage 345, поля log нет, блок 87084302. В trc20-списке владельца TD3BgzJA2MnarxkhedCq9Fe9o5R2SoRg2r на TronGrid — 0 строк. TronScan transaction-info: contractRet
OUT_OF_ENERGY, event_count 0, но trc20TransferInfo содержит запись type 'Transfer'. Случай REVERT по-прежнему никем не проверен.
  METHOD: API call made (TronGrid walletsolidity + wallet + v1, TronScan)
  EVIDENCE: https://apilist.tronscanapi.com/api/transaction-info?hash=c74ec7aa69947f3c7e9e8f8c347211a56ee9986ea0297efd5d845f296dbf6cf6

- [CONFIRMED] TRON JSON-RPC :: eth_getLogs ограничен 5000 блоками (ошибка -32602 'exceed max block range: 5000'); config.conf: maxBlockRange 5000, maxSubTopics 1000, maxBatchSize 100, maxResponseSize 26214400, saveInternalTx=false
  CORRECT VALUE: PublicNode: диапазон ровно 5000 блоков -> результат, 5001 -> error -32602 'exceed max block range: 5000'. Все пять значений найдены в framework/src/main/resources/config.conf ветки master.
  METHOD: API call made (2 eth_getLogs) + code read (raw.githubusercontent.com)
  EVIDENCE: https://github.com/tronprotocol/java-tron/blob/master/framework/src/main/resources/config.conf

- [CONFIRMED] java-tron / event-plugin :: java-tron: LGPL-3.0, 4,170 stars, 71 issue, релиз GreatVoyage-v4.8.2.3 от 2026-09-30, Windows не поддерживается, 3.5 TB Full / 200 GB Lite; event-plugin: лицензии нет, v3.0.0 от 2026-07-03; LiteFnQueryHttpFilter блокирует
gettransactionbyid/gettransactioninfobyid
  CORRECT VALUE: gh api: LGPL-3.0, pushed 2026-10-13, 4170 stars, 71 open issues, v4.8.2.3 опубликован 2026-09-30T09:17:33Z. README: 'Windows is not supported', FullNode Stable 8 CPU/32 GB/3.5 TB, Recommend 16+/32 GB+/4 TB. event-plugin:
license=none, в корне нет файла LICENSE, v3.0.0 2026-07-03. В фильтре Lite-узла перечислены /wallet и /walletsolidity gettransactionbyid, gettransactioninfobyid, getblockbynum, gettransactioninfobyblocknum.
  METHOD: gh api (метаданные, releases, contents) + code read
  EVIDENCE: https://api.github.com/repos/tronprotocol/java-tron

- [CONFIRMED] Chainstack TRON :: Developer $0: 3M RU/мес, 25 RPS; Growth $49: 20M RU, 250 RPS; Pro $199; Business $499; overage $20/$15/$12.5/$10; full 1 RU, archive 2 RU; Unlimited Node от $149
  CORRECT VALUE: Все числа совпадают со страницей pricing. Дополнительно: Enterprise от $990/мес (400M RU, $5 за 1M). Unlimited Node доступен начиная с Growth.
  METHOD: docs read (pricing page)
  EVIDENCE: https://chainstack.com/pricing/

- [CORRECTED] Chainstack TRON :: TRON на бесплатном Developer-плане подтверждён только блогом; ToS не читался; пакетная проверка одним eth_getLogs на окно до 5,000 блоков
  CORRECT VALUE: 1) Продуктовая страница Chainstack прямо говорит: Developer $0 включает TRON (3M RU, до 25 RPS). 2) НО по docs.chainstack.com/docs/limits диапазон eth_getLogs на Developer — 100 блоков (Growth и выше — 10,000; java-tron всё равно
режет до 5,000). Пакетная проверка окнами по 5,000 блоков на бесплатном плане невозможна — нужен Growth $49 или по одному receipt на TXID. 3) ToS (Last Updated: June 2026): 'use Chainstack Services solely for Customer's internal
business purposes', запрет 'make Chainstack Services available to any third party'; бесплатный план 'AS-IS', Chainstack 'at its sole discretion has a right at any time to suspend Services' и может односторонне менять условия
бесплатных планов. Наличие internal_transactions в receipt и множитель RU для TRON (1 или 2) не проверены.
  METHOD: docs read (limits, build-better-with-tron, tos); живых вызовов нет — нужен аккаунт
  EVIDENCE: https://docs.chainstack.com/docs/limits

- [CONFIRMED] tronpy :: MIT, 244 stars, версия 0.6.2, последний коммит 2026-01-08; в tronpy/providers/http.py зашиты 6 общих TronGrid-ключей (DEFAULT_API_KEYS)
  CORRECT VALUE: gh api: MIT, 244 stars, 4 issues, pushed 2026-01-08; последний коммит 'Version 0.6.2' 2026-01-08T01:53:45Z. В http.py массив DEFAULT_API_KEYS содержит ровно 6 UUID-ключей.
  METHOD: gh api + code read
  EVIDENCE: https://github.com/andelf/tronpy/blob/master/tronpy/providers/http.py

- [CONFIRMED] Bitquery :: Personal $29/мес (годовая оплата), без коммерции; Pro $69 годовая / $99 помесячно, 1M points, 90 req/min, Commercial-use license; Scale $199/$299, 5M points, 240 req/min; trial 1,000 points
  CORRECT VALUE: Числа совпадают. Дополнение, которого нет в аудите: в 7-дневный trial 'Archive history is not included' — пробный период не позволит проверить глубину истории TRON, то есть рекомендованная 'проба' не закрывает главный открытый
вопрос.
  METHOD: docs read (pricing page)
  EVIDENCE: https://bitquery.io/pricing

- [CORRECTED] SQD Portal :: Публичный Portal бесплатно для разработки; Starter $99/мес, Growth $499/мес; squid-sdk Apache-2.0, пакеты tron-* есть
  CORRECT VALUE: Цены верны, но упущены лимиты: Public $0 — около 0.1 MB/s и около 50 MB данных в месяц, Commercial use: No; Testing $0 — около 1 GB, 1 сеть, без коммерции; Starter $99 — 25 GB/мес, 1 сеть, без SLA; Growth $499 — 400 GB/мес; доп.
250 GB за $99. 'Portal billing is not live yet' (платные планы — early access). squid-sdk: Apache-2.0, pushed 2026-10-13, каталоги tron-data, tron-processor и др. на месте; subsquid/sqd-portal — AGPL-3.0. Полный backfill 3.7 млрд
Transfer-логов USDT в 25 GB не поместится.
  METHOD: docs read + gh api
  EVIDENCE: https://docs.sqd.dev/en/portal/pricing.md

- [CORRECTED] GetBlock / Ankr :: GetBlock free: 50,000 CU/день, RPS 5 или 20 — не подтверждено; Pro $399; Ankr: цены известны только из обзора конкурента
  CORRECT VALUE: GetBlock (собственная документация): Free 50,000 CU/день, 20 RPS, 2 access tokens; Starter $49/мес, 90M CU, 250 RPS; Pro $499/мес, 1B CU, 800 RPS. Ankr (собственная документация): Freemium 200M API credits/мес, около 1,800
req/min; PAYG $0.10 за 1M credits; 200 credits за запрос non-EVM (около 1M запросов/мес бесплатно, $20 за 1M далее). Упоминания TRON по имени на странице планов Ankr нет.
  METHOD: docs read (GetBlock docs, https://www.ankr.com/docs/rpc-service/service-plans/)
  EVIDENCE: https://docs.getblock.io/getting-started/plans-and-limits/cu-and-rate-limits

- [CONFIRMED] QuickNode / GoldRush / Flipside / Google BigQuery :: QuickNode: free trial 10M credits 15 RPS, Build $49 80M 50 RPS, постоянного бесплатного плана нет; GoldRush не поддерживает TRON; docs Flipside -> 301 на edisyl.com; BigQuery 'Tron Blockchain (Preview)'
  CORRECT VALUE: QuickNode: числа совпадают, бесплатен только trial. GoldRush: слова 'Tron' на странице сетей нет. docs.flipsidecrypto.xyz -> 301 https://edisyl.com/ (продажа SonarX не проверялась). BigQuery: 'Tron Blockchain (Preview)',
maintainer Google, идентификатор листинга blockchain-analytics-tron-mainnet-us (аудит его не нашёл).
  METHOD: docs read + curl (redirect)
  EVIDENCE: https://docs.cloud.google.com/blockchain-analytics/docs/supported-datasets

- [CONFIRMED] USDT blacklist (on-chain) :: AddedBlackList: 200 событий за 2026-09-30…2026-10-13; DestroyedBlackFunds до 2026-10-09; RemovedBlackList не запрашивался; TronScan total 7838; isBlackListed через triggerconstantcontract
  CORRECT VALUE: AddedBlackList: 200 событий 2026-09-30 14:25 … 2026-10-13 13:49 UTC. RemovedBlackList РАБОТАЕТ: 200 событий 2026-05-14 … 2026-10-13 13:48 UTC (result._user). DestroyedBlackFunds: 2026-05-26 … 2026-10-09, _blackListedUser +
_balance. order_by=block_timestamp,asc отдаёт самое первое AddedBlackList — 2020-06-26 15:22:39 UTC, блок 20972943, то есть полная история достижима. isBlackListed(0x0684d2…c72f) на PublicNode = true — согласуется с событием от
2026-10-13. TronScan /api/stableCoin/blackList total=7838.
  METHOD: API call made (TronGrid x4, PublicNode x1, TronScan x1)
  EVIDENCE: https://api.trongrid.io/v1/contracts/TR7NHqjeKQxGTCi8q8ZY4pL8otSzgjLj6t/events?event_name=RemovedBlackList&limit=200

- [CORRECTED] TronGrid /v1/accounts/{addr}/transactions (энергия) :: Для TKGiE3… список вернул 67 DelegateResourceContract и 68 UnDelegateResourceContract от одного провайдера энергии и 65 TriggerSmartContract
  CORRECT VALUE: Счётчики типов верны (67 / 68 / 65), но делегирований от одного адреса 66, ещё 1 — от другого владельца (41bcb31b…64b4); ресурс ENERGY. Чужие Delegate-транзакции действительно попадают в список получателя. Полнота на других
адресах не проверялась.
  METHOD: API call made
  EVIDENCE: https://api.trongrid.io/v1/accounts/TKGiE3LRQ7R1fAy2ZxhkVsBkex16bePp1S/transactions?limit=200

- [CORRECTED] Расчёт производительности :: Граф на 1,000 адресов = около 1,300 запросов к TronGrid (4.3 rps) + около 2,000 к узлу; BASIC-квоты хватает с запасом в 15–30 раз
  CORRECT VALUE: Расчёт противоречит собственной рекомендации аудита по энергии/TRX: она добавляет 2 запроса v1 на адрес (активация + список транзакций). Итого около 3,300 запросов TronGrid на граф = 11 rps в среднем за 300 с и при 0.7–0.9 с на
страницу требует 10+ параллельных соединений; суточной квоты 100,000 хватает примерно на 30 таких графов, а не на 70. Проверку рёбер нельзя пакетировать через eth_getLogs на бесплатном Chainstack (100 блоков) — по одному receipt
на TXID, то есть 3,000–4,000 запросов к узлу (10–13 rps из 25). Осуществимо, но запас в разы меньше заявленного, а QPS ключа TronGrid не измерен.
  METHOD: пересчёт по подтверждённым лимитам (docs + живые замеры латентности)
  EVIDENCE: https://developers.tron.network/reference/rate-limits-1

- [UNVERIFIABLE] TronGrid v1 :: QPS с API key — 15 или 30 rps
  CORRECT VALUE: Ни одно первичное число не найдено: официальные страницы дают только пример '30 requests per second' и запрет хардкодить лимиты; ключ не создавался (правила аудита). До нагрузочного прогона с реальным ключом цель '1,000 адресов за
5 минут' остаётся недоказанной.
  METHOD: docs read (select-network, rate-limits, rate-limits-1); живой проверки нет
  EVIDENCE: https://developers.tron.network/reference/select-network

## CANDIDATES MISSED BY THE RESEARCHER (found by verifier)

- trezor/blockbook — поддержка TRON (адресный индекс поверх java-tron) (https://github.com/trezor/blockbook/blob/master/docs/api-tron.md)
  WHY: Готовый open-source индексатор 'адрес -> транзакции/токены' с REST API v2 и WebSocket; именно он стоит за 'TRON BlockBook API' у NOWNodes, который аудит отклонил как неподтверждённый. Даёт организационно независимый от TRON DAO
индекс — то, чего не хватает паре TronGrid + TronScan.
  ASSESSMENT: Проверено gh api и чтением кода: AGPL-3.0, 796 stars, pushed 2026-10-12, коммиты по bchain/coins/tron от 2026-10-05; configs/coins/tron.json (backend java-tron 4.8.2.3, processInternalTransactions=true), docs/api-tron.md, tron-
config.md, tron-sync-tuning.md. Минусы: AGPL (безопасно только как немодифицированный отдельный сервис), нужен полный узел 3.5 TB плюс RocksDB-индекс — это фаза 2, не MVP. Хостинг-вариант через NOWNodes: цены на сайте не показаны,
эндпоинты и TRC20-пагинация не проверены — нужна проба.

- Goldsky Turbo (TRON mainnet) (https://docs.goldsky.com/chains/supported-networks)
  WHY: Управляемые пайплайны данных: по таблице сетей TRON (chain id 728126428) поддержан в Turbo с raw logs, enriched transactions, blocks и Fast Scan — альтернатива SQD для собственного индекса переводов USDT без эксплуатации узла.
  ASSESSMENT: Только чтение документации. Traces для TRON нет, готовых decoded transfers для TRON не заявлено, Subgraphs/Mirror/Edge RPC для TRON нет. Цены и условия коммерческого использования не читались. Кандидат на сравнение в фазе 2.

- Nodit (Lambda256) — TRON Node API (https://developer.nodit.io/chains/tron/overview.md)
  WHY: Ещё один независимый оператор java-tron API с дешёвым входным тарифом — запасной провайдер receipts вместо бесплатных планов без SLA.
  ASSESSMENT: Документация: FullNode HTTP API (93 метода), Solidity HTTP API (35), RPC API (34, включая eth_getLogs). Планы: Free Trial 1M CU/день, но ограничен 30 днями; Basic $10/мес 100M CU, 400 CU/s; Developer $45/мес 450M CU. Покрытие TRON
в их Web3 Data API (переводы по адресу) не подтверждено — страница рендерится компонентом. Не опробовано вживую.

- Pinax API (бывший The Graph Token API) — TVM-маршруты (https://github.com/pinax-network/pinax-api)
  WHY: Открытый (Apache-2.0) API поверх Substreams с маршрутами /tvm/transfers, /tvm/swaps, /tvm/pools, /tvm/tokens — потенциально независимый индекс переводов и DEX-свопов TRON; связан с pinax-network/substreams-tron из аудита.
  ASSESSMENT: Код активен (pushed 2026-10-08, CHANGELOG 3.10.0 упоминает EVM/TVM), но хостинг TRON сейчас не отдаёт: живой GET https://api.pinax.network/v1/networks вернул 10 сетей без tron, /v1/tvm/transfers -> 404; документация перечисляет
Ethereum, Base, Arbitrum One, Solana. Сегодня непригоден, держать в наблюдении.

- TronScan: неучтённые эндпоинты /api/token_trc20/transfers-with-status и /api/deep/account/relatedAccount (https://docs.tronscan.org/llms.txt)
  WHY: Первый отдаёт переводы вместе со статусом исполнения (решает проблему фантомных переводов в transaction-info), второй — связанные аккаунты (готовый сигнал для graph-intelligence). Оба есть в индексе документации, в аудите не
упомянуты.
  ASSESSMENT: Только индекс документации, вживую не вызывались (бюджет запросов к хосту исчерпан). Подпадают под те же юридические ограничения ToS 2022, поэтому полезны только после письменного согласия TronScan.

- Проверенные и исключённые новые кандидаты: Etherscan API v2, Allium Realtime APIs, Sim by Dune (https://api.etherscan.io/v2/chainlist)
  WHY: Чтобы не тратить время повторно: это очевидные претенденты на роль независимого адресного индекса, появившиеся или обновлённые в 2025–2026.
  ASSESSMENT: Etherscan v2 chainlist: 63 сети, TRON нет (живой GET). Allium: https://api.allium.so/api/v1/supported-chains/realtime-apis не содержит tron (живой GET) — у Allium TRON только в историческом каталоге. Sim by Dune: docs.sim.dune.com
отвечает 301 на dune.com/blog/sunsetting-sim — продукт сворачивается. Ни один не подходит.

============================================================
PART 2 - RESEARCHER AUDIT
============================================================

## RESEARCHER RECOMMENDATIONS

### R1. NEED: История TRC20-переводов USDT по адресу с полной обратной пагинацией (discovery для трассировщика)
PRIMARY: TronGrid v1: GET /v1/accounts/{address}/transactions/trc20 с собственным API key (план BASIC, 100,000 запросов/день)
RATIONALE: Единственный проверенный источник, который отдаёт переводы по адресу страницами по 200 с курсором fingerprint и фильтрами по времени и направлению. Живая проба: окно 2024-01-01 на горячем кошельке Binance-Hot 7 вернулось за 1.03
с, сортировка asc от первого перевода — за 0.61 с; значит, очень загруженные адреса можно читать окнами по времени, не листая миллионы строк. Неуспешные вызовы в список не попадают, фильтр contract_address отсекает поддельные
токены. Сверка с TronScan на одном адресе и окне дала 308 из 308 совпадений.
ARCHITECTURE NOTES: Запрос трассировщика: only_from=true, min_timestamp = время входящего перевода, order_by=block_timestamp,asc, limit=200, only_confirmed=true для доказательной части. Ограничить число страниц на адрес (например, 5 = 1,000
переводов) и помечать узел как hub/truncated при превышении. Игнорировать type != Transfer и value = 0. Номер блока и caller добирать на этапе верификации. Кэш: закрытые окна (max_timestamp старше solidified-блока) хранить
бессрочно как append-only журнал по адресу с watermark; обновлять инкрементально от watermark. Клиент: token bucket ниже лимита, экспоненциальный backoff на 429/403, не хардкодить лимиты (читать из конфигурации).
COST: $0 на плане BASIC. Стандартное расследование (около 40 адресов) ≈ 60–100 запросов к v1; граф на 1,000 адресов ≈ 1,300 запросов. При ~100 расследованиях в месяц ≈ 10–55 тыс. запросов/мес, при ~1,000 ≈ 100–190 тыс. запросов/мес — в
15–30 раз ниже квоты 3 млн/мес. Custom plan понадобится только если большие графы станут нормой (более ~30–70 графов по 1,000 адресов в сутки); его цена не публикуется.
DATA QUALITY VERIFICATION: 1) Каждую страницу проверять на непрерывность: монотонность block_timestamp, отсутствие дублей (txid, from, to, value) между страницами. 2) Выборочная сверка того же окна с TronScan (в MVP — для каждого адреса на пути отчёта) и
алерт при расхождении наборов. 3) Сверка суммы переводов с balanceOf для адресов с небольшой историей. 4) Ежедневный canary: фиксированное окно фиксированного адреса должно давать тот же хеш набора.
RISKS: Один оператор для ключевой функции; лимиты и поведение меняются без предупреждения (10→3 QPS в декабре 2025, удаление search_internal в 2025); QPS для ключа не подтверждён; нет SLA; условия прямо допускают неполноту данных.
REPLACEABILITY: Интерфейс TransferHistoryProvider с реализациями TronGrid и TronScan (fallback); в фазе 2 — собственный индекс на SQD Portal или своём узле.
REJECTED ALTERNATIVES:
  - TronScan как основной источник истории: Страница максимум 50 строк (в 4 раза больше запросов), окно start+limit ≤ 10,000 с тихим усечением, штраф 120 с при превышении 3 rps без ключа, неопределённые условия коммерческого
  - использования.
  - eth_getLogs (JSON-RPC): Жёсткий предел 5,000 блоков на запрос: полная история одного адреса в одном направлении ≈ 17,417 запросов.
  - Self-hosted java-tron + event plugin: 3.5 TB SSD и 16–32 GB RAM только под узел, плюс собственный индекс 3.7 млрд переводов; сборка не поддерживается на Windows; у event-plugin нет лицензии.
  - Bitquery / Dune / BigQuery: Платные и/или пакетные: Bitquery Pro 90 req/min и неизвестная цена запроса в points; Dune и BigQuery не дают отклик в пределах 30 с; глубина и свежесть данных TRON не подтверждены.

### R2. NEED: Второй независимый источник для кросс-валидации и контекст по адресам
PRIMARY: TronScan API с собственным ключом (история TRC20 для сверки, /api/account/tag, /api/transaction-info) — при условии письменного подтверждения условий использования
RATIONALE: Независимый от TronGrid индексатор с более богатой строкой: номер блока, confirmed, contractRet, finalResult, имя вызванного метода, признаки контракта и публичные теги. На совпадающем окне расхождений с TronGrid не найдено,
поэтому любое будущее расхождение — значимый сигнал. Теги ('Binance-Hot 7', 'OKX Hot Wallet 8', 'MXC') дают отправную точку для атрибуции, но только как утверждение источника.
ARCHITECTURE NOTES: Использовать окна start_timestamp/end_timestamp и не полагаться на total/rangeTotal. Запрашивать limit=50 явно. Не выходить за start+limit = 10,000. Держать нагрузку ≤2 rps до выяснения квот ключа. Из /api/transaction-info НЕ
брать trc20TransferInfo как факт перевода: сначала проверять contractRet = SUCCESS и наличие события в receipt узла. Теги сохранять с source, датой проверки и confidence, обогащение тегами выполнять лениво и из локального кэша.
COST: $0 (ключ бесплатный). Стандартное расследование ≈ 40–80 запросов, граф на 1,000 адресов — до 1,000 запросов тегов при холодном кэше.
DATA QUALITY VERIFICATION: Сравнение множеств (txid, from, to, value) и block_timestamp с TronGrid по каждому адресу пути; при расхождении — арбитраж по receipt узла (gettransactioninfobyid). Теги проверять на независимом размеченном наборе и не повышать
confidence без второго источника.
RISKS: ToS 2022 года требует предварительного письменного согласия для сторонних приложений и исключает ряд юрисдикций; штраф 120 с при превышении лимита; тихое усечение выдачи; документация за Cloudflare. При юридическом отказе кросс-
валидация остаётся на receipts узла, а теги — на других источниках.
REPLACEABILITY: Для сверки — высокая (node-level receipts, Bitquery). Для тегов — низкая.
REJECTED ALTERNATIVES:
  - Bitquery как второй источник: Платно ($69–99/мес за коммерческую лицензию), 90 req/min, глубина истории TRON не подтверждена; оставить как арбитр после пробного периода.
  - Tatum REST: Бесплатный план — 100K lifetime credits и 3 req/s; эндпоинт истории TRC20 не подтверждён; независимость данных сомнительна.
  - OKLink / Footprint / Chainbase / GoldRush / Flipside: GoldRush не поддерживает TRON; Flipside продал бизнес данных SonarX; у остальных поддержка TRON и условия не подтверждены.

### R3. NEED: Первичные данные по TXID и верификация каждого факта отчёта (receipt, event logs, комиссии, caller)
PRIMARY: java-tron HTTP API (/walletsolidity/gettransactioninfobyid + /wallet/gettransactionbyid) у независимого от TRON оператора — Chainstack; горячий fallback — те же методы на TronGrid, keyless-резерв — PublicNode
RATIONALE: Receipt узла — первичный факт: blockNumber, blockTimeStamp, receipt.result, log[] с topics и data, fee, energy_usage, energy_fee, net_fee. Проверка факта у другого оператора, чем тот, кто дал историю, закрывает требование двух
независимых источников даже без TronScan. API одинаков у всех провайдеров, поэтому переключение — это смена base URL.
ARCHITECTURE NOTES: Факт считается подтверждённым, если в /walletsolidity receipt есть лог USDT-контракта с topic Transfer и теми же from/to/value, а receipt.result = SUCCESS. Для пакетной проверки многих переводов одного отправителя в окне до 5,000
блоков — один eth_getLogs с topic-фильтром по from. gettransactioninfobyblocknum даёт все receipts блока одним вызовом (309 за 0.5 с). Solidified-данные отстают примерно на 18–19 блоков (54–69 с) — в отчёт включать только их. Кэш
receipts по TXID бессрочный.
COST: Chainstack Developer $0 (3M RU/мес, 25 RPS) покрывает и 100, и 1,000 расследований в месяц (≈16 тыс. и ≈350 тыс. запросов соответственно). Для SLA и запаса по RPS — Growth $49/мес (20M RU, 250 RPS), то есть ≈$0.05 на расследование
при 1,000 в месяц.
DATA QUALITY VERIFICATION: Двойная проверка solidified receipt у второго оператора для выборки TXID; сверка числа Transfer-логов блока между eth_getLogs и gettransactioninfobyblocknum (в пробе 82 = 82); тест на известных неуспешных TXID (должны
отсутствовать логи).
RISKS: Chainstack не опробован вживую и TRON на бесплатном плане подтверждён только блогом провайдера; internal transactions у провайдеров могут отсутствовать; историческое состояние (balanceOf на прошлый блок) недоступно нигде.
REPLACEABILITY: Очень высокая: цепочка провайдеров в конфигурации.
REJECTED ALTERNATIVES:
  - Только TronGrid для discovery и верификации: Один оператор для обоих шагов — нет организационной независимости; оставить как fallback.
  - PublicNode как основной: Нет SLA и опубликованных лимитов, условия ограничивают автоматизированный сбор; подходит для разработки и аварийного резерва.
  - java-tron Lite FullNode: По умолчанию отключены gettransactionbyid/gettransactioninfobyid, история глубже 65,536 блоков отсутствует.
  - QuickNode / GetBlock / Ankr: Функционально эквивалентны, но либо нет постоянного бесплатного плана (QuickNode), либо лимиты не подтверждены первичным источником (GetBlock, Ankr); держать как запасные.

### R4. NEED: Статус блэклиста Tether для адресов графа
PRIMARY: Локальное зеркало событий AddedBlackList / RemovedBlackList / DestroyedBlackFunds (TronGrid /v1/contracts/{USDT}/events) + подтверждающий constant call isBlackListed(address) на solidity-узле в момент формирования отчёта
RATIONALE: События дают доказательство с TXID, блоком и временем — это позволяет сказать, был ли адрес заблокирован до или после конкретного перевода, чего не даёт текущий isBlackListed. Зеркало небольшое (порядка 7.8 тыс. записей) и снимает
нагрузку на API при обходе графа: проверка адреса становится локальной.
ARCHITECTURE NOTES: Bootstrap: постраничная выгрузка трёх типов событий (limit=200, order asc), далее опрос раз в несколько минут от последнего block_timestamp. Адрес из result._user конвертировать: 0x + 40 hex → префикс 41 → base58check. В отчёте
указывать: статус, TXID события, блок, время проверки, блок constant call. DestroyedBlackFunds учитывать как списание без перевода при сверке балансов.
COST: $0: около 100–150 запросов на первичную выгрузку, затем единицы запросов в час; 1 constant call на адрес, включённый в отчёт.
DATA QUALITY VERIFICATION: Сверка числа активных записей зеркала с total из TronScan; выборочная проверка isBlackListed для адресов из зеркала (должно быть true, если нет более позднего RemovedBlackList); регресс-тест на известном адресе
TAZgAu6wADSjXqV1gJE6AdFjPV1ptaEjLH (AddedBlackList 2026-10-13 13:49:54 UTC, tx d65209292728…).
RISKS: Событие RemovedBlackList вживую не запрашивалось; активность высокая (около 15 блокировок в день) — устаревшее зеркало даёт ложные 'чисто'; поэтому финальный constant call обязателен.
REPLACEABILITY: Высокая.
REJECTED ALTERNATIVES:
  - TronScan /api/stableCoin/blackList как единственный источник: Вторичные данные с неподтверждённой свежестью и неясной сортировкой; использовать для сверки полноты зеркала (total 7,838).
  - Только isBlackListed: Отдаёт лишь текущее состояние, без TXID и времени блокировки.
  - eth_getLogs по всей истории: Около 17 тыс. запросов на тип события из-за предела 5,000 блоков.

### R5. NEED: Контекст TRX, энергии и комиссий как следственная связь
PRIMARY: Receipt узла (fee, energy_usage, energy_fee, net_fee, energy_penalty_total) + TronGrid /v1/accounts/{addr}/transactions (Delegate/UnDelegateResourceContract, первый входящий TRX) + /wallet/getaccount
RATIONALE: В проверенном блоке 70 из 80 USDT-транзакций оплачены застейканной или делегированной энергией и только 12 — сжиганием TRX, то есть источник энергии — массовая и информативная связь. Список транзакций аккаунта на TronGrid показал
чужие DelegateResourceContract на адрес (в пробе 67 Delegate и 68 UnDelegate от одного провайдера энергии). Первый входящий TRX-перевод (активация) находится одним запросом с only_to=true и сортировкой asc.
ARCHITECTURE NOTES: Для каждого адреса пути: activation tx (кто и когда завёл TRX), набор провайдеров энергии (owner_address в Delegate), плательщик комиссии (owner_address транзакции). getdelegatedresourceaccountindexv2 показывает только текущие
делегирования и обычно пуст — опираться на историю транзакций. Рёбра 'gas funding' и 'energy delegation' хранить отдельным типом, не смешивая с потоком USDT. Фильтровать пылевые входящие (в пробе 1 и 3 SUN сразу после активации)
как спам/address poisoning.
COST: $0: 2–3 дополнительных запроса на адрес (активация, список транзакций, getaccount).
DATA QUALITY VERIFICATION: Сверка fee и energy-полей receipt с cost из TronScan transaction-info на выборке; проверка, что найденный провайдер энергии повторяется у связанных адресов (иначе не использовать как связь).
RISKS: Популярные сервисы аренды энергии и биржи обслуживают тысячи несвязанных адресов — связь слабая и требует пометки низкого confidence; полнота выдачи чужих Delegate-транзакций наблюдалась на одном адресе.
REPLACEABILITY: Высокая (те же данные доступны через TronScan и собственный узел).
REJECTED ALTERNATIVES:
  - TronScan /api/account/resourcev2 и accountv2: accountv2 без ключа отвечает 401, квоты ключа неизвестны; использовать как дополнение после получения ключа.
  - getdelegatedresourceaccountindexv2 как основной: Только текущее состояние; краткосрочная аренда энергии к моменту расследования уже снята.
  - Dune/BigQuery: Пакетные источники, не укладываются во время отклика.

### R6. NEED: Данные для распознавания свопов, лендинга, мостов и депозитных sweep-переводов
PRIMARY: Полный receipt транзакции (все log[] всех контрактов) + признак контракта у получателя + метки контрактов; для бирж — паттерн сбора депозитов на помеченный hot wallet
RATIONALE: Своп или вход в мост виден в одном receipt: Transfer USDT на адрес-контракт и события других контрактов в той же транзакции (в пробном блоке таких было 3 из 80). Депозитный sweep виден как серия переводов от множества адресов на
один помеченный кошелёк (в ленте USDT десятки переводов подряд на 'Binance-Hot 7'). Этого достаточно, чтобы детерминированно остановить трассировку на понятной границе.
ARCHITECTURE NOTES: Правила: 1) получатель — контракт (getcontract / toAddressIsContract) → классифицировать по реестру (SunSwap, JustLend, мосты) и по сигнатурам событий; 2) если в той же транзакции отправителю вернулся другой актив — своп,
продолжать по новому активу только при поддержке сети, иначе граница; 3) мост → граница с указанием контракта и TXID; 4) адрес с тегом биржи или с характерным sweep-паттерном → граница 'exchange deposit', неизвестные адреса биржей
не называть. Реестр адресов контрактов вести как данные с source и датой проверки.
COST: $0 сверх верификации: receipt уже запрашивается для каждого факта; плюс 1 запрос getcontract на новый адрес-контракт (кэшируется бессрочно).
DATA QUALITY VERIFICATION: Тестовые сценарии с известными свопами и мостами в наборе из 50+ кейсов; сверка классификации контракта с тегом TronScan и исходным ABI.
RISKS: Реестр адресов SunSwap, JustLend и мостов в этом аудите не собирался и не проверялся; internal transactions (движение TRX внутри контрактов) у публичных узлов отсутствуют — нужен TronGrid /v1/transactions/{txid}/internal-
transactions (вживую не проверен).
REPLACEABILITY: Высокая.
REJECTED ALTERNATIVES:
  - Bitquery DEX trades: Удобно, но платно и покрывает только DEX; оставить для пробного сравнения.
  - Allium bridges schema: Enterprise-цены, документация не прочитана.
  - Эвристики только по сумме и времени: Нарушают требование не делать выводов по косвенному сходству.

### R7. NEED: Клиентская библиотека
PRIMARY: Собственный тонкий async-клиент на httpx (TronGrid v1, TronScan, java-tron HTTP, JSON-RPC) + минимальные утилиты base58check/ABI; tronpy — только как вспомогательная зависимость с явно переданным ключом
RATIONALE: Ни одна библиотека не покрывает TronGrid /v1 и TronScan, а read-only клиент — это несколько десятков строк на эндпоинт. Свой клиент даёт то, что требуется платформе: логирование каждого вызова без ключей, лимитер, backoff, бюджет
запросов, кэш и цепочку провайдеров. В tronpy зашиты общие TronGrid-ключи по умолчанию — полагаться на это в коммерческом продукте нельзя.
ARCHITECTURE NOTES: Единый слой с редактированием секретов в логах (заголовок TRON-PRO-API-KEY и ключ в URL провайдера), счётчики запросов на расследование, конфигурируемые лимиты по провайдеру. Кодек адресов покрыть тестами на три формата: base58
T…, hex 41…, 0x… из событий.
COST: $0 лицензий; разовая разработка клиента.
DATA QUALITY VERIFICATION: Контрактные тесты на записанных ответах (включая 400 на limit=201, 429 с телом allowed_rps, тихое усечение TronScan) и ежедневный live-smoke на фиксированных TXID.
RISKS: Собственный код требует сопровождения при изменениях API (в 2025 TronGrid менял параметры трижды).
REPLACEABILITY: Полная (код свой).
REJECTED ALTERNATIVES:
  - tronpy как основной клиент: Нет /v1, нет JSON-RPC и gettransactioninfobyblocknum; встроенные общие ключи; статус Beta, последний коммит 2026-01-08.
  - TronWeb: JavaScript — второй рантайм для backend на Python без выгоды для чтения данных.
  - gotron-sdk / trident: Go и Java, ориентированы на подпись и отправку транзакций, которые платформе не нужны.

### R8. NEED: Производительность, кэш и тариф: 1,000 адресов за 5 минут и стоимость при 100 и 1,000 расследований в месяц
PRIMARY: TronGrid API key (BASIC) + независимый узел (Chainstack Developer, затем Growth $49/мес) + TronScan key; локальные кэши receipts, окон истории, зеркала блэклиста и тегов
RATIONALE: Расчёт на 1,000 адресов: история — 1,000 × ~1.3 страницы ≈ 1,300 запросов к TronGrid (4.3 rps в среднем за 300 с); узел — ~1,000 getaccount + ~1,000 пакетных проверок ≈ 2,000 запросов (6.7 rps); теги TronScan — до 1,000 (3.3 rps).
Без ключа TronGrid даёт максимум 3 rps × 300 с = 900 запросов и штрафы, то есть цель недостижима; с ключом достаточно даже при 15 rps. Узел на 25 RPS справляется с запасом. Узкое место — TronScan: 3 rps без ключа со штрафом 120 с,
поэтому теги должны идти из локальной базы, а недостающие — догружаться лениво и асинхронно.
ARCHITECTURE NOTES: Простая транзакция: ~10 запросов, менее 5 с. Стандартное расследование (около 40 адресов, ~60 рёбер): ≈60–100 запросов v1 + ≈170 к узлу + ≈55 к TronScan ≈ 285–330 запросов, при суммарных 10 rps — около 30 с. Параллелизм 5–10 на
провайдера (страница на 200 строк отвечает за 0.5–1.1 с). Бюджеты на расследование: максимум запросов, глубина, число адресов, страниц на адрес. При исчерпании дневной квоты TronGrid по документации скорость падает примерно до 1
rps — нужен счётчик квоты и переключение на fallback.
COST: ~100 расследований/мес: ≈35–55 тыс. запросов суммарно — $0 на бесплатных планах (опционально $49/мес за Chainstack Growth ради SLA). ~1,000 расследований/мес (например, 900 стандартных и 100 больших графов): TronGrid ≈185 тыс.,
узел ≈350 тыс., TronScan ≈150 тыс. запросов — $0–$49/мес, то есть ≤$0.05 переменных затрат на данные на одно расследование; остаток лимита $1 уходит на LLM. Неизвестные: цена TronGrid Custom plan и квоты ключа TronScan.
DATA QUALITY VERIFICATION: Нагрузочный прогон на синтетическом графе из 1,000 адресов с замером доли успешных ответов (цель ≥99%), числа 429 и времени; метрики по провайдерам в логах каждого расследования.
RISKS: QPS ключа TronGrid и квоты ключа TronScan не подтверждены; hub-адреса (биржи) могут потребовать сотни страниц — нужны жёсткие лимиты и граница на помеченных адресах; бесплатные планы могут измениться.
REPLACEABILITY: Высокая: провайдеры взаимозаменяемы на уровне конфигурации, кроме индексной истории TronGrid.
REJECTED ALTERNATIVES:
  - Работа без ключей: 3 rps у TronGrid (пауза 5 с) и 3 rps у TronScan (пауза 120 с) — граф на 1,000 адресов за 5 минут не строится.
  - Собственный узел и индекс уже в MVP: Не помещается на один скромный сервер; экономии на запросах нет, пока бесплатных квот хватает.
  - Платные индексированные API (Bitquery Scale, Dune Plus): $199–399/мес при том, что бесплатные квоты покрывают расчётную нагрузку.

### R9. NEED: Масштабирование после MVP: собственный индекс переводов USDT
PRIMARY: Пробный проект на SQD Portal (tron-mainnet) с squid-sdk tron-processor; запасной путь — собственный java-tron FullNode
RATIONALE: Когда зависимость от единственного индексного API TronGrid или его дневной квоты станет ограничением, собственный индекс по адресам снимает оба риска. SQD отдаёт блоки, транзакции, логи и internal transactions TRON с genesis без
эксплуатации узла на 3.5 TB, SDK под Apache-2.0 и работает на Node. Это решение не для MVP и требует пробы.
COST: SQD Portal: бесплатно для разработки, Starter $99/мес, Growth $499/мес; плюс хранилище под индекс. Собственный узел — стоимость сервера не оценивалась.
DATA QUALITY VERIFICATION: Сверка индекса с TronGrid и TronScan на случайных адресах и окнах; подсчёт Transfer-логов по блокам против eth_getLogs.
RISKS: Не проверено вживую; объём данных USDT (3.7 млрд переводов) требует продуманной схемы хранения; условия production-использования Portal не прочитаны.
REPLACEABILITY: Средняя.
REJECTED ALTERNATIVES:
  - java-tron FullNode + event plugin (MongoDB/Kafka): 3.5–4 TB NVMe, 32 GB RAM, эксплуатация узла; event framework V2 не отдаёт internal transactions; у event-plugin нет лицензии.
  - Google BigQuery Tron (Preview): Статус Preview без SLA, свежесть и схема не подтверждены; годится для разовой выгрузки, а не для живого индекса.
  - c0mm4nd/tronetl, substreams-tron, firehose-tron: tronetl без лицензии; у остальных 1–13 stars и нужен собственный источник блоков.

## LIVE PROBE FINDINGS
- Объём проб (2026-10-13 21:05–21:20 UTC, без ключей): api.trongrid.io — 37 запросов (включая один намеренный burst из 9 параллельных), apilist.tronscanapi.com — 32 (включая burst из 6), tron-rpc.publicnode.com — 17. Это немного
выше ориентира ~30 на хост; оба burst-теста вызвали 429, после чего запросы к хосту прекращались.
- TronGrid, форма ответа: GET /v1/accounts/{addr}/transactions/trc20?contract_address=TR7NHqjeKQxGTCi8q8ZY4pL8otSzgjLj6t&limit=200 → {data[], success, meta{at, fingerprint, links.next, page_size}}; элемент: transaction_id,
token_info{symbol, address, decimals, name}, block_timestamp (мс), from, to, type, value. Номера блока, признака confirmed и contractRet в элементе нет. Заголовков rate-limit в ответе 200 нет.
- TronGrid, размер страницы: limit=200 работает; limit=201 и limit=1000 → HTTP 400 с пустым телом. Сортировка по умолчанию desc; order_by=block_timestamp,asc работает.
- TronGrid, пагинация и окна: fingerprint-курсор, пересечение страниц 1 и 2 — 0 строк; min_timestamp/max_timestamp работают на горячем кошельке Binance-Hot 7 (TDqSquXBgUCLYvYC4XZgrprLK589dkhSCf): окно 2024-01-01 00:00–01:00 UTC
вернуло 200 строк за 1.03 с; первые переводы Binance-Hot 2 (TV6MuMXfmLbBqPZvBHdwFsDnQeVfnmiuSi) через asc — 2021-09-01, за 0.61 с. only_to, only_from, only_confirmed, only_unconfirmed работают.
- Свежесть: неподтверждённые строки TronGrid отстают примерно на 14 с (первая строка 21:06:24 при meta.at 21:06:38); only_confirmed=true — примерно на 69 с; /walletsolidity на PublicNode отставал от /wallet на 18 блоков (≈54 с).
TronScan показал блок 87084224 (21:06:06) через ~4 с после его времени, с confirmed=false.
- TronGrid без ключа, лимит: 9 параллельных запросов → 1×200 и 8×429 с телом 'request rate exceeded the allowed_rps(3), and the query server is suspended for 5 s'. Последовательные запросы с интервалом ~1.2 с не ограничивались.
- TronScan, форма ответа: GET /api/token_trc20/transfers?contract_address=&relatedAddress=&start=&limit=&start_timestamp=&end_timestamp= → {total, rangeTotal, contractInfo, token_transfers[]}; элемент: transaction_id, block,
block_ts, from_address, to_address, quant, confirmed, contractRet, finalResult, revert, event_type, approval_amount, trigger_info{method, methodName, parameter}, from/to_address_tag, fromAddressIsContract, toAddressIsContract,
riskTransaction.
- TronScan, ограничения выдачи: limit=100 и limit=200 вернули по 50 строк при HTTP 200 (тихое обрезание); total и rangeTotal для адресных запросов всегда 10000; start=9950 отдал 50 строк, start=10000 — 1 строку без ошибки за 5.1 с.
10,000 последних переводов Binance-Hot 7 покрывают всего около 2.6 часа. Глобальный rangeTotal по USDT — 3,728,710,923 перевода.
- TronScan без ключа: работают token_trc20/transfers, transaction-info, account/tag, stableCoin/blackList, transfer/trc20; /api/security/account/data и /api/accountv2 → 401. 6 параллельных запросов → 3×429 с телом 'allowed_rps(3) …
suspended for 120 s'.
- Сравнение двух источников на одном адресе и окне (Binance-Hot 7, 2026-10-01 00:00:00–00:04:00 UTC): TronGrid 308 строк за 2 страницы, TronScan 308 строк за 7 страниц; по ключу (txid, from, to, value) совпало 308 из 308,
расхождений по времени 0. Окно 2 минуты: 11 из 11. Расхождений в наборах переводов не найдено; различия только в составе полей и лимитах.
- Неуспешный перевод: TXID c74ec7aa69947f3c7e9e8f8c347211a56ee9986ea0297efd5d845f296dbf6cf6 (transfer 5,000 USDT, OUT_OF_ENERGY, блок 87084302) отсутствует в списке trc20 TronGrid и в token_trc20/transfers TronScan; виден в
/v1/accounts/{owner}/transactions с ret.contractRet=OUT_OF_ENERGY; receipt узла: result FAILED, receipt.result OUT_OF_ENERGY, массива log нет. Но TronScan /api/transaction-info для него возвращает trc20TransferInfo с 'переводом'
5,000 USDT при event_count=0 — источник фантомных переводов для наивного парсера. В выборке из 200 прямых вызовов USDT-контракта 5 были OUT_OF_ENERGY.
- transferFrom: TXID 9dc9c86282fd634d63c90de644049404e330b016148ccf1c0839902a96de1280 — вызывающий TKGiE3LRQ7R1fAy2ZxhkVsBkex16bePp1S переместил 69,300 USDT с TA2tbcGzWMjF2TwsRKJP3XCUCmLc6E8Dia на TDEzSnZ31pMM7hA8QWpaebkDhYv5vuNBtc.
В обоих источниках строка есть только в истории from и to, в истории вызывающего её нет; вызывающий виден в gettransactionbyid (owner_address) и в TronScan transaction-info (ownerAddress, trigger_info.methodName=transferFrom).
/v1/transactions/{txid}/events отдаёт адреса в виде 0x + 40 hex без префикса 41.
- Node API на PublicNode без ключа: gettransactionbyid, gettransactioninfobyid (fee 378000, blockNumber, blockTimeStamp, receipt{energy_usage 155325, net_fee, energy_penalty_total, result}, log[]), те же методы на /walletsolidity,
gettransactioninfobyblocknum (309 receipts блока 87084303 за 0.5 с), triggerconstantcontract isBlackListed(address) → нули (false), balanceOf(Binance-Hot 7) → 896,361,630.80 USDT. internal_transactions в receipts отсутствуют (в
config.conf java-tron vm.saveInternalTx = false по умолчанию).
- JSON-RPC на PublicNode: eth_getLogs по блоку 87084303 с адресом USDT и topic Transfer → 82 лога, ровно столько же Transfer-логов USDT в gettransactioninfobyblocknum; фильтр по topic отправителя на 4,000 блоков отработал; на 20,000
блоков → error -32602 'exceed max block range: 5000'. В логах есть поле blockTimestamp.
- Блэклист: TronGrid /v1/contracts/TR7…/events?event_name=AddedBlackList&limit=200 → 200 событий за 2026-09-30 14:25 … 2026-10-13 13:49 UTC (около 15 в день), поля block_number, block_timestamp, transaction_id, result._user;
DestroyedBlackFunds → 200 событий за 2026-05-26 … 2026-10-09 с _blackListedUser и _balance (пример: 517,500 USDT, tx 9e22c83c…). TronScan /api/stableCoin/blackList требует limit в диапазоне [20,100] и сообщает total 7838; записи
содержат blackAddress, num, time, transHash.
- Энергия и комиссии: в блоке 87084303 из 80 транзакций с USDT-логом 70 имели energy_usage > 0 (стейк или делегирование), 12 — energy_fee > 0 (сжигание TRX), 2 — origin_energy_usage > 0. TronGrid
/v1/accounts/TKGiE3…/transactions?limit=200 вернул 67 DelegateResourceContract и 68 UnDelegateResourceContract от стороннего адреса (TCqZkyExhEMjaLQXjy9sUqJ43qinqUbYnP, resource ENERGY) и 65 TriggerSmartContract;
getdelegatedresourceaccountindexv2 для того же адреса пуст.
- Активация адреса: /v1/accounts/{addr}/transactions?only_to=true&order_by=block_timestamp,asc&limit=3 для TKGiE3… → первый входящий TransferContract 3,700 TRX от TXrf49JymwkT7PU47qGy2i7M2RzUE6aAa6 в 2025-01-14 15:23:21 UTC
(create_time аккаунта 15:23:18), затем пылевые переводы 1 и 3 SUN от других адресов через 3 и 12 секунд.
- Данные для свопов: в том же блоке 3 из 80 USDT-транзакций содержали в одном receipt логи других контрактов (пример: fb7b3a2433596693d191d3211147a58e849bfeef24ac1a02d85118166cf0e877 — Transfer USDT и событие контракта
TXtEs6t2oUWQsNos7m68gbHdE9Q5n6x2oN). TronScan отдаёт теги контрактов в contractInfo (например, 'USDT Token') и флаги from/toAddressIsContract.
- Сайт TronGrid (bundle.29481f13.js): планы BASIC — price 0, 100,000 Requests / Day, 3 API Keys; TRIAL — 500,000; Custom — по заявке; Developer/Team/Business с ценой '???'. Changelog: v1.10.0 (December 23) — keyless QPS с 10 до 3;
v1.7.0 (2025-08-15) — удалён search_internal; v1.8.0 и v1.9.0 — отдельные internal-transactions эндпоинты; v1.11.0 (March 9) — MCP API. Terms of Service: Last updated September 24, 2026.
- Чтение кода: java-tron README — FullNode 8 CPU / 16–32 GB / 3.5 TB (Lite 200 GB), сборка на Windows не поддерживается; config.conf — jsonrpc.maxBlockRange = 5000, vm.saveInternalTx = false, event.subscribe.startSyncBlockNum только
при version = 1; LiteFnQueryHttpFilter.java — в фильтре gettransactionbyid, gettransactioninfobyid, getblockbynum, gettransactioninfobyblocknum. tronpy/providers/http.py — встроенный список из 6 общих TronGrid-ключей по умолчанию;
tronpy/tron.py — ни одного обращения к /v1.

## CANDIDATES (full audit cards)

### [RECOMMENDED] TronGrid v1 indexed REST API (api.trongrid.io/v1)
NEED: История TRC20-переводов по адресу с полной обратной пагинацией (основной discovery-источник), события контракта, транзакции аккаунта
KIND: public API
URL: https://api.trongrid.io
LICENSE: Проприетарный сервис; TronGrid Terms of Service (Last updated: September 24, 2026)
COMMERCIAL USE: Прямого запрета коммерческого использования в ToS нет. Запрещено: 'resell, sublicense or provide unauthorized third-party access to the Services or API keys', обход лимитов. Продавать отчёты/аналитику можно, проксировать сырой API
клиентам нельзя. Сервис 'as is'; в ToS прямо сказано, что blockchain data 'may be incomplete, delayed or inaccurate'. Право Сингапура, арбитраж SIAC.
PROJECT STATE: Действующий сервис экосистемы TRON. Changelog на сайте: v1.11.0 (March 9, MCP API), v1.10.0 (December 23 — keyless QPS 10→3), v1.7.0–v1.9.0 (Aug–Sep 2025 — переработка internal transactions). Документация rate-limits обновлена
2026-07-21.
CLAIMED VS ACTUAL: 1) Официальная страница rate-limits НЕ содержит чисел ('Do not hard-code fixed limits'), другая официальная страница (rate-limits-1) пишет 'such as 30 requests per second' и 'such as 1 request per second' после исчерпания дневной
квоты; сторонние обзоры пишут 15 QPS и блокировку 403 на 30 с. Факт (живая проба без ключа): allowed_rps(3), HTTP 429, блокировка 5 с. 2) Страница pricing не рендерится без JS; в bundle сайта зашиты планы BASIC 100,000
Requests/Day + 3 API Keys (цена 0), TRIAL 500,000/day, Custom; у Developer/Team/Business цена '???' — публичных платных цен нет, хотя ToS уже описывает подписки через Stripe. 3) В ответе trc20 нет номера блока и признака confirmed
— их надо добирать через receipt.
CAPABILITIES: GET /v1/accounts/{addr}/transactions/trc20 (фильтры contract_address, only_to/only_from, only_confirmed/only_unconfirmed, min_timestamp/max_timestamp, order_by asc/desc, limit<=200, fingerprint); /v1/accounts/{addr}/transactions
(включая чужие Delegate/UnDelegateResource на адрес); /v1/accounts/{addr}; /v1/contracts/{c}/events?event_name=; /v1/contracts/{c}/transactions; /v1/transactions/{txid}/events; /v1/accounts|transactions|contracts/.../internal-
transactions. Тот же хост отдаёт /wallet, /walletsolidity, /jsonrpc.
INFRA: Только HTTPS-клиент; API key в заголовке TRON-PRO-API-KEY (хранить в секретах, не логировать).
PRICING/LIMITS: Без ключа: 3 rps, при превышении 429 и пауза 5 с (проверено). С ключом (BASIC, бесплатно): 100,000 запросов/день, 3 ключа на аккаунт (из bundle сайта https://www.trongrid.io/pricing); QPS с ключом не проверен (15 или 30 по разным
источникам). Сверх квоты — Custom plan по заявке (цена не публикуется). Размер страницы максимум 200; limit=201 → HTTP 400 с пустым телом.
RISKS: Единственный публичный источник с индексом 'адрес → TRC20-переводы' и окном по времени; зависимость от одного оператора. Лимиты меняются без версии (10→3 QPS в декабре 2025). Нет SLA на бесплатном плане. В списке trc20 нет block
number/contractRet; адреса в /events в формате 0x без префикса 41. Неуспешные вызовы в списке отсутствуют (это плюс), transferFrom показывается от имени владельца токенов — вызывающий (spender) виден только в gettransactionbyid.
REPLACEABILITY: Средняя: прямого аналога по API нет (у нод-провайдеров индексных /v1 эндпоинтов нет). Замена — TronScan (50 строк/страница, окно 10,000) или собственный индекс (SQD/Bitquery/свой узел). Изолировать за интерфейсом
TransferHistoryProvider.
HOW VERIFIED: API call made (≈37 keyless-запросов: пагинация, фильтры, burst-тест), чтение официальной документации, чтение JS-bundle сайта trongrid.io (планы, changelog, ToS)
CONFIDENCE: high
EVIDENCE: https://api.trongrid.io/v1/accounts/TDqSquXBgUCLYvYC4XZgrprLK589dkhSCf/transactions/trc20?contract_address=TR7NHqjeKQxGTCi8q8ZY4pL8otSzgjLj6t&limit=200 | https://developers.tron.network/reference/get-trc20-transaction-info-by-account-address | https://developers.tron.network/reference/rate-limits | https://developers.tron.network/reference/rate-limits-1 | https://www.trongrid.io/pricing | https://www.trongrid.io/bundle.29481f13.js

### [RECOMMENDED] TronScan API (apilist.tronscanapi.com)
NEED: Второй независимый индексатор для кросс-валидации истории TRC20, детали транзакции одним вызовом, публичные теги адресов, список блэклиста стейблкоинов
KIND: public API
URL: https://apilist.tronscanapi.com
LICENSE: Проприетарный сервис; TRONSCAN Terms of Service (Last updated: January 4, 2022)
COMMERCIAL USE: Под вопросом, нужен письменный ответ TronScan. В ToS: запрет 'Develop any third-party applications that interact with our Services without our prior written consent'; данные и материалы — собственность компании, 'Excerpts and
links may be used, provided that full and clear credit is given to TRONSCAN.io'; eligibility исключает резидентов/организации материкового Китая, Тайваня, Гонконга, США и Сингапура. Отдельных API-условий о
кэшировании/редистрибуции не найдено.
PROJECT STATE: Действующий официальный explorer TRON. Документация docs.tronscan.org обновлена в 2026 (страницы от March 16 и June 4, 2026), есть llms.txt, MCP, CLI. Объявления 2025 года: API key становится обязательным (30.06.2025, уточнение
28.07.2025, с 31.08.2025 QPS без ключа не гарантируется).
CLAIMED VS ACTUAL: 1) Документация: 'An API Key is required for calling Mainnet endpoints'. Факт: большинство эндпоинтов отвечают без ключа на 3 rps; 401 дают /api/security/account/data и /api/accountv2. 2) limit выше 50 молча обрезается до 50 при
HTTP 200 (limit=100 и 200 вернули 50 строк). 3) total/rangeTotal для адресного запроса всегда 10000 — это потолок окна, а не число переводов; start=10000 возвращает 1 строку без ошибки (тихое усечение). 4) /api/transaction-info
для НЕУСПЕШНОЙ транзакции (contractRet=OUT_OF_ENERGY, event_count=0) всё равно заполняет trc20TransferInfo намерением перевода — наивный парсер создаст фантомный перевод. 5) Числовые лимиты для ключа в документации не указаны.
CAPABILITIES: /api/token_trc20/transfers (relatedAddress, contract_address, start/limit, start_timestamp/end_timestamp, confirm): block, block_ts, confirmed, contractRet, finalResult, revert, trigger_info.methodName, from/to_address_tag,
from/toAddressIsContract, riskTransaction; /api/transaction-info?hash= (cost: energy_fee, net_fee, energy_usage, energy_penalty_total; ownerAddress; trc20TransferInfo; contractInfo с тегами; srConfirmList); /api/account/tag
(publicTag, например 'Binance-Hot 7'); /api/stableCoin/blackList; /api/transfer/trc20; /api/internal-transaction; /api/account/resourcev2; security-эндпоинты.
INFRA: HTTPS-клиент; заголовок TRON-PRO-API-KEY.
PRICING/LIMITS: Без ключа (проверено): allowed_rps(3), при превышении HTTP 429 и блокировка на 120 с. Страница ≤50 строк, окно start+limit ≤10,000 (обходится через start_timestamp/end_timestamp). /api/stableCoin/blackList: limit в диапазоне
[20,100]. Ключ бесплатный (регистрация на tronscan.org), квоты для ключа не проверены; платных тарифов в документации не найдено.
RISKS: Юридическая неопределённость коммерческого использования и переиспользования тегов; 20 запросов на 1,000 переводов против 5 у TronGrid; жёсткая штрафная пауза 120 с; документация за Cloudflare-challenge (читается нестабильно);
оператор из той же экосистемы TRON, что и TronGrid (индексаторы разные, но организационная независимость неполная). Теги — утверждение TronScan, а не первичный факт: хранить с source=TronScan, датой проверки и confidence.
REPLACEABILITY: Высокая для кросс-валидации (заменяется node-level receipts и Bitquery), низкая для публичных тегов (уникальные данные).
HOW VERIFIED: API call made (≈32 keyless-запроса, включая burst-тест), чтение docs.tronscan.org (llms.txt, common-network-auth, api-keys), чтение PDF Terms of Service, search snippets для объявлений support.tronscan.org (сама страница отдала
403)
CONFIDENCE: high
EVIDENCE: https://apilist.tronscanapi.com/api/token_trc20/transfers?limit=50&start=0&contract_address=TR7NHqjeKQxGTCi8q8ZY4pL8otSzgjLj6t | https://docs.tronscan.org/llms.txt | https://docs.tronscan.org/en/api/common-network-auth | https://docs.tronscan.org/en/api/api-keys | https://static.tronscan.org/pdf/TRONSCAN_Terms_of_Service.pdf | https://support.tronscan.org/hc/en-us/articles/49272903085465-Follow-up-Announcement-on-the-Mandatory-Requirement-of-API-Key-for-All-Requests

### [RECOMMENDED] java-tron HTTP API (/wallet, /walletsolidity) у независимого оператора — Chainstack TRON
NEED: Первичные данные по TXID (транзакция, receipt, event logs, комиссии/энергия), constant calls (isBlackListed, balanceOf), верификация каждого факта отчёта независимо от индексатора
KIND: commercial SaaS
URL: https://chainstack.com/pricing/
LICENSE: Проприетарный сервис (узлы java-tron, LGPL-3.0)
COMMERCIAL USE: Коммерческий RPC-провайдер, платные планы рассчитаны на production. Текст ToS не читался — см. not_verified.
PROJECT STATE: Действующий провайдер; обзор TRON-провайдеров обновлён 2026-08-21; документация TRON tooling актуальна.
CLAIMED VS ACTUAL: Заявлен 'archive mode', но eth_call/eth_getBalance/triggerconstantcontract работают только на latest — исторический balanceOf/isBlackListed на прошлый блок получить нельзя (исключение: /wallet/getaccountbalance для TRX). На
странице pricing TRON не упомянут ни в одном плане; о Developer-плане для TRON сказано только в блоге Chainstack.
CAPABILITIES: Один endpoint отдаёт /wallet, /walletsolidity, /jsonrpc и gRPC. По документации узлы TRON работают в archive mode (полная история блоков и транзакций, но не историческое состояние). Нет TronGrid-подобных /v1 индексных эндпоинтов и
event plugin, нет WebSocket-подписок.
INFRA: HTTPS-клиент, ключ в URL endpoint (не логировать URL целиком).
PRICING/LIMITS: Developer $0: 3,000,000 RU/мес, 25 RPS, без archive; Growth $49/мес: 20M RU, 250 RPS; Pro $199: 80M RU, 400 RPS; Business $499: 200M RU, 600 RPS. Overage $20/$15/$12.5/$10 за 1M RU. Full node запрос = 1 RU, archive = 2 RU.
Unlimited Node add-on от $149/мес (25 RPS).
RISKS: Не опробован вживую (нужен аккаунт). Internal transactions зависят от настройки узла (в java-tron по умолчанию vm.saveInternalTx=false). Нет исторического состояния.
REPLACEABILITY: Очень высокая: тот же java-tron HTTP API отдают TronGrid, QuickNode, GetBlock, Ankr, Tatum, PublicNode, собственный узел — меняется только base URL.
HOW VERIFIED: docs only (pricing, TRON tooling); идентичный API проверен живыми вызовами на tron-rpc.publicnode.com (17 запросов) и api.trongrid.io
CONFIDENCE: medium
EVIDENCE: https://chainstack.com/pricing/ | https://docs.chainstack.com/docs/tron-tooling | https://chainstack.com/best-tron-rpc-providers-2026/

### [ALTERNATIVE] TRON JSON-RPC (eth_getLogs и др., /jsonrpc)
NEED: Батч-проверка Transfer-логов USDT по узкому диапазону блоков; совместимость с EVM-инструментами при расширении на другие сети
KIND: standard
URL: https://developers.tron.network/reference/json-rpc-api-overview
LICENSE: Часть java-tron (LGPL-3.0)
COMMERCIAL USE: Определяется провайдером узла
PROJECT STATE: Поддерживается в java-tron (последний релиз GreatVoyage-v4.8.2.3 от 2026-09-30).
CLAIMED VS ACTUAL: Позиционируется как Ethereum-совместимый, но диапазон eth_getLogs жёстко ограничен: проба на 20,000 блоков вернула error -32602 'exceed max block range: 5000' (совпадает с jsonrpc.maxBlockRange = 5000 в config.conf java-tron). Нет
eth_sendRawTransaction и исторического состояния.
CAPABILITIES: eth_getLogs с фильтром address + topics (Transfer + indexed from/to), eth_getTransactionReceipt, eth_blockNumber, eth_call (только latest). В логах есть blockTimestamp.
PRICING/LIMITS: maxBlockRange 5000 блоков (≈4.2 часа), maxSubTopics 1000, maxBatchSize 100, maxResponseSize 26,214,400 байт (config.conf java-tron). Полная история одного адреса в одном направлении = 87,084,356 / 5,000 ≈ 17,417 запросов —
непригодно как основной источник истории.
RISKS: Адреса в 0x-формате без префикса 41 (нужна конвертация); на некоторых провайдерах лимиты могут отличаться.
REPLACEABILITY: Высокая (стандартный интерфейс у всех провайдеров).
HOW VERIFIED: API call made (PublicNode: eth_blockNumber, eth_getLogs на 1 блок = 82 лога, совпало с 82 Transfer-логами из gettransactioninfobyblocknum; диапазон 4,000 блоков OK, 20,000 → ошибка), code read (java-tron config.conf)
CONFIDENCE: high
EVIDENCE: https://tron-rpc.publicnode.com/jsonrpc | https://github.com/tronprotocol/java-tron/blob/master/framework/src/main/resources/config.conf

### [ALTERNATIVE] PublicNode (tron-rpc.publicnode.com, Allnodes)
NEED: Keyless fallback для node-level вызовов в разработке и при отказе основного провайдера
KIND: public API
URL: https://tron-rpc.publicnode.com
LICENSE: Проприетарный бесплатный сервис; PublicNode Terms
COMMERCIAL USE: Неясно: лицензия 'non-exclusive, limited, non-transferable, freely revocable'; запрещены scraping/data mining и 'commercial solicitation'; SLA нет, сервис 'AS IS'. Для production коммерческого SaaS не подходит как основной.
PROJECT STATE: Работает (проверено живыми вызовами 2026-10-13).
CLAIMED VS ACTUAL: none found (заявленное в ToS отсутствие гарантий соответствует бесплатному характеру сервиса); internal_transactions в receipts не возвращаются.
CAPABILITIES: /wallet/*, /walletsolidity/*, /jsonrpc без ключа: gettransactionbyid, gettransactioninfobyid, gettransactioninfobyblocknum, triggerconstantcontract, getaccount, getaccountresource, getdelegatedresourceaccountindexv2, eth_getLogs.
PRICING/LIMITS: Бесплатно, лимиты не опубликованы; rate-limit заголовков в ответах нет. Задержки 0.3–0.9 с на запрос.
RISKS: Нет SLA и опубликованных лимитов, возможна блокировка без предупреждения; условия ограничивают автоматизированный сбор данных.
REPLACEABILITY: Очень высокая.
HOW VERIFIED: API call made (17 запросов), чтение terms
CONFIDENCE: high
EVIDENCE: https://tron-rpc.publicnode.com/wallet/getnowblock | https://www.publicnode.com/terms

### [ALTERNATIVE] QuickNode TRON
NEED: Node-level данные по TXID (альтернативный провайдер)
KIND: commercial SaaS
URL: https://www.quicknode.com/docs/tron
LICENSE: Проприетарный сервис
COMMERCIAL USE: Коммерческий провайдер; ToS не читался
PROJECT STATE: Действующий; TRON mainnet и Nile, archive = Yes по таблице сетей в документации.
CLAIMED VS ACTUAL: Страница pricing не упоминает TRON и множители API credits для TRON-методов — реальная стоимость вызова не подтверждена.
CAPABILITIES: JSON-RPC, /wallet, /walletsolidity, gRPC. Индексной истории TRC20 по адресу нет.
PRICING/LIMITS: Free trial $0: 10M credits, 15 RPS; Build $49/мес: 80M credits, 50 RPS; Accelerate $249: 450M, 125 RPS; Scale $499: 950M, 250 RPS; overage $0.62–$0.50 за 1M credits.
RISKS: Постоянного бесплатного плана нет (trial); кредитная стоимость TRON-вызовов не проверена.
REPLACEABILITY: Очень высокая.
HOW VERIFIED: docs only (pricing page, docs/tron)
CONFIDENCE: medium
EVIDENCE: https://www.quicknode.com/pricing | https://www.quicknode.com/docs/tron

### [ALTERNATIVE] GetBlock TRON
NEED: Node-level данные по TXID (альтернативный провайдер)
KIND: commercial SaaS
URL: https://docs.getblock.io/api-reference/tron-trx
LICENSE: Проприетарный сервис
COMMERCIAL USE: Коммерческий провайдер; ToS не читался
PROJECT STATE: Действующий; документация TRON доступна.
CLAIMED VS ACTUAL: Противоречивые данные о бесплатном плане: документация (по поисковому сниппету) — 50,000 CU/день и 20 RPS, блог 2025 — 5 RPS и 5,000 запросов/день. В документации TRON таблица сетей и таблица интерфейсов расходятся по JSON-RPC
Solidity.
CAPABILITIES: REST Fullnode /wallet, REST Solidity /walletsolidity, JSON-RPC /jsonrpc, gRPC. Индексной истории TRC20 нет; archive для TRON в документации не раскрыт.
PRICING/LIMITS: Free: 50,000 CU/день, 2 access tokens (RPS 5 или 20 — не подтверждено); Starter $49/мес: 90M CU, 250 RPS (сниппет); Pro $399/мес при годовой оплате: 800 RPS, $0.40 за 1M CU (страница pricing); dedicated от $1,000.
RISKS: Числа бесплатного плана не подтверждены первичным источником.
REPLACEABILITY: Очень высокая.
HOW VERIFIED: docs only + search snippet only для чисел бесплатного плана
CONFIDENCE: low
EVIDENCE: https://getblock.io/pricing/ | https://docs.getblock.io/api-reference/tron-trx | https://docs.getblock.io/getting-started/plans-and-limits/cu-and-rate-limits

### [ALTERNATIVE] Ankr TRON RPC
NEED: Node-level данные по TXID (альтернативный провайдер)
KIND: commercial SaaS
URL: https://www.ankr.com/docs/rpc-service/chains/chains-api/tron/
LICENSE: Проприетарный сервис
COMMERCIAL USE: Коммерческий провайдер; ToS не читался
PROJECT STATE: Действующий; документация TRON доступна.
CLAIMED VS ACTUAL: Документация привязывает '26 methods … with a free demo key' только к JSON-RPC; доступность REST на бесплатном уровне не указана. Обзор Chainstack противоречит сам себе по WebSocket для TRON.
CAPABILITIES: JSON-RPC (26 методов, включая eth_getLogs) и REST /wallet, /walletsolidity. Индексной истории TRC20 нет.
PRICING/LIMITS: По обзору конкурента (Chainstack, обновлён 2026-08-21): free 200M credits/мес (~30 RPS), Premium $0.10 за 1M credits (≈$20 за 1M запросов при 200 credits/вызов). Первичным источником не подтверждено.
RISKS: Цены и лимиты известны только из стороннего обзора.
REPLACEABILITY: Очень высокая.
HOW VERIFIED: docs only (страница методов) + search snippet only (цены из обзора Chainstack)
CONFIDENCE: low
EVIDENCE: https://www.ankr.com/docs/rpc-service/chains/chains-api/tron/ | https://chainstack.com/best-tron-rpc-providers-2026/

### [REJECTED] NOWNodes TRON (RPC + Blockbook)
NEED: Node-level данные и альтернативный индекс адресов (Blockbook)
KIND: commercial SaaS
URL: https://nownodes.io/nodes/tron-trx
LICENSE: Проприетарный сервис
COMMERCIAL USE: Не проверено (ToS не читался)
PROJECT STATE: Действующий; страница TRON заявляет поддержку 'TRON RPC and BlockBook APIs'.
CLAIMED VS ACTUAL: Страница pricing не показывает цен и RPS (только объёмы запросов); заявленные 'no predefined RPS limits' и '99,95% Uptime' ничем не подтверждены. Цена €20/мес за Pro известна только со стороннего каталога.
CAPABILITIES: RPC и Blockbook (адреса, транзакции, балансы) — детали TRC20-истории и endpoint URL на странице не раскрыты.
PRICING/LIMITS: Start (free): 100,000 запросов/мес, 1 API key; Pro: 1,000,000/мес, 3 ключа; Pro Plus: 10M; overage €5 за 100k на Pro Plus. Цены планов на странице не указаны.
RISKS: Непрозрачное ценообразование; покрытие TRC20 в Blockbook не подтверждено.
REPLACEABILITY: Высокая.
HOW VERIFIED: docs only (pricing, страница TRON) + search snippet only для цен
CONFIDENCE: low
EVIDENCE: https://nownodes.io/pricing | https://nownodes.io/nodes/tron-trx

### [REJECTED] dRPC TRON
NEED: Node-level данные (альтернативный провайдер)
KIND: commercial SaaS
URL: https://drpc.org/chainlist/tron-mainnet-rpc
LICENSE: Проприетарный сервис
COMMERCIAL USE: Не проверено
PROJECT STATE: Страницы pricing и chainlist рендерятся только через JS — содержимое получить не удалось.
CLAIMED VS ACTUAL: Проверить не удалось; по обзору Chainstack — free tier на публичных узлах, платно от $10/мес и $6 за 1M запросов.
PRICING/LIMITS: Не проверено первичным источником.
RISKS: Нет подтверждённых данных о TRON-интерфейсах и лимитах.
HOW VERIFIED: search snippet only (обзор Chainstack); собственные страницы dRPC не прочитаны
CONFIDENCE: low
EVIDENCE: https://drpc.org/pricing | https://chainstack.com/best-tron-rpc-providers-2026/

### [REJECTED] Tatum TRON (RPC gateway + REST)
NEED: Node-level данные и обёртка над историей TRC20
KIND: commercial SaaS
URL: https://docs.tatum.io/reference/rpc-tron
LICENSE: Проприетарный сервис
COMMERCIAL USE: Не проверено (на странице pricing не указано)
PROJECT STATE: Действующий; gateway tron-mainnet.gateway.tatum.io отдаёт /jsonrpc, /wallet, /walletsolidity.
CLAIMED VS ACTUAL: 'Free Plans forever', но бесплатный план — это 100K lifetime credits и 3 req/s, то есть фактически пробный. Страница эндпоинта истории TRC20 по адресу вернула 404 — существование и параметры не подтверждены.
PRICING/LIMITS: Free: 2 API keys, 3 req/s, 100K lifetime credits. Dedicated API keys: $99/мес за 10 RPS, $249 за 25 RPS, $509 за 50 RPS. Цены базовых планов на странице не показаны.
RISKS: Бесплатный уровень непригоден для production; обёртка не добавляет независимости данных.
HOW VERIFIED: docs only
CONFIDENCE: medium
EVIDENCE: https://tatum.io/pricing | https://docs.tatum.io/reference/rpc-tron

### [REJECTED] Alchemy TRON API
NEED: Node-level данные (альтернативный провайдер)
KIND: commercial SaaS
URL: https://www.alchemy.com/docs/tron/tron-api-overview
LICENSE: Проприетарный сервис
COMMERCIAL USE: Не проверено
PROJECT STATE: Документация TRON существует.
CLAIMED VS ACTUAL: Обзорная страница перечисляет только eth_*/net_*/web3_* методы; нативные /wallet, /walletsolidity и индекс переводов (аналог alchemy_getAssetTransfers) для TRON не упомянуты.
PRICING/LIMITS: Не проверено для TRON.
RISKS: Без нативного API не получить energy/net receipt-поля TRON в привычном виде и triggerconstantcontract.
HOW VERIFIED: docs only (одна страница)
CONFIDENCE: low
EVIDENCE: https://www.alchemy.com/docs/tron/tron-api-overview.md

### [REJECTED] Self-hosted java-tron FullNode + event plugin (Kafka/MongoDB)
NEED: Собственный независимый источник первичных данных и собственный индекс переводов
KIND: open-source
URL: https://github.com/tronprotocol/java-tron
LICENSE: java-tron: LGPL-3.0. event-plugin: файла лицензии НЕТ (GitHub API: license = none)
COMMERCIAL USE: java-tron под LGPL-3.0 можно запускать в коммерческом сервисе без раскрытия собственного кода (запуск немодифицированного узла). У event-plugin лицензия не указана — юридически неопределённо, нужен запрос к tronprotocol.
PROJECT STATE: java-tron: 4,170 stars, 71 open issue, последний push 2026-10-13, релиз GreatVoyage-v4.8.2.3 от 2026-09-30, CI workflows (pr-build, integration-test-single-node, codeql и др.). event-plugin: 49 stars, v3.0.0 от 2026-07-03,
последний push 2026-07-03.
CLAIMED VS ACTUAL: 1) README: сборка на Windows не поддерживается (нужен Linux/macOS или Docker). 2) Event framework V2 не отдаёт internal transactions (internalTransactionList пуст) — для них нужен V1 без исторического replay. 3) vm.saveInternalTx
= false по умолчанию. 4) Узел сам по себе не даёт индекса 'адрес → переводы': его надо строить из потока событий (у USDT 3.73 млрд переводов по счётчику TronScan).
CAPABILITIES: Полный /wallet, /walletsolidity, /jsonrpc, gRPC; event subscribe V2 (version = 1) с историческим replay через startSyncBlockNum; триггеры block, transaction, contractevent, contractlog, solidity, solidityevent, soliditylog; фильтр
по contractAddress/contractTopic.
INFRA: Linux или Docker, JDK по архитектуре CPU, 3.5–4 TB NVMe, MongoDB или Kafka, синхронизация/снапшот, эксплуатация и мониторинг.
PRICING/LIMITS: Лицензионной платы нет. Железо для mainnet по README: минимум 8 CPU/16 GB RAM, стабильно 8 CPU/32 GB, диск 3.5 TB SSD (Full), рекомендовано 16+ CPU/32 GB+/4 TB. Плюс хранилище под индекс. Стоимость сервера не оценивалась.
RISKS: Не укладывается в 'single modest server' и ресурсы маленькой команды; долгий bootstrap; собственная ответственность за полноту индекса.
REPLACEABILITY: Интерфейс тот же, что у провайдеров — можно подключить позже без переписывания клиента.
HOW VERIFIED: gh api (метаданные, релизы, workflows), code read (README.md, config.conf), чтение официальной документации event subscription
CONFIDENCE: high
EVIDENCE: https://github.com/tronprotocol/java-tron | https://github.com/tronprotocol/java-tron/blob/master/README.md | https://github.com/tronprotocol/event-plugin | https://tronprotocol.github.io/documentation-en/architecture/event/

### [REJECTED] java-tron Lite FullNode
NEED: Дешёвый собственный узел для проверки транзакций
KIND: open-source
URL: https://tronprotocol.github.io/documentation-en/using_javatron/litefullnode/
LICENSE: LGPL-3.0
COMMERCIAL USE: Разрешено (запуск узла)
PROJECT STATE: Часть java-tron (v4.8.2.3 от 2026-09-30).
CLAIMED VS ACTUAL: 200 GB вместо 3.5 TB, но снапшот содержит только последнее состояние и историю последних 65,536 блоков; запросы истории по умолчанию отключены. В LiteFnQueryHttpFilter.java в фильтр попадают /wallet и /walletsolidity
gettransactionbyid, gettransactioninfobyid, getblockbynum, gettransactioninfobyblocknum. Опция node.openHistoryQueryWhenLiteFN = true открывает API, но данные до высоты снапшота всё равно недоступны.
PRICING/LIMITS: Железо: 8 CPU, 16 GB RAM, 200 GB SSD (README).
RISKS: Непригоден для расследований: кражи обычно старше окна снапшота, TXID не найдётся. Годится только для constant calls (isBlackListed, balanceOf) и свежих блоков.
HOW VERIFIED: docs read + code read (LiteFnQueryHttpFilter.java, README.md)
CONFIDENCE: high
EVIDENCE: https://tronprotocol.github.io/documentation-en/using_javatron/litefullnode/ | https://github.com/tronprotocol/java-tron/blob/master/framework/src/main/java/org/tron/core/services/filter/LiteFnQueryHttpFilter.java

### [NEEDS-TRIAL] Bitquery (Tron Transfers cube, GraphQL v2)
NEED: Третий независимый индексатор переводов TRC20; DEX trades SunSwap для определения свопов
KIND: commercial SaaS
URL: https://docs.bitquery.io/docs/blockchain/Tron/
LICENSE: Проприетарный сервис
COMMERCIAL USE: Разрешено начиная с Pro ('Commercial-use license'); Personal — 'no commercial use'. Trial 7 дней — условия не указаны.
PROJECT STATE: Действующий; документация TRON доступна (transfers, DEX trades SunSwap/SunPump, balance updates, fees, mempool).
CLAIMED VS ACTUAL: Страница pricing противоречит сама себе: в hero 'from $49/mo', карточка Personal $29/мес, FAQ называет Pro $99 и Scale $299, карточки — $69 и $199 (цены при годовой оплате против помесячной). В примерах документации USDT в одном
месте указан с другим адресом контракта (TThzxNRLr…) — примеры нельзя копировать без проверки.
CAPABILITIES: Фильтры по Sender/Receiver, Currency.SmartContract, Block.Time, TransactionStatus.Success; DEX trades. Глубина истории зависит от dataset (combined/realtime/archive) — для TRON не подтверждена.
PRICING/LIMITS: Personal $29/мес (годовая оплата): 100k points, 30 req/min, без коммерции; Pro $69/мес (годовая) или $99 помесячно: 1M points, 90 req/min; Scale $199/мес (годовая): 5M points, 240 req/min; trial: 1,000 points.
RISKS: Стоимость запроса в points для адресной истории неизвестна; полнота истории TRON от genesis не подтверждена; 90 req/min на Pro (1.5 rps) мало для графа на 1,000 адресов.
REPLACEABILITY: Высокая (используется только как арбитр расхождений).
HOW VERIFIED: docs only (pricing, документация TRON и tron-transfers)
CONFIDENCE: medium
EVIDENCE: https://bitquery.io/pricing | https://docs.bitquery.io/docs/blockchain/Tron/ | https://docs.bitquery.io/docs/blockchain/Tron/tron-transfers/

### [ALTERNATIVE] Dune (TRON tables + API)
NEED: Офлайн-аналитика и построение независимого тестового набора с ground truth
KIND: commercial SaaS
URL: https://docs.dune.com/data-catalog/tron/overview
LICENSE: Проприетарный сервис; Dune Terms + SQL API Addendum
COMMERCIAL USE: Общие Terms не дают прямого ответа; условия API вынесены в SQL API Addendum (не прочитан). Запрещено 'copy or mirror any material' и автоматизированный сбор вне API.
PROJECT STATE: Действующий; TRON в каталоге: logs, blocks, transactions, decoded, tokens, отдельный раздел Tether on TRON.
CLAIMED VS ACTUAL: Наборы TRON 'similar to our EVM chains, but without internal transactions and traces'. Латентность данных не указана. Free после trial — view-only, без API-экспорта.
PRICING/LIMITS: Analyst $75/мес (4,000 credits), Plus $399/мес (25,000 credits) — по документации Dune через поисковую выдачу; экспорт через API 10 credits/MB на Analyst и 2 credits/MB на Plus (страница billing).
RISKS: Пакетный SQL с очередями — не укладывается в 30 с на транзакцию; стоимость за compute и экспорт; нет internal transactions.
REPLACEABILITY: Высокая.
HOW VERIFIED: docs only (data catalog, billing, terms) + search snippet для цен планов
CONFIDENCE: medium
EVIDENCE: https://docs.dune.com/data-catalog/tron/overview | https://docs.dune.com/api-reference/overview/billing | https://dune.com/terms | https://docs.dune.com/learning/how-tos/pricing-faqs

### [ALTERNATIVE] Google BigQuery — Tron Blockchain (Preview)
NEED: Массовая выгрузка истории для собственного индекса и тестовых наборов
KIND: dataset
URL: https://docs.cloud.google.com/blockchain-analytics/docs/supported-datasets
LICENSE: Google Cloud Terms; Pre-GA
COMMERCIAL USE: Разрешено условиями Google Cloud (оплата за сканирование), но статус Preview: 'available as is and might have limited support'.
PROJECT STATE: В списке Google-maintained датасетов значится 'Tron Blockchain (Preview)'; community-датасета blockchain-etl для TRON нет (в организации blockchain-etl репозитория tron-etl нет).
CLAIMED VS ACTUAL: Статус Preview без SLA; идентификатор датасета, схема и свежесть на странице не указаны; страница схемы TRON вернула 404.
PRICING/LIMITS: Оплата BigQuery за объём сканирования; конкретные цифры и размер таблиц TRON не проверялись.
RISKS: Preview может быть свёрнут; свежесть неизвестна; не для интерактивной трассировки.
HOW VERIFIED: docs only
CONFIDENCE: low
EVIDENCE: https://docs.cloud.google.com/blockchain-analytics/docs/supported-datasets

### [NEEDS-TRIAL] SQD Portal (tron-mainnet) + squid-sdk tron-processor
NEED: Путь к собственному индексу переводов без эксплуатации java-tron (фаза масштабирования)
KIND: managed OSS
URL: https://sqd.dev/chains/tron/
LICENSE: squid-sdk: Apache-2.0; Portal — сервис SQD
COMMERCIAL USE: SDK — да (Apache-2.0). Публичный Portal: 'free for development', для production — платные планы.
PROJECT STATE: subsquid/squid-sdk: 1,339 stars, 64 open issues, push 2026-10-13; в репозитории есть пакеты tron-processor, tron-data, tron-ingest, tron-dump, tron-normalization, tron-data-service (последний коммит по пути tron — 2026-10-02).
CLAIMED VS ACTUAL: Заявлено 'sub-second latency on the hot path' без чисел; числовых лимитов публичного Portal нет. Описание репозитория на GitHub упоминает только Ethereum, Solana и Substrate, хотя пакеты TRON есть.
CAPABILITIES: Датасет TRON с блока 0: blocks, transactions, logs, internal_transactions; endpoint https://portal.sqd.dev/datasets/tron-mainnet/stream (POST, type: tron).
INFRA: Node 23 подходит для SDK; собственная БД (Postgres/ClickHouse) под индекс.
PRICING/LIMITS: Публичный Portal бесплатно для разработки; Starter $99/мес, Growth $499/мес, Enterprise — индивидуально (индекс документации SQD).
RISKS: Не опробовано вживую; состав полей receipt (contractRet, energy) не проверен; хранение индекса 3.7 млрд переводов USDT требует отдельной инфраструктуры.
REPLACEABILITY: Средняя.
HOW VERIFIED: gh api (репозиторий, каталоги, коммиты), docs only (страница TRON, llms.txt)
CONFIDENCE: medium
EVIDENCE: https://sqd.dev/chains/tron/ | https://github.com/subsquid/squid-sdk/tree/master/tron | https://docs.sqd.dev/llms.txt

### [REJECTED] Allium (TRON schemas)
NEED: Готовые таблицы переводов, мостов и меток для аналитики
KIND: commercial SaaS
URL: https://docs.allium.so/historical-data/supported-blockchains/evm/tron/assets/token-transfers
LICENSE: Проприетарный сервис
COMMERCIAL USE: Не проверено (enterprise-контракт)
PROJECT STATE: В индексе документации есть страницы TRON: token transfers (TRX, TRC10, TRC20), bridges, metrics.
CLAIMED VS ACTUAL: Страницы документации при загрузке вернули пустое содержимое — схемы и свежесть известны только из поисковых сниппетов.
PRICING/LIMITS: Публичных цен нет.
RISKS: Enterprise-ценообразование несовместимо с лимитом $1 на расследование на этапе MVP.
HOW VERIFIED: search snippet only
CONFIDENCE: low
EVIDENCE: https://docs.allium.so/historical-data/supported-blockchains/evm/tron/assets/token-transfers | https://docs.allium.so/historical-data/supported-blockchains/evm/tron/bridges

### [REJECTED] GoldRush (Covalent) Foundational API
NEED: Индексированные переводы токенов по адресу
KIND: commercial SaaS
URL: https://goldrush.dev/docs/chains/overview
LICENSE: Проприетарный сервис
COMMERCIAL USE: Не релевантно
PROJECT STATE: Действующий, но TRON не поддерживается.
CLAIMED VS ACTUAL: TRON (tron-mainnet) отсутствует во всех категориях списка сетей (Foundational, Frontier, Community, Archived); из не-EVM указаны Bitcoin, HyperCore, а также Solana.
PRICING/LIMITS: Не релевантно для TRON.
RISKS: Нет данных TRON. Может пригодиться позже для Ethereum/BSC/Solana.
HOW VERIFIED: docs only
CONFIDENCE: high
EVIDENCE: https://goldrush.dev/docs/chains/overview

### [REJECTED] Flipside (data API / shares)
NEED: Аналитические таблицы TRON
KIND: commercial SaaS
URL: https://docs.flipsidecrypto.xyz
LICENSE: Проприетарный сервис
COMMERCIAL USE: Не релевантно
PROJECT STATE: Бизнес блокчейн-данных продан SonarX (пресс-релиз от 2026-05-19), компания ушла в продукт edisyl; docs.flipsidecrypto.xyz отдаёт 301 на https://edisyl.com/.
CLAIMED VS ACTUAL: Документация по данным больше недоступна по прежнему адресу; поддержка TRON не подтверждена ни у Flipside, ни у SonarX.
PRICING/LIMITS: Неизвестно.
RISKS: Продукт в переходе к другому владельцу.
HOW VERIFIED: WebFetch (редирект 301 зафиксирован) + search snippet only (пресс-релиз)
CONFIDENCE: medium
EVIDENCE: https://docs.flipsidecrypto.xyz/data/flipside-data/supported-chains | https://www.einpresswire.com/article/913502316/flipside-sells-blockchain-data-business-to-sonarx-commits-fully-to-edisyl-enterprise-ai-platform

### [REJECTED] OKLink Explorer API / Footprint Analytics / Chainbase
NEED: Альтернативные индексированные API с историей токенов по адресу
KIND: commercial SaaS
URL: https://www.oklink.com/docs/en/
LICENSE: Проприетарные сервисы
COMMERCIAL USE: Не проверено
PROJECT STATE: OKLink: документация открывается, но прочитанная часть касается только верификации контрактов, TRON в ней не упомянут. Footprint и Chainbase: страницы supported chains вернули 404, поддержка TRON не подтверждена.
CLAIMED VS ACTUAL: Для OKLink сторонний блог называет бесплатный API 50 calls/sec и Pro $300/мес — первичным источником не подтверждено. Footprint заявляет '30+ chains' на pricing и 23 в таблице сравнения (по сниппету).
PRICING/LIMITS: Не проверено.
RISKS: Нет подтверждённых эндпоинтов, лимитов и условий для TRON.
HOW VERIFIED: docs only (частично) + search snippet only
CONFIDENCE: low
EVIDENCE: https://www.oklink.com/docs/en/ | https://footprint.network/pricing

### [REJECTED] ETL: c0mm4nd/tronetl, pinax-network/substreams-tron, streamingfast/firehose-tron
NEED: ETL-инструменты для выгрузки блоков/переводов TRON в собственное хранилище
KIND: open-source
URL: https://github.com/c0mm4nd/tronetl
LICENSE: c0mm4nd/tronetl: лицензии нет; pinax-network/substreams-tron: Apache-2.0; streamingfast/firehose-tron: Apache-2.0
COMMERCIAL USE: tronetl — нельзя полагаться (без лицензии все права у автора). substreams-tron и firehose-tron — да (Apache-2.0).
PROJECT STATE: c0mm4nd/tronetl: Go, 6 stars, 4 open issues, последний push 2026-02-05, есть тесты (*_test.go) и .github. pinax-network/substreams-tron: 13 stars, push 2025-11-20. streamingfast/firehose-tron: 1 star, 6 open issues, push
2026-10-02. В организации blockchain-etl репозитория для TRON нет.
CLAIMED VS ACTUAL: Официального 'tron-etl' от blockchain-etl не существует — упоминания в обзорах относятся к сторонним форкам. Поиск по GitHub выдаёт много фишинговых и мусорных репозиториев с 'tronscan' в названии.
PRICING/LIMITS: Бесплатно; нужен источник блоков (свой узел или Firehose/Substreams endpoint).
RISKS: Малые сообщества (1–13 stars), bus factor 1; tronetl без лицензии; всё равно требуется инфраструктура хранения.
HOW VERIFIED: gh api (метаданные, содержимое корня, коммиты, список репозиториев организации)
CONFIDENCE: high
EVIDENCE: https://github.com/c0mm4nd/tronetl | https://github.com/pinax-network/substreams-tron | https://github.com/streamingfast/firehose-tron | https://github.com/blockchain-etl

### [ALTERNATIVE] tronpy (andelf/tronpy)
NEED: Python-клиент: кодек адресов base58/hex, ABI-декодирование, вызовы /wallet
KIND: open-source
URL: https://github.com/andelf/tronpy
LICENSE: MIT
COMMERCIAL USE: Да (MIT)
PROJECT STATE: 244 stars, 4 open issues, версия 0.6.2, последний коммит 2026-01-08; classifiers включают Python 3.13 и 3.14, статус 'Development Status :: 4 - Beta'; тесты в tests/, CI на CircleCI (.circleci/config.yml), GitHub Actions нет.
CLAIMED VS ACTUAL: 1) В tronpy/providers/http.py зашит список из 6 общих TronGrid API-ключей (DEFAULT_API_KEYS), которые используются, если свой ключ не передан и URL содержит 'trongrid' — чужие общие ключи с непредсказуемой квотой. 2) Нет ни одного
вызова TronGrid /v1 (история TRC20, события) — для основной задачи библиотека не помогает. 3) Нет gettransactioninfobyblocknum и JSON-RPC.
CAPABILITIES: Sync и async клиенты (requests/httpx) для /wallet/* и двух /walletsolidity-методов: get_transaction, get_transaction_info, get_solid_transaction_info, get_account, get_account_resource, get_delegated_resource_v2,
get_delegated_resource_account_index_v2, trigger_constant_contract.
PRICING/LIMITS: Бесплатно.
RISKS: Обязательно передавать собственный api_key; последний релиз 9 месяцев назад; тянет coincurve/pycryptodome ради подписи, которая платформе не нужна (ключи не запрашиваются).
REPLACEABILITY: Высокая: используемая часть (base58check, ABI) — десятки строк.
HOW VERIFIED: gh api + code read (pyproject.toml, tronpy/providers/http.py, tronpy/tron.py)
CONFIDENCE: high
EVIDENCE: https://github.com/andelf/tronpy | https://github.com/andelf/tronpy/blob/master/tronpy/providers/http.py | https://github.com/andelf/tronpy/blob/master/pyproject.toml

### [ALTERNATIVE] TronWeb (tronprotocol/tronweb) и прочие SDK (gotron-sdk, trident)
NEED: Клиентские библиотеки не на Python
KIND: open-source
URL: https://github.com/tronprotocol/tronweb
LICENSE: tronweb: MIT; fbsobreira/gotron-sdk: LGPL-3.0; tronprotocol/trident: Apache-2.0
COMMERCIAL USE: Да для всех трёх (LGPL у gotron-sdk накладывает условия при статической линковке Go)
PROJECT STATE: tronweb: 570 stars, 8 open issues, v6.5.1 от 2026-09-16, тесты на vitest, каталога .github/workflows в репозитории нет. gotron-sdk: 456 stars, push 2026-10-13. trident (Java): 216 stars, push 2026-08-12. Адрес tronweb/tronweb не
существует (404), актуальный — tronprotocol/tronweb.
CLAIMED VS ACTUAL: none found
PRICING/LIMITS: Бесплатно.
RISKS: Backend платформы на Python — JS/Go/Java SDK добавляют второй рантайм без выгоды для read-only задач. TronWeb уместен только если появится Node-сервис.
HOW VERIFIED: gh api (метаданные, релизы, package.json)
CONFIDENCE: high
EVIDENCE: https://github.com/tronprotocol/tronweb | https://github.com/fbsobreira/gotron-sdk | https://github.com/tronprotocol/trident

### [RECOMMENDED] USDT contract on-chain: isBlackListed(address) + события AddedBlackList / RemovedBlackList / DestroyedBlackFunds
NEED: Статус блэклиста Tether с доказательством (TXID события, блок, время)
KIND: standard
URL: https://api.trongrid.io/v1/contracts/TR7NHqjeKQxGTCi8q8ZY4pL8otSzgjLj6t/events?event_name=AddedBlackList
LICENSE: Публичные данные блокчейна
COMMERCIAL USE: Да (ограничения только у провайдера доступа)
PROJECT STATE: Контракт TR7NHqjeKQxGTCi8q8ZY4pL8otSzgjLj6t активен: 200 событий AddedBlackList за 2026-09-30…2026-10-13 (около 15 в день), последнее DestroyedBlackFunds — 2026-10-09.
CLAIMED VS ACTUAL: TronScan /api/stableCoin/blackList отдаёт готовый список (total 7,838), но свежесть относительно on-chain событий не подтверждена: в выборке с sort=2 самая верхняя запись датирована 2026-10-12 19:01 UTC, тогда как TronGrid
показывает AddedBlackList от 2026-10-13 13:49 UTC (семантика сортировки неизвестна).
CAPABILITIES: Текущий статус: POST /wallet(solidity)/triggerconstantcontract с function_selector isBlackListed(address). История: TronGrid /v1/contracts/{USDT}/events?event_name=… (limit 200, fingerprint, min/max_timestamp) — block_number,
block_timestamp, transaction_id, result._user. DestroyedBlackFunds содержит _blackListedUser и _balance.
PRICING/LIMITS: Первичное зеркало: порядка 7.8 тыс. Added + Removed + Destroyed по 200 на страницу — около 100–150 запросов разово; далее 1–3 запроса на инкремент. Constant call — 1 запрос на адрес.
RISKS: isBlackListed возвращает только текущее состояние (историческое состояние узлы не отдают) — для статуса 'на момент перевода' нужна история событий. Адреса в событиях в 0x-hex без префикса 41. DestroyedBlackFunds уменьшает баланс
без обычного перевода — учесть в сверке балансов.
REPLACEABILITY: Высокая: события читаются также через eth_getLogs (окнами по 5000 блоков) или собственный узел.
HOW VERIFIED: API call made (TronGrid events AddedBlackList и DestroyedBlackFunds, PublicNode isBlackListed и balanceOf, TronScan stableCoin/blackList)
CONFIDENCE: high
EVIDENCE: https://api.trongrid.io/v1/contracts/TR7NHqjeKQxGTCi8q8ZY4pL8otSzgjLj6t/events?event_name=AddedBlackList&limit=200 | https://apilist.tronscanapi.com/api/stableCoin/blackList?limit=20&start=0 | https://tron-rpc.publicnode.com/wallet/triggerconstantcontract

## OPEN QUESTIONS FOR OWNER (researcher)
- В какой юрисдикции зарегистрирована компания? TRONSCAN Terms of Service (2022) исключает резидентов и организации США, Сингапура, материкового Китая, Гонконга и Тайваня и требует письменного согласия на сторонние приложения.
Готовы ли вы запросить у TronScan письменное разрешение на коммерческое использование API и показ их тегов в отчётах (с атрибуцией)?
- Кто заведёт аккаунты и ключи TronGrid (до 3 ключей на аккаунт), TronScan и Chainstack? Я аккаунты не создавал и условия не принимал.
- Считаете ли вы пару TronGrid + TronScan достаточно независимой (оба сервиса из экосистемы TRON) или второй источник обязан быть сторонним оператором (узел Chainstack/QuickNode, Bitquery)?
- Какая ожидается доля больших графов (около 1,000 адресов) и пиковая одновременность? От этого зависит, хватит ли бесплатных 100,000 запросов в день TronGrid или нужно сразу запрашивать Custom plan.
- Одобряете ли фиксированные $49/мес за Chainstack Growth ради SLA и запаса по RPS, или на старте остаёмся на бесплатных планах с PublicNode в резерве?
- Политика для hub-адресов (горячие кошельки бирж с миллионами переводов): останавливаться на помеченной границе или листать ограниченное число страниц? Какой лимит страниц на адрес принять по умолчанию?
- Включать ли в отчёты только solidified-данные (задержка около 1 минуты) или допускается предварительный показ неподтверждённых переводов с пометкой?
- Нужны ли в MVP вторичные рёбра графа — финансирование TRX (активация адреса) и делегирование энергии — или только поток USDT?
- Нужен ли статус блэклиста 'на момент перевода' (требует зеркала событий) или достаточно текущего isBlackListed на момент отчёта?
- Готовы ли вы в фазе 2 к собственному индексу (SQD Portal от $99/мес или сервер с 3.5–4 TB NVMe под java-tron), если зависимость от единственного индексного API TronGrid станет неприемлемой?

## NOT VERIFIED (researcher)
- QPS и поведение дневной квоты TronGrid с API key (15 или 30 rps по разным источникам; '1 request per second' после исчерпания квоты — только из документации). Ключ не создавался.
- Цены платных и Custom планов TronGrid (на сайте '???' и форма заявки).
- Квоты, QPS и возможные платные тарифы TronScan для запросов с ключом; страницы документации по отдельным эндпоинтам (token-trc20-transfers, common-errors, blacklist) не прочитаны из-за Cloudflare-challenge, который я не обходил.
- Применимость TRONSCAN Terms of Service от 2022-01-04 к API и наличие более новых API-условий; текст объявлений support.tronscan.org известен только по поисковым сниппетам (страница отдала 403).
- Поведение неуспешных транзакций типа REVERT (проверен только OUT_OF_ENERGY) и появление в истории нулевых transferFrom (address poisoning) для USDT — вживую не выбиралось.
- Глубокая пагинация TronGrid по fingerprint дальше 2 страниц и наличие общего потолка строк; проверена только работа окон по времени.
- TronGrid internal-transactions эндпоинты (/v1/accounts|transactions|contracts/.../internal-transactions) — вживую не вызывались.
- Событие RemovedBlackList и семантика Issue/Redeem/DestroyedBlackFunds относительно Transfer-событий (влияет на сверку балансов).
- Свежесть и полнота TronScan /api/stableCoin/blackList относительно on-chain событий; смысл параметров sort и direction.
- Полнота выдачи чужих Delegate/UnDelegateResourceContract в TronGrid /v1/accounts/{addr}/transactions — наблюдалась на одном адресе.
- Chainstack: доступность TRON на бесплатном Developer-плане (подтверждено только блогом Chainstack), фактическая работа эндпоинтов и ToS; живых вызовов не было.
- ToS о коммерческом использовании у QuickNode, GetBlock, Ankr, dRPC, NOWNodes, Tatum, Chainstack, SQD — не читались.
- Точные цены и лимиты GetBlock (free 5 или 20 RPS), Ankr, dRPC, NOWNodes (€20/мес за Pro) — только поисковые сниппеты или сторонние обзоры; кредитная стоимость TRON-вызовов QuickNode.
- Bitquery: глубина истории TRON в v2 (archive/combined), стоимость адресного запроса в points, фактические цены (страница противоречива).
- Google BigQuery Tron (Preview): идентификатор датасета, схема таблиц, свежесть, стоимость сканирования.
- Dune: SQL API Addendum (коммерческое использование, хранение результатов), латентность таблиц TRON; цены планов взяты из документации Dune через поисковую выдачу.
- Allium (схемы и цены), OKLink (статус API, эндпоинты TRON, цены), Footprint и Chainbase (поддержка TRON), SonarX после покупки бизнеса Flipside.
- SQD Portal для TRON: состав полей (contractRet, energy), лимиты публичного Portal, условия production — вживую не проверялось.
- Существование и параметры эндпоинта Tatum для истории TRC20 по адресу (страница документации вернула 404).
- Адреса и актуальный реестр контрактов SunSwap, JustLend и кросс-чейн мостов на TRON — в этом аудите не собирались.
- Стоимость сервера под собственный java-tron FullNode (3.5–4 TB NVMe) и время синхронизации.
- Является ли 2021-09-01 действительно первым переводом Binance-Hot 2 (то есть полнота истории TronGrid от самого начала) — независимым источником не сверялось.