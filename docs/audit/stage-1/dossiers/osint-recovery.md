# AREA osint-recovery: OSINT sources and recovery channels (exchanges, Tether, law enforcement)

============================================================
PART 1 - VERIFIER REPORT (takes precedence over the researcher wherever they disagree)
============================================================

## VERIFIER SUMMARY
Аудит в основном точен по фактам: из 26 перепроверенных утверждений 14 подтверждены первичными источниками, 10 исправлены, 1 опровергнуто, 1 проверить не удалось. Но три из девяти рекомендаций в текущем виде не проходят. **Что не
проходит** - **Минимальный набор OSINT-источников.** Файл OFAC по тегу TRX (261 адрес) не содержит 79 TRON-адресов, которые OFAC помечает тегом USDT; полный набор — 340. GoPlus вернул sanctioned=0 для двух адресов из SDN — его
нужно исключить. TronScan работает без ключа (аудит утверждал обратное), но лимит 3 rps со штрафом около 94 с не укладывается в цель «1,000 адресов за 5 минут», а условия коммерческого использования не опубликованы. - **Brave
Search API.** Цена подтверждена ($0.005 за запрос), но предписание аудита логировать все ответы нарушает ToS §3(b)(i). Нужно либо сменить основной провайдер на Tavily, либо логировать только запросы и собственные снимки страниц. -
**Справочник бирж.** Структура верна, наполнение не подтверждено: сайты девяти бирж с этой сети недоступны и мне, и исследователю. Окна временной заморозки (MEXC 48 часов, Binance 24 часа или 7 дней) нужно убрать до проверки с
другого сетевого выхода. **Что исправлено в фактах** - Зеркало OFAC проверяется каждую ночь, а не раз в несколько недель; оно совпало с первичными файлами на 337 из 340 адресов. - TRM free Sanctions API пометил только 2 из 13
адресов с тегом TRX — локальный список он не заменяет. - У crt.sh есть бесплатная замена: SSLMate Certificate Search API, план $0. - RDAP через rdap.org не обслуживает .ru и .io — нужен fallback на WHOIS. - У T3 FCU, по сообщению
прессы от 2026-05-27, появился официальный сайт; домен я не подтвердил. - Для Узбекистана официальный канал есть: колл-центр 102 и 1102, обращения через murojaat.gov.uz. **Что подтверждено** Политика Tether (2018-01-03,
inforequests@tether.to, пути для жертвы нет), условия Chainabuse (non-commercial, 10 вызовов в месяц), isBlackListed через TronGrid, цены Tavily, Exa, X API, GoPlus, закрытие Google Custom Search, условия urlscan и VirusTotal,
Report Fraud, IC3 PSA, политика Circle, EDPB Guidelines 02/2025 v2.0 от 2026-07-07. **Пропущенные кандидаты** TRM Beacon Network, SSLMate CT Search API, MistTrack (метки TRON по $0.10 за вызов), Parallel, Perplexity Search и
Linkup, EDPB Guidelines 03/2026 о web scraping, Chainabuse как канал подачи отчёта жертвой. **Ограничения проверки** Лимит WebSearch исчерпан в середине работы, поэтому поиск новых кандидатов неполон; полный список непроверенного
— в blocking_risks. Аккаунты не создавались, ключи не вводились. Сторонний код не запускался; в scratchpad сессии сохранены только публичные данные (списки OFAC, PDF EDPB), ответы API и условия в PDF.

## BLOCKING RISKS
- Справочник бирж не подтверждён первичными источниками: сайты Binance, OKX, HTX, KuCoin, Bitget, Gate, MEXC, Bybit с этой сети недоступны (ECONNRESET), Coinbase — 403, Wayback — 429. Все реквизиты и сроки взяты из поисковой выдачи.
Выпуск таких записей как официальных нарушает требование «ничего не выдумывать»; регулярная сверка page_hash с текущей машины невозможна.
- Ошибка в санкционном наборе: использование только sanctioned_addresses_TRX.json пропускает 79 из 340 TRON-адресов OFAC (они помечены тегом USDT). Для платформы по USDT TRC20 это пропуск именно целевого актива.
- Сторонние санкционные проверки на TRON ненадёжны: GoPlus вернул sanctioned=0 для двух адресов из SDN; TRM free Sanctions API пометил 2 из 13 адресов с тегом TRX, подтверждённых в первичных файлах OFAC. Заменять локальный список
ими нельзя.
- TronScan: условия использования и квоты с ключом не опубликованы; без ключа 3 rps и приостановка около 94 с при превышении. При запросе метки на каждый адрес граф из 1,000 адресов занимает не менее 334 с — больше цели 5 минут.
Коммерческое использование не подтверждено документом.
- Конфликт ToS Brave (§3(b)(i): запрет хранить Search Results) с обязательным журналом действий агентов. У альтернатив свои ограничения: Tavily хранит входы и выходы для обучения, Exa получает лицензию на раскрытие запросов и
результатов третьим лицам, Parallel обучается на данных клиента. Без решения владельца о провайдере и о составе журнала поисковый модуль нельзя запускать в коммерческом продукте.
- В MVP нет лицензионно чистого источника жалоб на мошенничество: Chainabuse разрешён только для personal, non-commercial use и ограничен 10 вызовами в месяц; ScamSniffer не содержит адресов TRON; CryptoScamDB заброшен. OSINT-слой
рискует не дать измеримого прироста над детерминированным baseline, пока не получен Chainabuse Partner Access (цена не опубликована).
- Возврат средств целиком зависит от правоохранительных органов: у Tether, T3 FCU, Beacon Network и порталов Kodex нет входа для жертвы или платформы. Продукт может выдавать только пакет доказательств и черновики; любые формулировки
об обещанном возврате создают правовой и репутационный риск (FBI PSA I-082423 прямо предупреждает о сервисах возврата).
- Риск фишинговых двойников в справочнике: вокруг T3 FCU найдено несколько доменов-кандидатов (один на продаже, один зарегистрирован в марте 2026 и отдаёт 404), официальный домен не подтверждён. Без поля проверки домена запись может
направить следователя на поддельный адрес.
- Ограничение этой проверки: лимит WebSearch исчерпан в середине работы, поэтому поиск новых кандидатов 2025–2026 годов неполон (не проверены Bitrace, Whale Alert Scam Alert, AMLBot, OKLink labels, Google Web Risk, Chainalysis
sanctions API), как и статус Шотландии в Report Fraud и каналы России, Казахстана, Кыргызстана, Таджикистана, Беларуси.

## VERIFIER VERDICTS ON RECOMMENDATIONS

### NEED: (a) Минимальный набор OSINT-источников об адресах для MVP
PRIMARY: isBlackListed on-chain + локальная копия OFAC SDN (TRX — 261 адрес) + TronScan API с бесплатным ключом + GoPlus как подсказка
STANDS: False
ISSUE: Три дефекта. (1) Набор OFAC неполон: файл TRX не содержит 79 TRON-адресов, которые OFAC помечает тегом USDT (пересечение 0) — пропуск 23% санкционных адресов именно по целевому активу. (2) GoPlus на TRON даёт ложноотрицательные
ответы: sanctioned=0 для двух адресов из SDN; страницы условий — 404. Как источник он не подсказывает, а вводит в заблуждение. (3) TronScan: условия коммерческого использования и квоты с ключом не опубликованы; без ключа лимит 3
rps со штрафом около 94 с, то есть 1,000 адресов занимают не менее 334 с — больше цели 5 минут; риск-флагов в ответе нет (санкционный адрес помечен только "High Balance"). Кроме того, в наборе нет ни одного лицензионно чистого
источника жалоб на мошенничество, поэтому вклад OSINT agent сверх детерминированного baseline будет близок к нулю.
SUGGESTED CHANGE: Оставить isBlackListed и события AddedBlackList/RemovedBlackList/DestroyedBlackFunds через TronGrid как первичный факт. OFAC: объединять файлы TRX и USDT (адреса на T…) либо парсить sdn_advanced.xml самим; зеркало проверяется
каждую ночь и совпало с первичными файлами на 337 из 340 адресов. GoPlus из MVP исключить. TRM free Sanctions API не использовать как замену (2 из 13 по тегу TRX). TronScan — только для publicTag, вне критического пути, с кэшем и
лимитом на топ-N адресов; до письменного ответа TronScan о коммерческом использовании помечать источник как "terms unverified". Заявку на Chainabuse Partner Access подать сразу; до ответа — только deep link для ручной проверки.
Санкционные адреса из OFAC включить в тестовый набор как ground truth.

### NEED: (a) Контекст инцидентов
PRIMARY: Web3 is Going Great (RSS, CC BY 3.0); SlowMist Hacked только как ссылка
STANDS: True
ISSUE: Факты подтверждены. Релевантность для розничных краж USDT TRC20 низкая, что аудит сам признаёт. CC BY 3.0 требует атрибуции в отчёте.
SUGGESTED CHANGE: Оставить отключаемым модулем вне MVP-метрик; в отчёте добавлять строку атрибуции и ссылку на запись.

### NEED: (a) Web search API для OSINT agent
PRIMARY: Brave Search API (план Search)
STANDS: False
ISSUE: Цена и лимиты подтверждены ($0.005 за запрос, 50 QPS), но рекомендация внутренне противоречива: в architecture_notes предписано логировать все запросы и ответы, а ToS Brave §3(b)(i) запрещает хранить, кэшировать и создавать базу
Search Results целиком или частично, кроме transient storage; §13(c)(ii) требует стереть их при расторжении. Это прямо конфликтует с требованием воспроизводимости (логируется каждое действие агента). Права на хранение доступны
только по отдельному соглашению (Enterprise). Нужна карта владельца. Запросы содержат адреса и TXID жертвы и уходят третьей стороне.
SUGGESTED CHANGE: Вариант А: основным сделать Tavily (1,000 кредитов в месяц без карты, $0.008, запрета хранения Output в Terms нет), приняв, что по §6.5 Tavily может хранить входы и выходы для обучения, — значит в запросы нельзя включать ничего,
кроме публичных адресов, TXID и доменов. Вариант Б: оставить Brave, но логировать только текст запроса, время и собственные снимки страниц, загруженных платформой, а не выдачу; получить письменное подтверждение Brave. В обоих
вариантах адаптер search(query) оставить сменным; оценить Parallel Search API ($1–5 за 1,000, 5,000 бесплатных запросов в месяц, 600 rpm; Output принадлежит клиенту, но Parallel обучается на данных клиента) и Linkup ($0.005, ZDR
по addendum).

### NEED: (a) Доменная и инфраструктурная разведка
PRIMARY: RDAP (rdap.org); crt.sh дополнительно, best-effort
STANDS: True
ISSUE: RDAP работает, но не покрывает .ru и .io (404 для существующих доменов) и, вероятно, .me, .co, .kz, .su — зоны, значимые для скам-сайтов и СНГ. crt.sh недоступен (4 из 4 попыток за два аудита — 502). Утверждение, что бесплатной
альтернативы нет, неверно.
SUGGESTED CHANGE: Добавить fallback на WHOIS (порт 43) для TLD без RDAP и хранить сырой ответ с хешем. Вместо crt.sh основным источником CT сделать SSLMate Certificate Search API, план Small $0 (100 single-hostname и 10 full-domain запросов в час);
crt.sh оставить запасным. Условия коммерческого использования бесплатного плана SSLMate уточнить письменно.

### NEED: (b) Заморозка USDT эмитентом (Tether, T3 FCU)
PRIMARY: Жертва подаёт заявление в полицию; орган направляет запрос с legal process на inforequests@tether.to; платформа готовит пакет и черновик для следователя
STANDS: True
ISSUE: Маршрут соответствует опубликованной политике Tether (2018-01-03) и подтверждён: на tether.to нет пути для жертвы. Устарели два утверждения: у T3 FCU, по сообщению прессы от 2026-05-27, появился официальный сайт (домен мной не
подтверждён); не учтён TRM Beacon Network (с 2025-08-20) — сеть, в которой проверенные следователи помечают адреса, а участники (Coinbase, Binance, Kraken, PayPal и другие) получают оповещения. Оба канала также доступны только
через органы.
SUGGESTED CHANGE: В справочник добавить записи T3 FCU и Beacon Network со статусом press и who_may_submit = law_enforcement_only; домен T3 FCU вносить только после подтверждения через официальные аккаунты Tether, TRON DAO или TRM. В черновике для
следователя упоминать, что орган может обратиться в T3 FCU и TRM. Проверки isBlackListed и остатка USDT перед формированием запроса сохранить.

### NEED: (b) Запросы к биржам
PRIMARY: Двухканальный пакет: обращение жертвы в поддержку биржи + черновик запроса для следователя с указанием официального канала органа
STANDS: True
ISSUE: Структура верна и согласуется с тем, что удалось подтвердить (Kraken, пресс-релиз Bybit, официальная формулировка Binance о невозможности заморозки без official freezing order). Но ни один реквизит девяти бирж не подтверждён
первичным чтением ни исследователем, ни мной: сайты бирж с этой сети недоступны, Wayback отдаёт 429. Окна времени в обосновании (MEXC 48 часов, Binance 24 часа или 7 дней, Bybit до 12 часов) не подтверждены, а для Binance, по
выдаче, взяты со сторонних копий.
SUGGESTED CHANGE: До проверки с другого сетевого выхода все записи бирж хранить со статусом unverified и не показывать как official; класс official_via_search приравнять к unverified. Сроки временной заморозки из текстов и шаблонов убрать. Для
Bybit указать: портал только для VIP, рассмотрение 2–4 часа, ограничения дискреционные. Проверку наличия биржи в Kodex делать по странице самой биржи, а не по URL app.kodexglobal.com.

### NEED: (b) Полицейские и киберполицейские каналы
PRIMARY: Справочник по юрисдикциям: IC3, Report Fraud, национальная полиция ЕС по списку Europol, записи СНГ со статусом unverified
STANDS: True
ISSUE: IC3 и Report Fraud подтверждены первичными источниками. Для Узбекистана официальный канал существует и проверяется за один запрос: gov.uz/ru/iiv — колл-центр 102 и 1102, обращения через murojaat.gov.uz. Список стран на странице
Europol не читается без JavaScript.
SUGGESTED CHANGE: Запись Узбекистана перевести в official_read (102, 1102, murojaat.gov.uz) с пометкой, что отдельного порядка для криптовалютных краж нет. Украину (ticket.cyberpolice.gov.ua) и Казахстан (qamqor.gov.kz) подтвердить чтением страниц
в браузере. Список Europol собрать вручную.

### NEED: (b) Структурированный справочник получателей
PRIMARY: Версионируемый справочник (БД + YAML) с source_url, source_class, date_verified, page_hash, conflicts_noted и запретом LLM создавать записи
STANDS: True
ISSUE: Схема адекватна. Слабые места: класс official_via_search создаёт впечатление официальности у непроверенных данных; нет поля о том, с какого сетевого выхода страница прочитана и доступна ли она вообще; нет защиты от поддельных
доменов (в ходе проверки найдены несколько доменов-кандидатов T3 FCU, один на продаже, один зарегистрирован в 2026-03). Сверка page_hash для страниц бирж с этой сети невозможна.
SUGGESTED CHANGE: Добавить поля canonical_domain и domain_verified_via, verification_vantage, snapshot_path (сохранённая копия страницы), entity_by_jurisdiction. Класс official_via_search исключить из показа в отчётах. Для бирж сократить срок
пересмотра с 90 до 30 дней. Задачу сверки запускать с внешнего хоста.

### NEED: (c) Правовые и приватностные ограничения
PRIMARY: Режим "адреса и организации, не люди"; перечень запретов для платформы
STANDS: True
ISSUE: Подход верен; ссылка на EDPB Guidelines 02/2025 v2.0 от 2026-07-07 подтверждена первичным PDF. Пропущено: (1) EDPB Guidelines 03/2026 о web scraping в контексте generative AI (консультация до 2026-10-30) прямо относятся к OSINT
agent; (2) условия поисковых провайдеров означают передачу данных расследования третьим лицам — Tavily §6.5, лицензия Exa на User Input и Output с правом раскрытия, обучение Parallel на данных клиента; (3) недоступность сайтов
бирж с сети разработки может указывать на регуляторные ограничения в стране размещения — это не проверено и требует местного юриста.
SUGGESTED CHANGE: В DPIA включить поток "запрос к поисковому API" и правило минимизации: в запрос идут только публичные адреса, TXID и домены, без имён, контактов и описаний дела. Учесть Guidelines 03/2026 при проектировании снимков страниц. До
запуска получить заключение местного юриста о допустимости сервиса и о локализации данных.

## VERIFIER FACT CHECKS

- [CORRECTED] TronScan API :: Без ключа сервис непригоден: /api/account/tag и /api/stableCoin/blackList возвращают 429, /api/accountv2 и /api/security/account/data — 401; квоты и цена не опубликованы
  CORRECT VALUE: Без ключа /api/account/tag отвечает 200 и отдаёт поля blueTag/greyTag/redTag/publicTag/chainTags (для TV6MuMXf… publicTag = "Binance-Hot 2"); /api/stableCoin/blackList отвечает 200 (total 7838, limit обязан быть в диапазоне
20–100, порядок записей не хронологический). 429 возникает только при превышении лимита: текст ошибки "request rate exceeded the allowed_rps(3), and the query server is suspended for 94 s". 401 для /api/security/account/data и
/api/accountv2 подтверждён. Квоты с ключом и условия использования в документации действительно не опубликованы (страница auth: "see the TronScan developer portal", обновлена 2026-03-16).
  METHOD: API call made (около 12 keyless GET) + docs read (docs.tronscan.org/en/api/common-network-auth, /en/api/api-keys)
  EVIDENCE: https://apilist.tronscanapi.com/api/account/tag?address=TV6MuMXfmLbBqPZvBHdwFsDnQeVfnmiuSi

- [CORRECTED] TronScan API :: Даёт нативные метки и риск-флаги TRON, пригодные как OSINT-источник об адресах
  CORRECT VALUE: Метки бирж есть (hot wallet), но риск-флагов в keyless-ответе нет: для адреса TA3941uFAvmVibSkQ6fMJXxmaSNovX86mz, который находится в OFAC SDN (тег USDT), /api/account/tag вернул только chainTag "High Balance", без redTag.
Санкционный статус через этот эндпоинт не виден. Покрытие депозитных адресов бирж не проверено.
  METHOD: API call made (1 адрес — выборка минимальная)
  EVIDENCE: https://apilist.tronscanapi.com/api/account/tag?address=TA3941uFAvmVibSkQ6fMJXxmaSNovX86mz

- [CONFIRMED] On-chain isBlackListed через TronGrid :: Keyless constant call работает: result=true, constant_result=0, energy 4658
  CORRECT VALUE: Подтверждено дословно. Дополнительно: keyless /v1/contracts/TR7N…/events?event_name=AddedBlackList отдаёт события с TXID; последнее — 2026-10-13T13:49:54Z, за 2026-09-30…2026-10-13 набирается 200 событий. Для фактов о заморозке
это первичный источник; список TronScan вторичен.
  METHOD: API call made (1 POST constant call + 2 GET events)
  EVIDENCE: https://api.trongrid.io/v1/contracts/TR7NHqjeKQxGTCi8q8ZY4pL8otSzgjLj6t/events?event_name=AddedBlackList&limit=3&order_by=block_timestamp,desc

- [CORRECTED] 0xB10C/ofac-sanctioned-digital-currency-addresses :: MIT, 179 stars, ветка lists обновлена 2026-10-01, TRX — 261 адрес; зеркало обновляется раз в несколько недель, а не ежедневно
  CORRECT VALUE: Лицензия MIT, 179 stars, последний коммит lists 2026-10-01, 261 адрес в TRX — подтверждено. Вывод о редком обновлении неверен: workflow generate-lists.yml запускается каждую ночь (cron '24 1 * * *'), запуски 2026-10-10…13
завершились success; коммит появляется только при изменении списка OFAC. Сверка с первичными sdn.csv + sdn_comments.csv: 259 из 261 адресов TRX и 78 из 79 TRON-адресов из файла USDT найдены в первичных файлах.
  METHOD: gh api (repo, commits ветки lists, actions/runs, workflow) + загрузка первичных sdn.csv и sdn_comments.csv с treasury.gov и сверка
  EVIDENCE: https://github.com/0xB10C/ofac-sanctioned-digital-currency-addresses/blob/main/.github/workflows/generate-lists.yml

- [CORRECTED] OFAC SDN — набор санкционных адресов TRON :: Для TRON достаточно локальной копии sanctioned_addresses_TRX.json (261 адрес)
  CORRECT VALUE: Файл TRX неполон для задачи USDT TRC20: в sanctioned_addresses_USDT.json 94 адреса, из них 79 в формате TRON (T…, 34 символа), пересечение с файлом TRX — 0. Полный набор TRON-адресов — 340 (261 + 79). В первичном sdn.csv адрес
TA3941uFAvmVibSkQ6fMJXxmaSNovX86mz помечен "Digital Currency Address - USDT". Использование только файла TRX пропускает 23% санкционных TRON-адресов.
  METHOD: Загрузка обоих JSON, подсчёт и пересечение; проверка адреса в первичном sdn.csv
  EVIDENCE: https://raw.githubusercontent.com/0xB10C/ofac-sanctioned-digital-currency-addresses/lists/sanctioned_addresses_USDT.json

- [CONFIRMED] Chainabuse API :: Terms of Use v4 от 2025-01-20 дают лицензию только для personal, non-commercial use; бесплатный ключ — 10 вызовов в месяц; Partner — до 5,000 calls/hour; TRON поддерживается
  CORRECT VALUE: Все четыре пункта подтверждены. В тексте ToS (7 страниц) слова API, scraping, automated не встречаются — отдельного разрешения на программный доступ нет. Дополнение: документация описывает Chainabuse и как канал подачи отчёта
жертвой с опциональной передачей контактов правоохранительным органам (Contribute Reports, Law Enforcement Partners).
  METHOD: PDF прочитан целиком (извлечение текста) + docs read (docs.trmlabs.com: getting-started-2-1.md, supported-blockchain-list.md)
  EVIDENCE: https://chainabuse.com/ChainAbuse_TermsofUse.pdf

- [CORRECTED] GoPlus Security — Address Security API :: Tron поддерживается, 20 флагов; лимиты противоречивы; платные пакеты $199–$3,499/месяц (по сниппету); качество по TRON не подтверждено
  CORRECT VALUE: Цены и лимиты подтверждены на официальной странице: Free 150K CU/месяц, 30k CU/день, 150 CU/мин; пакеты $199, $399, $799, $1,899, $3,499 в месяц. Качество по TRON опровергнуто живой пробой: для двух адресов из OFAC SDN (TA3rH2A7…
с chain_id=tron и TA3941uF… с chain_id=tron и без него) поле sanctioned = "0", data_source пуст. Страницы условий использования по адресам /terms-of-service и /en/terms — 404.
  METHOD: API call made (3 keyless GET) + чтение gopluslabs.io/en/security-api
  EVIDENCE: https://api.gopluslabs.io/api/v1/address_security/TA3rH2A7iHnm6pKH8gr9cK1EZnShnmZdFg?chain_id=tron

- [CORRECTED] TRM Labs free Sanctions Screening API :: Без ключа 1 req/sec и 100 req/day, с ключом 100K req/day; поддержка TRON не подтверждена
  CORRECT VALUE: Лимиты из первичного источника проверить нельзя: страница эндпоинта отдаёт форму входа, а introduction.md сообщает, что документацию присылают после заполнения формы (продукт теперь называется "Free Sanctions and Beacon Network
address screening"). Keyless POST работает (HTTP 201). TRON-адреса распознаются, но полнота низкая: из 13 адресов с тегом TRX, присутствующих в первичных файлах OFAC, isSanctioned=true только у 2; из 8 TRON-адресов с тегом USDT —
у 8 из 8.
  METHOD: API call made (3 keyless POST, 26 адресов) + сверка выборки с первичными sdn.csv/sdn_comments.csv
  EVIDENCE: https://api.trmlabs.com/public/v1/sanctions/screening

- [CONFIRMED] Brave Search API :: $5 за 1,000 запросов, $5 кредитов ежемесячно, 50 QPS; ToS от 2026-09-01 запрещает хранение Search Results (3(b)(i)) и использование для обучения моделей (3(b)(xiii)); атрибуция необязательна; нужна карта
  CORRECT VALUE: Подтверждено. Уточнение: права на хранение даются только планом, который их явно предоставляет; в общих ToS такого положения нет, на странице цен оно упомянуто лишь в FAQ, а среди планов есть только Search, Answers и Enterprise
(custom agreements, Zero Data Retention). ToS §13(c)(ii) требует стереть Search Results при расторжении.
  METHOD: docs read (страница цен через curl, ToS через WebFetch)
  EVIDENCE: https://api-dashboard.search.brave.com/terms-of-service

- [CONFIRMED] Tavily Search API :: Free 1,000 кредитов без карты; PAYG $0.008; Project $30 за 4,000; Terms от 2026-05-04 разрешают интеграцию в Customer Applications, запрета кэширования нет
  CORRECT VALUE: Подтверждено (другие планы: Bootstrap $100/15,000, Startup $220/38,000, Growth $500/100,000). Существенное дополнение, не отмеченное в аудите: §6.5 — Tavily может хранить Customer Input и Outputs для обучения; §6.6(i) запрещает
использовать Output для разработки конкурирующих моделей.
  METHOD: docs read (terms, api-credits, pricing)
  EVIDENCE: https://www.tavily.com/terms

- [CORRECTED] Exa API :: instant $4, fast/auto $7, deep $12, deep-reasoning $15 за 1,000; $10 бесплатных кредитов; условия использования не прочитаны
  CORRECT VALUE: Цены подтверждены. Условия (PDF, 8 страниц) прочитаны: пользователь даёт Exa бессрочную безотзывную лицензию хранить, публиковать и раскрывать третьим лицам User Input и Output; запрещено дублировать, публиковать и лицензировать
информацию, полученную через сервис, кроме временного кэша браузера; запрещено использовать сервис и Output для конкурирующего продукта. Даты обновления в документе нет.
  METHOD: PDF прочитан (извлечение текста) + docs read (exa.ai/pricing)
  EVIDENCE: https://exa.ai/terms-of-service

- [CONFIRMED] Google Custom Search JSON API :: Закрыт для новых клиентов; действующие должны перейти до 2027-01-01
  CORRECT VALUE: Подтверждено дословно: "closed to new customers", срок 1 января 2027; 100 запросов в день бесплатно, далее $5 за 1,000 до 10k в день.
  METHOD: docs read
  EVIDENCE: https://developers.google.com/custom-search/v1/overview

- [CONFIRMED] Tether — Law Enforcement Requests Policy :: Политика датирована 2018-01-03, требует appropriate legal process для запросов данных и заморозки, контакт inforequests@tether.to; ToS от 2026-02-26; пути для жертвы нет
  CORRECT VALUE: Подтверждено по page-data JSON сайта. Дополнительно проверено: в page-data разделов FAQ и Knowledge Base нет ни одного вхождения слов stolen, hacked, scam, freeze, frozen — официального пути для жертвы на tether.to действительно
нет (портал cs.tether.to — JS-приложение, содержимое не прочитано).
  METHOD: Чтение page-data JSON (legal, faqs, knowledge-base) через curl
  EVIDENCE: https://tether.to/page-data/en/legal/page-data.json

- [CORRECTED] T3 Financial Crime Unit :: Заморожено более $450 млн (сообщение 2026-05-14), 23 юрисдикции; официального сайта не найдено
  CORRECT VALUE: $450 млн, 23 юрисдикции и дата 2026-05-14 подтверждены (The Block). Утверждение об отсутствии сайта устарело: Crypto Briefing 2026-05-27 сообщает о запуске официального сайта T3 FCU. Домен в публикациях не назван, и я его не
подтвердил. t3fcu.org зарегистрирован 2026-03-25 (GoDaddy), размещён на Webflow, сертификаты выпущены 2026-09-11, но все пути отдают 404 с этой сети — принадлежность проекту не доказана. t3fcu.com выставлен на продажу. Ссылка
аудита на trondao.org вернула 404.
  METHOD: WebFetch (Crypto Briefing, The Block) + RDAP и Cert Spotter по t3fcu.org + curl по доменам
  EVIDENCE: https://cryptobriefing.com/t3-financial-crime-unit-launches-website/

- [CORRECTED] RDAP (rdap.org) :: Бесплатно, без ключа, 200 за 0.8 с; не все ccTLD поддерживают RDAP
  CORRECT VALUE: Для .com подтверждено (200, 0.76 с, redirect на rdap.verisign.com). Пробел шире, чем указано: через rdap.org не обслуживаются .ru и .io (yandex.ru и github.io — 404); nic.me, nic.co, nic.kz, nic.su тоже 404. Работают .uz
(rdap.cctld.uz), .xyz, .top, .cc, .vip, .app, .site, .online, .pro, .info, .org, .biz, .finance, .live, .shop, .club, .ai, .to. Для .ru и .io нужен fallback на WHOIS (порт 43).
  METHOD: API call made (около 28 keyless GET)
  EVIDENCE: https://rdap.org/domain/yandex.ru

- [REFUTED] crt.sh / Cert Spotter :: crt.sh нестабилен (502); замена — платный Cert Spotter от $15/месяц, бесплатного API не найдено
  CORRECT VALUE: 502 от crt.sh подтверждён (ещё 2 попытки). Но бесплатный API есть: у SSLMate Certificate Search API план Small за $0/месяц — 100 single-hostname запросов в час, 10 full-domain в час, 75 в минуту, 5 в секунду. Keyless GET
api.certspotter.com/v1/issuances?domain=…&include_subdomains=true&expand=dns_names вернул данные. $15/месяц — это цена мониторинга, а не API поиска. Условия коммерческого использования бесплатного плана на странице не указаны.
  METHOD: API call made (2 keyless GET) + docs read
  EVIDENCE: https://sslmate.com/pricing/ct_search_api

- [CONFIRMED] urlscan.io и VirusTotal Public API :: urlscan: коммерческое использование только с письменного разрешения, Automate $5,000/год; VirusTotal: 500 запросов/день, 4/мин, запрещён в коммерческих продуктах
  CORRECT VALUE: Подтверждено дословно. urlscan Terms: Last updated July 22, 2020; Free 5,000 scans / 1,000 searches / 10,000 retrievals в день; Professional $1,250/месяц.
  METHOD: docs read (urlscan pricing и terms, docs.virustotal.com)
  EVIDENCE: https://urlscan.io/terms/

- [CONFIRMED] ScamSniffer scam-database :: GPL-3.0; 2,530 адресов, все EVM, TRON — 0; задержка 7 дней; real-time API $999/месяц
  CORRECT VALUE: Подтверждено: 2,530 записей, все начинаются с 0x, адресов формата TRON 0; pushed 2026-10-13; 267 stars.
  METHOD: gh api (repo, README) + подсчёт в blacklist/address.json
  EVIDENCE: https://github.com/scamsniffer/scam-database

- [CONFIRMED] Web3 is Going Great и SlowMist Hacked :: W3IGG: текст CC BY 3.0, код MIT, лента обновлена 2026-10-12. SlowMist Hacked: 2,308 событий, около $39.08 млрд, последняя запись 2026-10-10, фильтр Tron Ecosystem, All Rights Reserved, API нет
  CORRECT VALUE: Подтверждено по обоим источникам (W3IGG /about: "Text is licensed under a Creative Commons Attribution 3.0 Unported License"; LICENSE репозитория — MIT; feed 2026-10-12T23:58Z).
  METHOD: gh api + curl feed.xml и /about + WebFetch hacked.slowmist.io
  EVIDENCE: https://www.web3isgoinggreat.com/about

- [CONFIRMED] X API :: Около $0.005 за пост и $0.010 за профиль — только по сторонним обзорам
  CORRECT VALUE: Подтверждено официальной документацией: Posts: Read — $0.005 per resource; User: Read — $0.010 per resource; модель pay-per-use без подписок. Статус legacy-тарифа Basic на странице не указан.
  METHOD: docs read
  EVIDENCE: https://docs.x.com/x-api/getting-started/pricing

- [CONFIRMED] Report Fraud (UK) и FBI IC3 PSA :: Report Fraud запущен 2025-12-04 и заменил Action Fraud, 0300 123 2040; PSA I-082423 от 2023-08-24 — перечень сведений для заявления
  CORRECT VALUE: Подтверждено по gov.uk (публикация от 4 December 2025, reportfraud.police.uk, номер телефона не изменился) и по ic3.gov (I-082423-PSA: адреса, сумма и тип актива, дата и время, TXID). Статус Шотландии не проверен:
reportfraud.police.uk вернул 403.
  METHOD: docs read (gov.uk через curl, ic3.gov через WebFetch)
  EVIDENCE: https://www.gov.uk/government/news/report-fraud-new-service-from-city-of-london-police

- [CONFIRMED] EDPB Guidelines 02/2025 (blockchain) :: Версия 2.0 от 2026-07-07 — известна только по вторичным источникам
  CORRECT VALUE: Подтверждено первичным PDF: "Version 2.0, Adopted on 07 July 2026" (v1.1 — 08 April 2025). В тексте: публичные ключи и идентификаторы квалифицируются как personal data, если физическое лицо можно идентифицировать разумно
вероятными средствами. Дополнительно найдено: Guidelines 03/2026 on web scraping in the context of generative AI — консультация до 2026-10-30; документ прямо касается OSINT agent.
  METHOD: PDF загружен и прочитан (извлечение текста) + страницы edpb.europa.eu
  EVIDENCE: https://www.edpb.europa.eu/system/files/2026-07/edpb_guidelines_202502_blockchain_v2_en.pdf

- [UNVERIFIABLE] Биржи: Binance, OKX, HTX, KuCoin, Bitget, Gate, MEXC, Coinbase, Bybit :: Каналы для органов (Kodex, LEORS, email), перечни документов и окна временной заморозки (MEXC 48 часов, Binance 24 часа или 7 дней, Bybit ответ до 12 часов)
  CORRECT VALUE: Первичные страницы прочитать не удалось: binance.com, okx.com, htx.com, gate.com, mexc.com, kucoin.com, bitget.com, bybit.com — ECONNRESET; help.coinbase.com — 403; web.archive.org — 429. По поисковой выдаче: OKX guide обновлён
2026-08-03, Kodex основной, enforcement@okx.com — резерв; официальный текст Binance говорит, что биржа не может заморозить без official freezing order, а формулировка про временную заморозку и 24 часа встречается только на
сторонних копиях. Bybit: по пресс-релизу от 2025-09-29 портал только для VIP, рассмотрение за 2–4 часа, ограничения дискреционные. app.kodexglobal.com/<slug>/signin отвечает 200 на любой slug, включая несуществующий, — этим
наличие биржи в Kodex не проверяется.
  METHOD: Попытки WebFetch и curl (отказ сети) + search snippet + WebFetch пресс-релиза
  EVIDENCE: https://www.prnewswire.com/news-releases/bybit-launches-dedicated-vip-portal-for-stolen-fund-inflow-reporting-302569525.html

- [CONFIRMED] Kraken :: Единая форма legal inquiry (статья обновлена 2025-04-02); Transparency Report 2025: 7,957 запросов, 74 страны, 51.3%
  CORRECT VALUE: Подтверждено: форма support.kraken.com/hc/forms/35862482750484, отдельного портала и перечня документов на странице нет. По вакансии Kraken (только поисковая выдача) Kodex используется как внутренняя система учёта запросов —
открыт ли он для внешней подачи, не установлено.
  METHOD: docs read (support.kraken.com, payward.com)
  EVIDENCE: https://support.kraken.com/articles/how-do-i-submit-a-legal-inquiry

- [CORRECTED] Каналы СНГ и Центральной Азии :: Узбекистан: 102, онлайн-форма не найдена; все сведения community-reported
  CORRECT VALUE: Официальный сайт МВД Узбекистана (gov.uz/ru/iiv) указывает колл-центр 102 и 1102 и ведёт на портал обращений murojaat.gov.uz (ссылка "Отправить обращение", organization_tin=200637696). Отдельного порядка для криптовалютных краж на
странице нет. ticket.cyberpolice.gov.ua отвечает 200 ("Система електронного звернення громадян"), qamqor.gov.kz — 200 (JS-приложение, содержимое не прочитано). Сайт МВД России с этой сети недоступен.
  METHOD: curl официальных сайтов (заголовки, ссылки)
  EVIDENCE: https://gov.uz/ru/iiv

- [CONFIRMED] Circle :: Access Denial Policy (PDF от 2026-05-28): блокировка по приказу органа или суда США или Франции, суды Delaware или Massachusetts; USDC на TRON не выпускается с 2024-02-21
  CORRECT VALUE: Подтверждено текстом PDF (2 страницы, creationDate 2026-05-28) и блогом Circle ("Effective immediately we will no longer mint USDC on TRON", 21 февраля 2024).
  METHOD: PDF прочитан (извлечение текста) + WebFetch блога
  EVIDENCE: https://www.circle.com/blog/circle-is-discontinuing-support-for-usdc-on-the-tron-blockchain

## CANDIDATES MISSED BY THE RESEARCHER (found by verifier)

- TRM Beacon Network (https://www.trmlabs.com/resources/blog/trm-labs-launches-beacon-network-the-first-real-time-crypto-crime-response-network)
  WHY: Запущена 2025-08-20: проверенные следователи помечают адреса, метки распространяются на связанные кошельки, участники (Coinbase, Binance, Kraken, PayPal, Robinhood, Stripe, Ripple, Crypto.com) получают оповещения до вывода
средств. Среди целей названо возвращение средств жертв мошенничества. TRM объединил её с бесплатным API: "Free Sanctions and Beacon Network address screening".
  ASSESSMENT: Для жертвы и платформы прямого входа нет — только через правоохранительный орган или участника сети. В справочник получателей — как канал уровня law_enforcement_only со статусом press. Документация API закрыта формой запроса;
состав участников на 2026 год не проверен.

- SSLMate Certificate Search API (Cert Spotter), план Small $0 (https://sslmate.com/pricing/ct_search_api)
  WHY: Рабочая замена crt.sh, который не ответил ни разу за два аудита. Бесплатно: 100 single-hostname и 10 full-domain запросов в час, 75 в минуту; keyless-вызов вернул сертификаты с not_before.
  ASSESSMENT: Подходит для MVP: модуль доменной разведки запускается редко. Условия коммерческого использования бесплатного плана на странице не указаны — нужен письменный ответ SSLMate. Следующий план — $50 в месяц.

- MistTrack OpenAPI (SlowMist) (https://docs.misttrack.io/openapi/x402-pay-as-you-go-pricing.md)
  WHY: Единственный найденный платный источник меток с поддержкой TRON и оплатой за вызов без подписки: address_labels возвращает сущность и тип адреса (deposit, hot, cold) — то, чего не дают TronScan-метки для депозитных адресов бирж.
  ASSESSMENT: Дорого для бюджета $1: address_labels $0.10 за запрос по x402 (или $0.20 в пакете Developer от $20 за 100 вызовов), risk_score $1.00 за запрос; подписки $229, $689, $2,069 в месяц. Применим только точечно — к 2–5 конечным адресам
расследования. Условия использования и точность меток по TRON не проверены.

- Parallel Search API, Perplexity Search API, Linkup (https://parallel.ai/pricing)
  WHY: Поисковые API 2025–2026 годов, не рассмотренные в аудите. Parallel: $1 (Turbo, Fast) или $5 (Basic, Advanced) за 1,000 запросов, до 5,000 бесплатных запросов в месяц, 600 rpm, Output принадлежит клиенту. Perplexity Search API: $5
за 1,000, Fast $1 за 1,000. Linkup: $0.005 за стандартный поиск, $20 ежемесячного кредита при регистрации с рабочим email, Zero Data Retention по addendum.
  ASSESSMENT: Parallel и Perplexity Fast дешевле Brave в 5 раз, но у Parallel Output одного запроса нельзя хранить или передавать другим конечным клиентам, и Parallel обучается на данных клиента. Условия хранения у Perplexity не проверены.
Кандидаты на второго провайдера после сравнения условий.

- Guidelines 03/2026 on web scraping in the context of generative AI (EDPB) (https://www.edpb.europa.eu/public-consultations/guidelines-032026-on-web-scraping-in-the-context-of-generative-ai_en)
  WHY: Правовой источник, пропущенный в разделе (c): OSINT agent загружает веб-страницы и передаёт их в LLM. Консультация открыта до 2026-10-30.
  ASSESSMENT: Текст PDF не прочитан — зафиксировано только существование и сроки. Учесть в DPIA до запуска платных тарифов и при обслуживании клиентов из ЕС.

- Официальные каналы МВД Узбекистана: колл-центр 102 и 1102, murojaat.gov.uz (https://gov.uz/ru/iiv)
  WHY: Аудит записал Узбекистан как "онлайн-форма не найдена" и community-reported. Официальный сайт министерства указывает номера 102 и 1102 и ведёт на портал электронных обращений.
  ASSESSMENT: Можно внести в справочник со статусом official_read и датой 2026-10-14. Специального порядка для криптовалютных краж не найдено; подразделение по киберпреступности на странице как канал приёма не указано.

- Chainabuse как канал подачи отчёта жертвой (https://docs.trmlabs.com/guides/chainabuse/offering-scam-support.md)
  WHY: Аудит рассматривал Chainabuse только как источник поиска. Документация описывает подачу отчёта жертвой с опциональной передачей контактов правоохранительным органам; партнёры-органы ищут отчёты по своей юрисдикции.
  ASSESSMENT: Бесплатный и законный шаг для жертвы; добавить в справочник как community-канал с пометкой, что это не заявление в полицию. Встраивание формы в продукт требует партнёрского соглашения.

- Cloudflare URL Scanner API (https://developers.cloudflare.com/radar/investigate/url-scanner/)
  WHY: Возможная замена urlscan.io, коммерческое использование которого требует письменного разрешения: скриншоты, сетевые запросы, сертификаты, DNS, вердикты; хранение успешных сканов 12 месяцев.
  ASSESSMENT: Цена и лимиты на странице не указаны, условия коммерческого использования не проверены; нужен API token аккаунта Cloudflare; сканы по умолчанию публичные — для расследований ставить Unlisted. Требует пробной проверки владельцем.

- WHOIS (порт 43) как fallback к RDAP (https://rdap.org/domain/github.io)
  WHY: RDAP через rdap.org не обслуживает .ru и .io, а также, судя по пробам, .me, .co, .kz, .su.
  ASSESSMENT: Бесплатно, без ключа; ответы неструктурированы и у каждого реестра свои ограничения частоты. Нужен для дат регистрации и регистратора в этих зонах.

============================================================
PART 2 - RESEARCHER AUDIT
============================================================

## RESEARCHER RECOMMENDATIONS

### R1. NEED: (a) Минимальный набор OSINT-источников об адресах для MVP
PRIMARY: Четыре источника с нулевой ценой запроса: (1) on-chain isBlackListed по контракту USDT; (2) локальная копия OFAC SDN (TRX — 261 адрес); (3) TronScan API с бесплатным ключом (account tag, security, stableCoin blackList); (4) GoPlus
Address Security — только как подсказка и только после проверки ToS.
RATIONALE: Только эти источники одновременно покрывают TRON, доступны без договора и дают проверяемый первичный факт (состояние контракта, запись SDN) либо воспроизводимый ответ API. Chainabuse — самая полезная база жалоб, но её Terms of Use
разрешают только 'personal, non-commercial use', а бесплатный ключ даёт 10 вызовов в месяц.
ARCHITECTURE NOTES: OFAC синхронизировать cron-задачей из sdn_advanced.xml. Ключ TronScan — только в secrets, в логах маскировать. Кэш ответов по адресу с TTL 24 часа. В отчёте формулировка 'reported as / listed in', а не утверждение о виновности.
COST: $0 за запрос по всем четырём источникам. На стандартное расследование (несколько десятков адресов): 0 платных вызовов.
DATA QUALITY VERIFICATION: Каждая OSINT-запись хранит source_url, retrieved_at, sha256 ответа, класс источника (primary / official / commercial-curated / community-reported / unverified) и confidence. Правило: community-reported и GoPlus никогда не дают
метку 'биржа' и не поднимают confidence выше low без подтверждения первичным фактом. В тестовом наборе из 50 сценариев — не менее 10 с известными публичными фактами (адреса из OFAC SDN, адреса из событий AddedBlackList USDT) для
измерения precision и recall.
RISKS: Квоты и ToS TronScan не опубликованы; качество GoPlus по TRON неизвестно (в пробе все флаги 0); зеркало OFAC обновляется раз в 2–3 недели.
REPLACEABILITY: Каждый источник — отдельный адаптер с интерфейсом lookup(address) -> [claims]; отключение любого не ломает трассировку.
REJECTED ALTERNATIVES:
  - Chainabuse free API: ToS: non-commercial; 10 calls/month. Использовать только после Partner Access; до этого — ссылка для ручной проверки пользователем.
  - ScamSniffer: В открытом списке 0 адресов TRON (2,530 адресов, все EVM); задержка 7 дней; real-time $999/месяц.
  - CryptoScamDB: Заброшен с 2023 года, API отвечает 502, у данных нет лицензии.
  - TRM Sanctions API: Дублирует локальный OFAC; поддержка TRON этим эндпоинтом не подтверждена; без ключа 100 запросов в день.

### R2. NEED: (a) Контекст инцидентов (взломы, известные схемы)
PRIMARY: Web3 is Going Great (RSS, текст CC BY 3.0) для загрузки; SlowMist Hacked — только как ссылка, найденная веб-поиском.
RATIONALE: Web3 is Going Great — единственный источник с ясной лицензией и машиночитаемой лентой (обновлена 2026-10-12). SlowMist Hacked лучше покрывает TRON (фильтр Tron Ecosystem, 2,308 событий), но у него нет API и стоит 'All Rights
Reserved'.
ARCHITECTURE NOTES: Функция необязательная; в MVP её можно отключить без потери ключевых метрик.
COST: $0
DATA QUALITY VERIFICATION: Инцидент привязывается к расследованию только при совпадении адреса или TXID из первичных данных; совпадение по названию проекта — не более чем 'возможная связь' с confidence low.
RISKS: Низкая релевантность для розничных краж USDT: большинство случаев в этих базах не появится.
REPLACEABILITY: Полная
REJECTED ALTERNATIVES:
  - De.Fi REKT Database API: Ключ по email, цена кредитов не опубликована, покрытие Tron и коммерческие условия не подтверждены.
  - Массовый парсинг SlowMist Hacked: Нет лицензии и API — юридический риск; достаточно ссылки на конкретную запись.

### R3. NEED: (a) Web search API для OSINT agent
PRIMARY: Brave Search API (план Search)
RATIONALE: Собственный индекс (нет риска скрейпинга Google), ясный коммерческий договор, $0.005 за запрос, 50 QPS, $5 кредитов в месяц покрывают около 1,000 запросов.
ARCHITECTURE NOTES: Запросы строить детерминированно по шаблонам (адрес в кавычках, TXID в кавычках, домен + 'scam'), а не свободно генерировать LLM — это снижает расход и повышает воспроизводимость. Все запросы и ответы логировать с идентификатором
расследования.
COST: Лимит 10 запросов на расследование = $0.05; жёсткий потолок 20 запросов = $0.10. Первые ~1,000 запросов в месяц покрываются кредитом.
DATA QUALITY VERIFICATION: Поиск используется только для обнаружения URL. Факт попадает в отчёт после того, как платформа сама загрузила страницу, сохранила sha256 снимка, дату и короткую цитату, а evidence-verification agent нашёл в снимке искомый адрес
или TXID. Результат без точного вхождения адреса/TXID отбрасывается.
RISKS: ToS Brave запрещает хранить и перераспространять Search Results — в отчёт идут только URL и собственный снимок. Для подписки нужна карта владельца. Допустимость подачи результатов в LLM для inference стоит подтвердить у Brave
письменно.
REPLACEABILITY: Высокая: интерфейс search(query) -> [url, title, snippet]; Tavily подключается как второй провайдер.
REJECTED ALTERNATIVES:
  - Tavily: Запасной вариант: $0.008 за запрос, 1,000 бесплатных кредитов в месяц без карты; условия мягче к хранению, но выдача — метапоиск.
  - Exa: $7 за 1,000 (auto); условия использования не прочитаны.
  - Serper / SerpApi: Скрейпинг Google; незавершённые процессы Google v. SerpApi и Reddit v. SerpApi; SerpApi к тому же $0.025 за запрос.
  - Google Custom Search JSON API: Закрыт для новых клиентов, отключение 2027-01-01.
  - X API: Около $0.005 за пост; один поиск на 100 постов = $0.50.

### R4. NEED: (a) Доменная и инфраструктурная разведка
PRIMARY: RDAP (rdap.org как bootstrap); crt.sh — дополнительно, best-effort
RATIONALE: RDAP бесплатен, без ключа, ответил за 0.8 с; даёт дату регистрации домена и регистратора, чего достаточно, чтобы показать 'сайт создан за N дней до кражи' и адресовать abuse-жалобу регистратору.
ARCHITECTURE NOTES: Модуль включается только если пользователь указал домен или он найден в первичных материалах. Ретраи с backoff для crt.sh, таймаут 10 с, отказ не блокирует отчёт.
COST: $0
DATA QUALITY VERIFICATION: Хранить сырой RDAP-ответ с хешем и датой; дату регистрации сверять по полю events реестра, а не по сторонним whois-сайтам.
RISKS: Персональные данные владельца скрыты; часть ccTLD без RDAP.
REPLACEABILITY: Полная
REJECTED ALTERNATIVES:
  - urlscan.io: Коммерческое использование только с письменного разрешения; платный план от $5,000 в год.
  - VirusTotal Public API: Прямой запрет на использование в коммерческих продуктах; 500 запросов в день.
  - SecurityTrails: Цены не удалось проверить (403), по сторонним данным — индивидуальные.
  - crt.sh как основной: Два запроса из двух вернули 502.

### R5. NEED: (b) Заморозка USDT эмитентом (Tether, T3 FCU)
PRIMARY: Маршрут: жертва -> заявление в полицию своей юрисдикции -> орган направляет запрос с legal process на inforequests@tether.to. Платформа готовит пакет доказательств и черновик письма для следователя.
RATIONALE: Опубликованная политика Tether требует 'appropriate legal process' и адресована органам. У T3 FCU нет публичного приёма обращений. Официально подтверждённого прямого канала для жертвы нет.
ARCHITECTURE NOTES: Recovery agent ранжирует адреса по остатку USDT и давности последнего движения: запрос имеет смысл только пока средства лежат на адресе. В тексте черновика не обещать результат.
COST: $0 платных вызовов; одна проверка isBlackListed на каждый конечный адрес.
DATA QUALITY VERIFICATION: Перед формированием запроса проверять on-chain: текущий баланс USDT на адресе (есть ли что замораживать) и isBlackListed (не заморожен ли уже). Обе проверки — с номером блока и временем.
RISKS: Политика Tether не обновлялась с 2018 года — реальная практика может отличаться. Заморозка не равна возврату: возврат требует решения суда или органа.
REPLACEABILITY: Нет альтернативы эмитенту
REJECTED ALTERNATIVES:
  - Прямой freeze request жертвы в Tether: Не описан ни в политике, ни в ToS; сообщения об успехе — только из блогов коммерческих фирм. Можно предложить как необязательный шаг через cs.tether.to с пометкой 'результат не
  - гарантирован'.
  - Обращение в T3 FCU: Нет официального сайта и адреса; домены t3fcu.io и t3fcu.com не принадлежат проекту.
  - Circle: USDC на TRON не выпускается с 2024-02-21; политика требует приказа органа или суда США/Франции.

### R6. NEED: (b) Запросы к биржам, получившим USDT
PRIMARY: Двухканальный пакет на каждую биржу: (1) обращение жертвы в поддержку/форму биржи (Binance Support, Bybit Report Stolen Funds, MEXC Report Abnormal Funds, OKX support); (2) черновик запроса для следователя с указанием официального
канала органа (Kodex, LEORS, KuCoin Information Request System, email Gate/HTX).
RATIONALE: Все биржи с опубликованными правилами принимают запросы данных и заморозки только от органов; порталы Kodex закрыты для частных лиц. Жертве доступно лишь уведомление биржи и, у части бирж, краткая временная заморозка до
поступления документов полиции (MEXC — 48 часов, Binance — 24 часа или 7 дней по разным версиям).
ARCHITECTURE NOTES: Пакет доказательств в формате, который прямо требуют биржи: адреса и хеши в копируемой таблице (CSV/XLSX — требование HTX), хронология (Gate), обзор инцидента и трассировка до адреса биржи (OKX), ссылки на explorer (Binance,
MEXC), английский язык. Срок давности первого перевода показывать крупно: окна измеряются часами.
COST: $0
DATA QUALITY VERIFICATION: Биржа называется получателем только если адрес депозита подтверждён меткой с источником и confidence выше порога (см. область address attribution). В пакет входят только TXID, проверенные по первичным данным; каждая строка таблицы
— TXID, время UTC, сумма, адрес отправителя, адрес получателя, ссылка на explorer.
RISKS: Страницы бирж не удалось прочитать напрямую — все реквизиты из пересказа поиска и требуют повторной проверки. У Bybit, Kraken и Coinbase канал для органов не подтверждён. Требования бирж меняются без уведомления.
REPLACEABILITY: Справочник получателей — данные, а не код; запись заменяется без релиза.
REJECTED ALTERNATIVES:
  - Автоматическая отправка писем на адреса для органов от имени пользователя: Биржи требуют государственный домен отправителя и proof of authority; письма от частных лиц игнорируются, а массовая рассылка вредит репутации
  - платформы.
  - Регистрация платформы в Kodex: Доступ только для сотрудников органов; попытка — выдача себя за орган.

### R7. NEED: (b) Полицейские и киберполицейские каналы
PRIMARY: Справочник по юрисдикциям с выбором по стране жертвы: США — IC3; Великобритания — Report Fraud; ЕС — национальная полиция по списку Europol; СНГ и Центральная Азия — записи со статусом 'unverified' до проверки по официальным
сайтам.
RATIONALE: Europol и INTERPOL заявления от граждан не принимают. Номер заявления в полиции — обязательное условие почти у всех бирж, поэтому это первый шаг в любом сценарии.
ARCHITECTURE NOTES: Шаблон заявления строить на перечне FBI PSA I-082423: адреса, сумма и актив, дата и время, TXID, хронология, переписка, домены, использованные биржи. Локализация RU/EN, далее по стране первого клиента.
COST: $0
DATA QUALITY VERIFICATION: Запись справочника попадает в отчёт только со статусом official и датой проверки не старше 90 дней; иначе показывается с явной пометкой 'не проверено, уточните на официальном сайте'.
RISKS: Юрисдикция первой жертвы неизвестна; для стран Центральной Азии официальные онлайн-каналы не подтверждены.
REPLACEABILITY: Полная
REJECTED ALTERNATIVES:
  - Europol / INTERPOL как адресаты: Официально не принимают обращения частных лиц.
  - Action Fraud: Заменён сервисом Report Fraud 2025-12-04.
  - SEAL 911: Волонтёрская группа для экстренных крупных инцидентов, не правовой канал.

### R8. NEED: (b) Проектирование структурированного справочника получателей
PRIMARY: Собственный версионируемый справочник (таблица в БД + YAML в репозитории) со схемой: recipient_id; organisation; legal_entity; category (issuer / exchange / le_portal / police / community); jurisdictions; channel_type (kodex /
web_form / email / phone / in_person); channel_value; who_may_submit (victim / lawyer / law_enforcement_only); request_types (report / preservation / freeze / info); requirements[]; language; time_window; victim_path; le_path;
source_url; source_class (official_read / official_via_search / press / community / unverified); date_verified; verified_by; page_hash; next_review_due; conflicts_noted; status.
RATIONALE: Требование проекта — хранить источник, дату проверки и уверенность для каждого факта; каналы бирж противоречивы между версиями страниц и меняются, поэтому нужны поля conflicts_noted и page_hash.
ARCHITECTURE NOTES: Стартовое наполнение на 2026-10-14 — из этого аудита: official_read — Tether, Circle, Kraken (форма), IC3; official_via_search — Binance, OKX, HTX, KuCoin, Bitget, Gate, MEXC, Coinbase, Report Fraud, Europol; press — T3 FCU;
unverified — Bybit (канал органов), каналы СНГ.
COST: $0 за запрос; около 2–4 часов ручной проверки раз в 90 дней на ~25 записей.
DATA QUALITY VERIFICATION: Ежеквартальная ручная проверка; еженедельная автоматическая сверка page_hash официальной страницы с оповещением при изменении; запись без source_url и date_verified не публикуется; LLM может только выбирать записи из справочника,
но не создавать их.
RISKS: С машины разработки сайты бирж недоступны (соединение сбрасывается) — задаче сверки нужен другой сетевой выход.
REPLACEABILITY: Полная
REJECTED ALTERNATIVES:
  - Жёстко зашитые адреса в шаблонах писем: Устаревают незаметно; невозможно показать дату проверки.
  - Генерация контактов LLM: Нарушает правило 'ничего не выдумывать'; найден поддельный домен с 'контактами Bybit'.

### R9. NEED: (c) Правовые и приватностные ограничения
PRIMARY: Режим 'адреса и организации, не люди': хранить OSINT только об адресах, транзакциях, доменах и юридических лицах; персональные данные физических лиц — не собирать, а случайно попавшие — не индексировать и не включать в отчёт.
RATIONALE: Идентификаторы кошельков могут быть персональными данными (EDPB Guidelines 02/2025, версия 2.0 от 2026-07-07 — по вторичным источникам). Сведения о подозрении в преступлении подпадают под ст. 10 GDPR. Ошибочное обвинение — риск
иска о диффамации. Условия источников ограничивают хранение и коммерческое использование.
ARCHITECTURE NOTES: Платформа не должна: выдавать себя за правоохранительный орган и подавать запросы в каналы для органов; обещать возврат средств или брать плату 'за возврат'; связываться с подозреваемыми; называть неизвестный адрес биржей или
человека преступником; отправлять сообщения от имени пользователя без его явного действия; запрашивать seed-фразы и приватные ключи; выдавать черновики за юридическую консультацию. Формулировки — 'по данным источника X на дату Y'.
COST: Разовая консультация юриста по юрисдикции первого клиента; DPIA до запуска платных тарифов.
DATA QUALITY VERIFICATION: Автоматический фильтр отчёта на email, телефоны и имена физических лиц; журнал оснований обработки; срок хранения материалов расследования задаётся явно и удаление проверяется тестом.
RISKS: Локализация данных: Узбекистан (ст. 27-1, поправки от 2026-03-26), Казахстан (ст. 12), Россия (152-ФЗ, первичный сбор с 2025-07-01) — по вторичным источникам, нужен местный юрист.
REPLACEABILITY: n/a
REJECTED ALTERNATIVES:
  - Профили подозреваемых (имена, соцсети, телефоны): Ст. 10 и 14 GDPR, риск диффамации и доксинга; это работа органов.
  - Покупка утечек и закрытых баз: Незаконное происхождение данных.
  - Скрейпинг источников вопреки условиям: Chainabuse (non-commercial), urlscan.io и VirusTotal (запрет коммерческого использования), Brave (запрет хранения результатов).

## LIVE PROBE FINDINGS
- gh api: scamsniffer/scam-database — GPL-3.0, 267 stars, последний коммит 2026-10-13; в blacklist/address.json 2,530 адресов, все EVM, адресов TRON 0.
- gh api: CryptoScamDB/blacklist — без лицензии, последний push 2023-04-29; GET https://api.cryptoscamdb.org/v1/stats вернул 502.
- gh api: 0xB10C/ofac-sanctioned-digital-currency-addresses — MIT, ветка lists обновлена 2026-10-01, sanctioned_addresses_TRX.json содержит 261 адрес.
- gh api: molly/web3-is-going-great — MIT; feed.xml обновлён 2026-10-12.
- gh api: MetaMask/eth-phishing-detect — лицензия DBAD v1.2, pushed 2026-10-13.
- TronScan без ключа: /api/accountv2 и /api/security/account/data — 401; /api/account/tag и /api/stableCoin/blackList — 429; /api/system/status — 200.
- TronGrid без ключа: triggerconstantcontract isBlackListed(address) на контракте USDT вернул result=true, constant_result=0, energy 4658.
- GoPlus без ключа: address_security с chain_id=tron — HTTP 200 за 0.5 с, 20 флагов; supported_chains включает Tron (id 'tron').
- RDAP: https://rdap.org/domain/example.com — 200 за 0.8 с, redirect на rdap.verisign.com.
- crt.sh: два запроса JSON подряд вернули 502 Bad Gateway.
- tether.to page-data JSON: Law Enforcement Requests Policy — 'Last updated: January 3, 2018', контакт inforequests@tether.to; Terms of Service — 'Last updated: February 26, 2026'.
- Домены T3 FCU: t3fcu.io — припаркованная страница (/lander); t3fcu.com — редирект на площадку продажи доменов; t3fcu.org — 404.
- Circle Stablecoin Access Denial Policy (PDF создан 2026-05-28) прочитан целиком.
- Chainabuse Terms of Use (PDF v4, 'last updated on January 20, 2025') прочитан целиком: лицензия 'solely for your personal, non-commercial use'.
- Сайты бирж с этой машины недоступны: binance.com, okx.com, kraken.com, bybit.com, kucoin.com, bitget.com, gate.com, mexc.com, htx.com — сброс соединения (curl exit 35, WebFetch ECONNRESET). web.archive.org вернул 429, но показал
наличие снимка Binance guidelines от 2026-08-18.
- developers.google.com: Custom Search JSON API 'closed to new customers', отключение 2027-01-01.

## CANDIDATES (full audit cards)

### [RECOMMENDED] TronScan API (account tag, security service, stablecoin blacklist)
NEED: (a) OSINT об адресах: публичные метки и риск-флаги TRON
KIND: public API
LICENSE: Proprietary; условия использования API не найдены в документации
COMMERCIAL USE: Не подтверждено. Документация не содержит условий коммерческого использования и атрибуции; нужен API key (заводит владелец).
PROJECT STATE: Документация docs.tronscan.org живая (есть llms.txt, разделы MCP/CLI). Эндпоинты из индекса: GET /api/account/tag, GET /api/security/account/data, GET /api/stableCoin/blackList. Заголовок TRON-PRO-API-KEY.
CLAIMED VS ACTUAL: В индексе ключ назван 'recommended', а на странице авторизации — 'Required' для mainnet. На практике без ключа: /api/accountv2 и /api/security/account/data вернули 401, /api/account/tag и /api/stableCoin/blackList — 429. То есть
без ключа сервис непригоден.
CAPABILITIES: Нативное покрытие TRON: метки аккаунтов, security check по адресу/токену/транзакции, список blacklist стейблкоинов.
INFRA: HTTPS-клиент, хранение ключа в secrets, кэш ответов.
PRICING/LIMITS: Цена и квоты не опубликованы на прочитанных страницах ('see the TronScan developer portal'). Rate limit глобальный, при 429 — Retry-After.
RISKS: Нет опубликованных квот и ToS; метки частично пользовательские — нельзя считать их доказательством принадлежности бирже; имена полей ответа не проверены (страницы рендерятся на клиенте).
REPLACEABILITY: Средняя: метки заменяются другими источниками; blacklist дублируется on-chain вызовом isBlackListed.
HOW VERIFIED: docs read (curl llms.txt и страницы common-network-auth) + живые keyless-вызовы (401/429).
CONFIDENCE: medium
EVIDENCE: https://docs.tronscan.org/llms.txt | https://docs.tronscan.org/en/api/common-network-auth | https://apilist.tronscanapi.com/api/accountv2?address=TR7NHqjeKQxGTCi8q8ZY4pL8otSzgjLj6t

### [RECOMMENDED] On-chain проверка blacklist USDT: isBlackListed(address) через TronGrid triggerconstantcontract
NEED: (a)/(b) первичный факт: заморожен ли адрес эмитентом Tether
KIND: public API
LICENSE: Публичные данные блокчейна; TronGrid — proprietary ToS
COMMERCIAL USE: Данные блокчейна публичны; условия TronGrid в этой области не проверялись (см. область blockchain-data).
PROJECT STATE: Работает: keyless POST вернул result=true, constant_result=0x0 для нулевого адреса, energy 4658, метка времени блока 2026-10-14.
CLAIMED VS ACTUAL: none found
CAPABILITIES: Детерминированный ответ по контракту TR7NHqjeKQxGTCi8q8ZY4pL8otSzgjLj6t: адрес в чёрном списке или нет. События AddedBlackList/DestroyedBlackFunds дают TXID заморозки.
INFRA: Нет
PRICING/LIMITS: $0 за вызов (constant call). Лимиты TronGrid — см. область blockchain-data.
RISKS: Показывает только состояние контракта, а не причину и не инициатора заморозки.
REPLACEABILITY: Высокая: любой TRON full node / другой RPC-провайдер.
HOW VERIFIED: API call made (keyless, read-only constant call)
CONFIDENCE: high
EVIDENCE: https://api.trongrid.io/wallet/triggerconstantcontract | https://tether.to/en/legal/

### [RECOMMENDED] OFAC SDN list (digital currency addresses) + зеркало 0xB10C/ofac-sanctioned-digital-currency-addresses
NEED: (a) OSINT об адресах: санкционные адреса TRON
KIND: dataset
LICENSE: Первичный источник OFAC — публичные данные США; инструмент-зеркало MIT
COMMERCIAL USE: Разрешено (MIT для инструмента; сами данные публичны).
PROJECT STATE: Репозиторий: MIT, 179 stars, не archived, CI generate-lists.yml, ветка lists обновлена 2026-10-01 (предыдущее обновление 2026-09-10). Файл sanctioned_addresses_TRX.json — 261 адрес.
CLAIMED VS ACTUAL: README говорит 'As of December 2023 the tool covers…' и предупреждает, что часть активов SDN может быть не покрыта. Зеркало обновляется раз в несколько недель, а не ежедневно — для актуальности парсить sdn_advanced.xml самим.
CAPABILITIES: Списки по активам: TRX (261), USDT, ETH, XBT, SOL, BSC, ARB и др. — пригодно и для расширения на другие сети.
INFRA: Ежедневный cron: скачивание списка, хранение локально с датой и хешем файла.
PRICING/LIMITS: $0
RISKS: Только санкции США; адрес в SDN — не метка 'скам' и не метка биржи.
REPLACEABILITY: Высокая: первичный XML OFAC, TRM Sanctions API.
HOW VERIFIED: gh api (метаданные, ветка lists, подсчёт адресов в JSON, README)
CONFIDENCE: high
EVIDENCE: https://github.com/0xB10C/ofac-sanctioned-digital-currency-addresses | https://www.treasury.gov/ofac/downloads/sanctions/1.0/sdn_advanced.xml

### [NEEDS-TRIAL] Chainabuse API (TRM Labs; преемник BitcoinAbuse)
NEED: (a) OSINT об адресах: пользовательские отчёты о мошенничестве
KIND: public API
LICENSE: 'License: Proprietary API'; Terms of Use v4 от 2025-01-20
COMMERCIAL USE: НЕ разрешено по умолчанию: Terms of Use дают лицензию 'solely for your personal, non-commercial use'. Коммерческое использование — только через Partner Access (по запросу, с рабочего email).
PROJECT STATE: Документация перенесена на docs.trmlabs.com (страницы изменены в апреле и июне 2026). GET https://api.chainabuse.com/v0/reports, Basic auth. Sanctions API Chainabuse помечен deprecated.
CLAIMED VS ACTUAL: Позиционируется как 'free' инструмент, но бесплатный ключ — 10 вызовов в месяц (1 вызов = до 50 отчётов), а ToS запрещает коммерческое использование. Цена партнёрского доступа не опубликована.
CAPABILITIES: Фильтр chain включает TRON (enum: BTC, ETH, TRON, SOL, …). Поля отчёта: id, createdAt, scamCategory, addresses, trusted, checked, losses, description. Evidence, геолокация и контакты через публичный API не отдаются.
INFRA: Нет
PRICING/LIMITS: Free: 10 calls/month. Partner: до 5,000 calls/hour, цена по запросу (hello@chainabuse.com).
RISKS: Отчёты пользовательские и не проверенные (есть флаги trusted/checked); риск ложных обвинений; без партнёрского договора использовать в SaaS нельзя.
REPLACEABILITY: Низкая: это крупнейшая открытая база жалоб с покрытием TRON.
HOW VERIFIED: docs read (docs.trmlabs.com), Terms of Use PDF прочитан целиком; живой вызов не делался (нужен аккаунт)
CONFIDENCE: high
EVIDENCE: https://docs.trmlabs.com/guides/chainabuse/getting-started-2-1.md | https://docs.trmlabs.com/api/chainabuse/reports/get-reports.md | https://chainabuse.com/ChainAbuse_TermsofUse.pdf | https://crypto.news/trm-labs-acquires-chainabuse/

### [NEEDS-TRIAL] GoPlus Security — Address Security API
NEED: (a) OSINT об адресах: риск-флаги адреса
KIND: public API
LICENSE: Proprietary; ToS не прочитаны
COMMERCIAL USE: Не подтверждено. Маркетинг: 'open, license-free' — это не лицензия; нужен письменный ответ GoPlus.
PROJECT STATE: Живой сервис: keyless GET вернул HTTP 200 за 0.5 с; supported_chains для address_security содержит Tron (id 'tron') среди 19 сетей.
CLAIMED VS ACTUAL: Лимиты противоречат друг другу: одна страница — free 150K CU/месяц, 30K CU/день, 150 CU/мин; другая — '100 call credits per minute'. Качество данных по TRON не подтверждено: в тестовом ответе все флаги 0 и data_source пуст.
CAPABILITIES: 20 флагов: phishing_activities, stealing_attack, money_laundering, sanctioned, blacklist_doubt, mixer, cybercrime, financial_crime, darkweb_transactions и др.; поле data_source.
INFRA: Нет
PRICING/LIMITS: Free tier (см. противоречие выше); платные пакеты $199–$3,499/месяц (search snippet).
RISKS: Непрозрачная методика; годится только как подсказка, не как основание для метки.
REPLACEABILITY: Высокая
HOW VERIFIED: API call made (2 keyless GET); цены — search snippet only
CONFIDENCE: medium
EVIDENCE: https://api.gopluslabs.io/api/v1/address_security/TT2T17KZhoDu47i2E4FWxfG79zdkEWkU9N?chain_id=tron | https://api.gopluslabs.io/api/v1/supported_chains?name=address_security | https://gopluslabs.io/en/security-api

### [ALTERNATIVE] TRM Labs free Sanctions Screening API
NEED: (a) OSINT об адресах: санкционный скрининг
KIND: public API
LICENSE: Proprietary
COMMERCIAL USE: Заявлен как бесплатный для крипто-платформ; текст условий не прочитан.
PROJECT STATE: Документация на docs.trmlabs.com; Chainabuse отсылает к нему как к замене своего deprecated Sanctions API.
CLAIMED VS ACTUAL: Заявлено покрытие 'TRON, Solana and 23 other blockchains' — маркетинговая строка; поддержка TRON именно этим эндпоинтом не подтверждена.
CAPABILITIES: POST /public/v1/sanctions/screening: есть ли у адреса санкционная экспозиция.
INFRA: Нет
PRICING/LIMITS: Без ключа: 1 req/sec и 100 req/day. С бесплатным ключом: 1000 req/sec, 100K req/day (по документации в пересказе поиска).
RISKS: Дублирует локальный список OFAC; внешняя зависимость.
REPLACEABILITY: Высокая (локальный список OFAC)
HOW VERIFIED: search snippet only (документация в пересказе); вызов не делался
CONFIDENCE: low
EVIDENCE: https://docs.trmlabs.com/api/sanctions/screening/submit-one-or-more-addresses-to-be-screened.md | https://www.trmlabs.com/post/trms-free-sanctions-screening-tool-goes-live

### [ALTERNATIVE] ScamSniffer scam-database
NEED: (a) OSINT: фишинговые домены и адреса
KIND: dataset
LICENSE: GPL-3.0
COMMERCIAL USE: Использовать как входные данные в SaaS можно; при распространении самого списка действует GPL-3.0. Real-time API — платный.
PROJECT STATE: 267 stars, не archived, коммиты ежедневно (последний 2026-10-13), 287 open issues, CI-workflows в репозитории нет.
CLAIMED VS ACTUAL: Заявлено 'Web3 blacklists', но все 2,530 адресов — EVM (0x…), адресов TRON — 0. Открытые данные отдаются с задержкой 7 дней.
CAPABILITIES: blacklist/domains.json (9.1 MB) и blacklist/address.json (2,530 адресов).
INFRA: Периодическая синхронизация файла
PRICING/LIMITS: Открытый список $0; real-time API $999/месяц.
RISKS: Для TRON MVP полезен только список доменов (если жертва называет сайт).
REPLACEABILITY: Высокая
HOW VERIFIED: gh api: метаданные, README, LICENSE, подсчёт адресов в address.json
CONFIDENCE: high
EVIDENCE: https://github.com/scamsniffer/scam-database

### [ALTERNATIVE] MetaMask eth-phishing-detect
NEED: (a) OSINT: фишинговые домены
KIND: dataset
LICENSE: DON'T BE A DICK PUBLIC LICENSE v1.2 (нестандартная, GitHub показывает NOASSERTION)
COMMERCIAL USE: Формально разрешено ('do whatever you like'), но лицензия нестандартная — юридическая неопределённость для коммерческого SaaS.
PROJECT STATE: 1,339 stars, не archived, pushed 2026-10-13.
CLAIMED VS ACTUAL: none found
CAPABILITIES: Списки фишинговых доменов Web3.
INFRA: Синхронизация файла
PRICING/LIMITS: $0
RISKS: Только домены, EVM-фокус, адресов TRON нет.
REPLACEABILITY: Высокая
HOW VERIFIED: gh api (метаданные, текст лицензии)
CONFIDENCE: medium
EVIDENCE: https://github.com/MetaMask/eth-phishing-detect

### [REJECTED] CryptoScamDB
NEED: (a) OSINT об адресах и доменах
KIND: dataset
LICENSE: blacklist — без лицензии; api — MIT
COMMERCIAL USE: Не определено (у основного набора данных нет лицензии).
PROJECT STATE: Заброшен: CryptoScamDB/blacklist последний push 2023-04-29, остальные репозитории 2018–2021. api.cryptoscamdb.org отвечает 502.
CLAIMED VS ACTUAL: Сторонние сервисы до сих пор называют CryptoScamDB источником данных, но API не работает и данные не обновляются с 2023 года.
CAPABILITIES: Исторический список URL и адресов, в основном Ethereum.
PRICING/LIMITS: $0
RISKS: Устаревшие данные, нет TRON, нет лицензии.
REPLACEABILITY: n/a
HOW VERIFIED: gh api (список репозиториев организации) + живой запрос к API (502)
CONFIDENCE: high
EVIDENCE: https://github.com/CryptoScamDB/blacklist | https://api.cryptoscamdb.org/v1/stats

### [REJECTED] BitcoinAbuse (и 'преемники')
NEED: (a) OSINT об адресах
KIND: dataset
LICENSE: n/a
COMMERCIAL USE: n/a
PROJECT STATE: Куплен TRM Labs в октябре 2023, данные влиты в Chainabuse.
CLAIMED VS ACTUAL: Самостоятельного преемника с API и покрытием TRON не найдено; фактический преемник — Chainabuse.
CAPABILITIES: Отдельного источника больше нет; только BTC.
PRICING/LIMITS: n/a
RISKS: Сайты-клоны под похожими именами — риск фишинга.
REPLACEABILITY: n/a
HOW VERIFIED: search snippet only (crypto.news о покупке)
CONFIDENCE: medium
EVIDENCE: https://crypto.news/trm-labs-acquires-chainabuse/

### [RECOMMENDED] Web3 is Going Great (molly/web3-is-going-great)
NEED: (a) OSINT об инцидентах
KIND: dataset
LICENSE: Текст — CC BY 3.0 Unported; код — MIT
COMMERCIAL USE: Разрешено при атрибуции (CC BY 3.0).
PROJECT STATE: 826 stars; код pushed 2026-01-21; лента /feed.xml обновлена 2026-10-12 — контент ведётся активно.
CLAIMED VS ACTUAL: API нет, только RSS. Сам проект пишет, что фиксирует 'only some' инцидентов. Релевантность TRON низкая.
CAPABILITIES: Курируемая хронология инцидентов со ссылками на источники; RSS-лента.
INFRA: RSS-поллер
PRICING/LIMITS: $0
RISKS: Уровень инцидентов, не адресов; авторская подача.
REPLACEABILITY: Высокая
HOW VERIFIED: gh api + curl feed.xml + страница /about
CONFIDENCE: high
EVIDENCE: https://github.com/molly/web3-is-going-great | https://www.web3isgoinggreat.com/about | https://www.web3isgoinggreat.com/feed.xml

### [ALTERNATIVE] SlowMist Hacked
NEED: (a) OSINT об инцидентах
KIND: dataset
LICENSE: 'SlowMist Hacked All Rights Reserved'; условий использования и API нет
COMMERCIAL USE: Не разрешено явно: только ссылаться, не копировать базу.
PROJECT STATE: Активна: 2,308 событий, суммарные потери около $39.08 млрд, последняя запись 2026-10-10.
CLAIMED VS ACTUAL: API, экспорта и лицензии нет; в отчётах SlowMist прямо сказано, что список не исчерпывающий.
CAPABILITIES: Дата, цель, описание, сумма, метод атаки, ссылка на источник; есть фильтр 'Tron Ecosystem'.
PRICING/LIMITS: $0 для ручного просмотра
RISKS: Массовый парсинг без разрешения — юридический риск.
REPLACEABILITY: Средняя
HOW VERIFIED: docs only (страница прочитана через WebFetch)
CONFIDENCE: medium
EVIDENCE: https://hacked.slowmist.io/

### [NEEDS-TRIAL] De.Fi REKT Database API
NEED: (a) OSINT об инцидентах
KIND: commercial SaaS
LICENSE: Proprietary
COMMERCIAL USE: Не описано; условия по запросу info@de.fi.
PROJECT STATE: Документация существует: GraphQL https://public-api.de.fi/graphql, заголовок X-Api-Key, ключ выдают по email.
CLAIMED VS ACTUAL: Цена кредитов не опубликована; покрытие Tron не подтверждено; страница базы de.fi/rekt-database рендерится на клиенте и не прочиталась.
CAPABILITIES: Запрос rekts — постраничные данные о взломах и эксплойтах; заявлено '35+ blockchains'.
PRICING/LIMITS: Кредитная модель: rekts = 3 кредита, лимит 100 запросов/мин; цена кредита неизвестна.
RISKS: Нельзя оценить стоимость и права до переписки.
REPLACEABILITY: Высокая
HOW VERIFIED: docs only
CONFIDENCE: low
EVIDENCE: https://docs.de.fi/api/api

### [RECOMMENDED] Brave Search API
NEED: (a) веб-поиск для OSINT agent
KIND: public API
LICENSE: Proprietary ToS (Last updated: 1 Sep, 2026)
COMMERCIAL USE: Да, платный коммерческий API. Ограничения: нельзя хранить/кэшировать Search Results кроме transient storage (ToS 3(b)(i)), нельзя перераспространять, нельзя использовать для обучения/оценки моделей (3(b)(xiii)). Атрибуция
необязательна.
PROJECT STATE: Действующий сервис с собственным индексом; новая модель цен 2026 года.
CLAIMED VS ACTUAL: '$5 free credits every month' — это не бесплатный план: для подписки нужна карта. Права на хранение результатов требуют отдельного плана; какого именно и по какой цене — не указано.
CAPABILITIES: Веб-поиск, Goggles, extra snippets; отдельный план Answers.
INFRA: Нет
PRICING/LIMITS: Search: $5 за 1,000 запросов ($0.005/запрос), $5 кредитов ежемесячно (~1,000 запросов), 50 QPS. Answers: $4/1,000 + $5 за 1M токенов, 2 QPS.
RISKS: В отчёт нельзя вкладывать сами результаты поиска — только URL и собственный снимок страницы.
REPLACEABILITY: Высокая: интерфейс 'query -> URLs' одинаков у всех провайдеров.
HOW VERIFIED: docs read (страница цен и ToS)
CONFIDENCE: high
EVIDENCE: https://brave.com/search/api/ | https://api-dashboard.search.brave.com/terms-of-service

### [ALTERNATIVE] Tavily Search API
NEED: (a) веб-поиск для OSINT agent
KIND: commercial SaaS
LICENSE: Proprietary Terms (Last updated: May 4, 2026)
COMMERCIAL USE: Да: 'solely for Customer's internal business purposes', интеграция в Customer Applications прямо разрешена; запрета на кэширование Output в тексте нет; запрещено строить конкурирующий продукт.
PROJECT STATE: Действующий сервис, ориентирован на LLM-агентов.
CLAIMED VS ACTUAL: На странице цен цена плана Project не читалась (placeholder); взята из документации ($30). RPM-лимиты на прочитанных страницах не указаны.
CAPABILITIES: Search (basic/advanced), Extract, Map, Crawl, Research.
INFRA: Нет
PRICING/LIMITS: Free 1,000 кредитов/месяц без карты; PAYG $0.008/кредит; Project $30 за 4,000; basic search = 1 кредит, advanced = 2; extract = 1 кредит за 5 URL.
RISKS: Метапоиск — происхождение выдачи непрозрачно; дороже Brave на запрос.
REPLACEABILITY: Высокая
HOW VERIFIED: docs read (pricing, api-credits, terms)
CONFIDENCE: high
EVIDENCE: https://www.tavily.com/pricing | https://docs.tavily.com/documentation/api-credits | https://www.tavily.com/terms

### [ALTERNATIVE] Exa API
NEED: (a) веб-поиск для OSINT agent
KIND: commercial SaaS
LICENSE: Proprietary (Terms — PDF, не прочитан)
COMMERCIAL USE: Не проверено.
PROJECT STATE: Действующий сервис.
CLAIMED VS ACTUAL: QPS-лимиты не опубликованы.
CAPABILITIES: Нейросетевой поиск, типы instant/fast/auto/deep, получение контента страниц.
PRICING/LIMITS: instant $4/1,000; fast и auto $7/1,000; deep $12/1,000; deep-reasoning $15/1,000; contents $1/1,000 страниц; бесплатно $10 кредитов (баланс восстанавливается до $10 первого числа месяца).
RISKS: Условия хранения результатов не проверены.
REPLACEABILITY: Высокая
HOW VERIFIED: docs read (pricing)
CONFIDENCE: medium
EVIDENCE: https://exa.ai/pricing

### [REJECTED] Serper (Google SERP API)
NEED: (a) веб-поиск для OSINT agent
KIND: commercial SaaS
LICENSE: Proprietary Terms (Updated on May 29, 2024)
COMMERCIAL USE: B2B-сервис; сам пишет, что отдаёт 'web-scraped data' и 'not affiliated with or endorsed by Google'.
PROJECT STATE: Действующий сервис.
CLAIMED VS ACTUAL: Самая низкая цена, но это скрейпинг Google без лицензии Google.
CAPABILITIES: Выдача Google в JSON.
PRICING/LIMITS: 2,500 запросов бесплатно; $50 за 50,000 ($1.00/1,000), 50 QPS; $375 за 500,000 ($0.75/1,000); кредиты действуют 6 месяцев.
RISKS: Юридический риск для коммерческого SaaS: идут процессы Google v. SerpApi (иск 2025-12-19, отклонён в июле 2026, исправленный иск 2026-08-10) и Reddit v. SerpApi (31.07.2026 иск в основном устоял).
REPLACEABILITY: Высокая
HOW VERIFIED: docs read (главная страница, terms) + search для судебных дел
CONFIDENCE: high
EVIDENCE: https://serper.dev/ | https://serper.dev/terms | https://seroundtable.com/google-lawsuit-serpapi-dismissed-41731.html

### [REJECTED] SerpApi
NEED: (a) веб-поиск для OSINT agent
KIND: commercial SaaS
LICENSE: Proprietary
COMMERCIAL USE: Да, но U.S. Legal Shield только с плана Production ($150/месяц).
PROJECT STATE: Действующий сервис; ответчик в делах Google v. SerpApi и Reddit v. SerpApi.
CLAIMED VS ACTUAL: Legal Shield (до $2 млн) не входит в планы Free, Starter и Developer.
CAPABILITIES: Выдача Google и других поисковиков.
PRICING/LIMITS: Free 250 запросов/месяц; Starter $25 за 1,000 ($0.025/запрос); Developer $75 за 5,000; Production $150 за 15,000.
RISKS: В 5 раз дороже Brave на запрос; исход судебных дел не определён.
REPLACEABILITY: Высокая
HOW VERIFIED: docs read (pricing) + search
CONFIDENCE: high
EVIDENCE: https://serpapi.com/pricing | https://www.loeb.com/fr/insights/publications/2026/08/reddit-v-serpapi-llc

### [REJECTED] Google Programmable Search — Custom Search JSON API
NEED: (a) веб-поиск для OSINT agent
KIND: public API
LICENSE: Google APIs ToS
COMMERCIAL USE: Недоступно для новых клиентов.
PROJECT STATE: Официально: 'closed to new customers'; действующие клиенты должны перейти на альтернативу до 2027-01-01.
CLAIMED VS ACTUAL: Многие руководства всё ещё рекомендуют этот API, но подключиться новому проекту нельзя.
CAPABILITIES: n/a
PRICING/LIMITS: Для действующих клиентов: 100 запросов/день бесплатно, далее $5/1,000, максимум 10,000/день.
RISKS: Закрытие сервиса.
REPLACEABILITY: n/a
HOW VERIFIED: docs read (официальная страница)
CONFIDENCE: high
EVIDENCE: https://developers.google.com/custom-search/v1/overview

### [REJECTED] X API (посты расследователей)
NEED: (a) публичные посты расследователей
KIND: public API
LICENSE: X Developer Agreement (не прочитан)
COMMERCIAL USE: Не проверено.
PROJECT STATE: С 2026-02-06 по умолчанию pay-per-use; тариф Basic закрыт для новых клиентов.
CLAIMED VS ACTUAL: Цены известны только из сторонних обзоров (июль–сентябрь 2026), официальная страница не прочитана.
CAPABILITIES: Чтение постов и профилей.
PRICING/LIMITS: Около $0.005 за возвращённый пост, около $0.010 за профиль; один поисковый вызов на 100 постов = $0.50.
RISKS: Один вызов съедает половину бюджета расследования; посты — непроверенные утверждения.
REPLACEABILITY: Высокая: посты находятся через веб-поиск.
HOW VERIFIED: search snippet only
CONFIDENCE: low
EVIDENCE: https://opentweet.io/x-api-pricing | https://bundle.social/blog/x-api-pricing-2026-costs-limits

### [RECOMMENDED] RDAP (bootstrap rdap.org + RDAP реестров)
NEED: (a) доменная разведка: регистрационные данные
KIND: standard
LICENSE: Открытый стандарт IETF; у каждого реестра свои Terms of Service (в ответе есть notices)
COMMERCIAL USE: Запросы допустимы; массовый сбор ограничен условиями реестров.
PROJECT STATE: С 2025-01-28 RDAP — основной источник регистрационных данных gTLD вместо WHOIS (по сообщениям о решении ICANN).
CLAIMED VS ACTUAL: none found
CAPABILITIES: Даты регистрации/изменения/истечения, статусы, nameservers, регистратор. Персональные данные владельца обычно скрыты.
INFRA: Нет
PRICING/LIMITS: $0, без ключа. Живой запрос: 200 за 0.8 с, redirect на rdap.verisign.com.
RISKS: Не все ccTLD поддерживают RDAP; владельца домена не раскрывает.
REPLACEABILITY: Высокая
HOW VERIFIED: API call made (keyless GET)
CONFIDENCE: high
EVIDENCE: https://rdap.org/domain/example.com | https://www.hlc.com/en/publications/domain-name-news-february-2025

### [ALTERNATIVE] crt.sh (Certificate Transparency)
NEED: (a) доменная разведка: сертификаты и поддомены
KIND: public API
LICENSE: Бесплатный сервис Sectigo без SLA; условия не проверены
COMMERCIAL USE: Не проверено.
PROJECT STATE: Нестабилен: два запроса JSON подряд вернули 502 Bad Gateway.
CLAIMED VS ACTUAL: Широко рекомендуется как надёжный источник, но в проверке не ответил ни разу.
CAPABILITIES: История сертификатов по домену — дата первого появления сайта, связанные поддомены.
PRICING/LIMITS: $0
RISKS: Нельзя ставить в критический путь; только best-effort с ретраями и кэшем.
REPLACEABILITY: Средняя: платный Cert Spotter (от $15/месяц, бесплатного API не найдено).
HOW VERIFIED: API call made (2 попытки, обе 502)
CONFIDENCE: high
EVIDENCE: https://crt.sh/?q=chainabuse.com&output=json | https://sslmate.com/pricing

### [ALTERNATIVE] urlscan.io
NEED: (a) доменная разведка: снимки и инфраструктура фишинговых сайтов
KIND: commercial SaaS
LICENSE: Terms (Last updated: July 22, 2020)
COMMERCIAL USE: 'Commercial use of any part of our service requires express written permission'; перепродажа и распространение данных запрещены.
PROJECT STATE: Действующий сервис (footer 2026).
CLAIMED VS ACTUAL: Щедрый бесплатный тариф, но для коммерческого продукта он недоступен без письменного разрешения.
CAPABILITIES: Сканирование URL, поиск по истории сканов, скриншоты, DOM, IP/ASN.
PRICING/LIMITS: Free: 5,000 public scans/день, 1,000 search requests/день, 10,000 result requests/день. Платно: Automate $5,000/год, Professional $1,250/месяц.
RISKS: Цена платного плана несоразмерна MVP.
REPLACEABILITY: Высокая
HOW VERIFIED: docs read (pricing, terms)
CONFIDENCE: high
EVIDENCE: https://urlscan.io/pricing/ | https://urlscan.io/terms/

### [REJECTED] VirusTotal Public API
NEED: (a) доменная разведка: репутация URL/доменов
KIND: public API
LICENSE: VirusTotal ToS
COMMERCIAL USE: Запрещено: 'The Public API must not be used in commercial products or services'.
PROJECT STATE: Действующий сервис.
CLAIMED VS ACTUAL: Бесплатный API существует, но не для коммерческих продуктов.
CAPABILITIES: Репутация URL, доменов, файлов.
PRICING/LIMITS: 500 запросов/день, 4 запроса/мин. Premium — цена по запросу.
RISKS: Нарушение условий при использовании в SaaS.
REPLACEABILITY: Высокая
HOW VERIFIED: docs read
CONFIDENCE: high
EVIDENCE: https://docs.virustotal.com/reference/public-vs-premium-api

### [REJECTED] SecurityTrails API
NEED: (a) доменная разведка: история DNS
KIND: commercial SaaS
LICENSE: Proprietary
COMMERCIAL USE: Не проверено.
PROJECT STATE: Страница цен вернула 403; сторонние каталоги пишут 'pricing custom'.
CLAIMED VS ACTUAL: Не удалось проверить ни цены, ни лимиты бесплатного тарифа.
CAPABILITIES: История DNS, поддомены, связанные домены.
PRICING/LIMITS: Не подтверждено.
RISKS: Enterprise-ценообразование.
REPLACEABILITY: Высокая
HOW VERIFIED: search snippet only
CONFIDENCE: low
EVIDENCE: https://securitytrails.com/corp/pricing | https://www.g2.com/products/securitytrails-api/pricing

### [RECOMMENDED] Tether — Law Enforcement Requests Policy
NEED: (b) заморозка USDT эмитентом
KIND: standard
LICENSE: n/a (официальная политика эмитента)
COMMERCIAL USE: n/a. Канал предназначен для правоохранительных органов.
PROJECT STATE: Политика: 'Last updated: January 3, 2018'. Terms of Service: 'Last updated: February 26, 2026'.
CLAIMED VS ACTUAL: В пресс-релизах Tether говорит о быстрых добровольных заморозках, но опубликованная политика не менялась с 2018 года и не описывает путь для жертвы. ToS не содержит обязанности замораживать или возвращать средства и снимает
ответственность за украденные токены. Утверждения, что Tether замораживает по прямому обращению жертвы, — только из блогов коммерческих фирм.
CAPABILITIES: Запросы информации и заморозки адресов 'should be accompanied by appropriate legal process' (production orders, search warrants, subpoenas, а также запросы о добровольном раскрытии). Контакт для органов: inforequests@tether.to.
Общий контакт: cs.tether.to.
PRICING/LIMITS: Бесплатно для органов.
RISKS: Жертва не может подать freeze request напрямую: нужен запрос органа. Заморозка — не возврат.
REPLACEABILITY: Нет
HOW VERIFIED: Текст политики и ToS прочитан из page-data JSON сайта tether.to; статистика — search (пресса)
CONFIDENCE: high
EVIDENCE: https://tether.to/en/legal/?tab=law-enforcement-requests | https://tether.to/en/legal/ | https://www.theblock.co/post/398599/tether-freezes-344-million-in-usdt-on-tron-after-wallets-flagged-by-u-s-authorities

### [ALTERNATIVE] T3 Financial Crime Unit (TRON, Tether, TRM Labs)
NEED: (b) заморозка USDT на TRON
KIND: standard
LICENSE: n/a
COMMERCIAL USE: n/a
PROJECT STATE: Запущен в августе–сентябре 2024. По сообщению от 2026-05-14 заморожено более $450 млн. Программа T3+ с 2025-08-12, первый участник — Binance. 23 юрисдикции.
CLAIMED VS ACTUAL: Публичного канала приёма обращений нет: официального сайта не найдено, t3fcu.io — припаркованный домен, t3fcu.com выставлен на продажу, t3fcu.org отвечает 404.
CAPABILITIES: Быстрая координация заморозок USDT на TRON по запросам органов, в срочных случаях в пределах 24 часов.
PRICING/LIMITS: n/a
RISKS: Любой сайт или email 'от имени T3 FCU' — вероятный фишинг. Жертва попадает в T3 FCU только через свой правоохранительный орган.
REPLACEABILITY: Нет
HOW VERIFIED: search (пресс-релизы TRM, TRON DAO, The Block) + curl по доменам
CONFIDENCE: medium
EVIDENCE: https://trondao.org/news/tether-tron-and-trm-labs-backed-t3-financial-crime-unit-tops-450-million-in-frozen-illicit-crypto-assets | https://www.trmlabs.com/resources/blog/t3-financial-crime-unit-launches-t3-global-collaborator-program-over-250m-in-criminal-assets-frozen-as-binance-becomes-first-member | https://t3fcu.io/

### [ALTERNATIVE] Circle — Stablecoin Access Denial Policy
NEED: (b) заморозка эмитентом (для сравнения)
KIND: standard
LICENSE: n/a
COMMERCIAL USE: n/a
PROJECT STATE: PDF создан 2026-05-28. USDC на TRON не выпускается с 2024-02-21.
CLAIMED VS ACTUAL: Пресса (ICIJ, Protos) сообщает о жалобах прокуроров на отказы Circle возвращать замороженные средства; Circle это оспаривает.
CAPABILITIES: Блокирует адрес только: по закону или приказу уполномоченного органа/суда США или Франции; по 'certain urgent law enforcement requests pending a valid court order'; по санкционным запросам; по приказам суда до завершения MLAT.
Суды США — Delaware или Massachusetts.
PRICING/LIMITS: n/a
RISKS: Для TRON MVP не применимо; понадобится при расширении на Ethereum/Solana.
REPLACEABILITY: Нет
HOW VERIFIED: PDF политики прочитан целиком; блог Circle о TRON прочитан
CONFIDENCE: high
EVIDENCE: https://6778953.fs1.hubspotusercontent-na1.net/hubfs/6778953/Blog%20Posts/Circle%20Stablecoin%20Access%20Denial%20Policy_pdf.pdf | https://www.circle.com/blog/circle-is-discontinuing-support-for-usdc-on-the-tron-blockchain | https://www.icij.org/investigations/coin-laundry/crypto-giant-circle-rebuffed-efforts-to-help-scam-victims-police-say/

### [ALTERNATIVE] Kodex (портал запросов правоохранительных органов)
NEED: (b) канал запросов к биржам
KIND: commercial SaaS
LICENSE: Proprietary
COMMERCIAL USE: n/a: доступ только для сотрудников органов с официальным email.
PROJECT STATE: Действующий; по официальным страницам бирж используется Binance, OKX, Bitget, Coinbase, HTX (для США).
CLAIMED VS ACTUAL: Позиционируется как защита от поддельных запросов; в 2024 году сообщалось о продаже доступа через скомпрометированные учётные записи органов.
CAPABILITIES: Единая верификация сотрудника и подача запросов (данные, заморозка, emergency).
PRICING/LIMITS: Бесплатно для органов.
RISKS: Платформа и жертва не могут и не должны регистрироваться в Kodex.
REPLACEABILITY: n/a
HOW VERIFIED: search (официальные страницы бирж в пересказе) + curl app.kodexglobal.com (200)
CONFIDENCE: medium
EVIDENCE: https://www.kodexglobal.com/ | https://404media.co/hackers-target-kodex-accounts-edrs

### [RECOMMENDED] Binance — Government Law Enforcement Request System и FAQ для жертв
NEED: (b) запросы к бирже
KIND: standard
LICENSE: n/a
COMMERCIAL USE: n/a
PROJECT STATE: Guidelines опубликованы на binance.com/…/law-enforcement/guidelines (снимок Wayback от 2026-08-18 существует). FAQ 'How to Report Stolen Funds Transferred to Binance'.
CLAIMED VS ACTUAL: Guidelines: 'not intended for private parties'. FAQ: Binance не может заморозить без официального freezing order. Срок предоставления police report для сохранения временной заморозки в разных версиях разный: 24 часа и 7 дней. По
данным NYT (в пересказе Unchained), с апреля 2025 иностранные запросы направляются через ОАЭ/MLAT — Binance замедление отрицает.
CAPABILITIES: Органы: регистрация в системе запросов с официального email, проверка доступа около 3 рабочих дней, обязательны копии официальных документов; для данных пользователя — court order или police order/warrant. Жертва: обращение в
Binance Support с описанием, TXID и ссылками на explorer, затем police report.
PRICING/LIMITS: Бесплатно
RISKS: Прочитать страницы напрямую не удалось (соединение с binance.com сбрасывается); данные из пересказа поиска.
REPLACEABILITY: Нет
HOW VERIFIED: search snippet only (официальные страницы binance.com в пересказе)
CONFIDENCE: medium
EVIDENCE: https://www.binance.com/en/support/law-enforcement/guidelines | https://www.binance.com/en/support/faq/how-to-report-stolen-funds-transferred-to-binance-360000006051 | https://unchainedcrypto.com/binance-routes-foreign-law-enforcement-requests-through-the-uae-frustrating-investigators-nyt-reports/

### [RECOMMENDED] OKX — Law Enforcement Request Guide
NEED: (b) запросы к бирже
KIND: standard
LICENSE: n/a
COMMERCIAL USE: n/a
PROJECT STATE: Guide обновлён 2026-08-03 (по пересказу поиска).
CLAIMED VS ACTUAL: Разные региональные версии страницы противоречат друг другу: Kodex или email; отдельные адреса для США и Европы (okcoin.com).
CAPABILITIES: Органы: Kodex portal; если не удаётся подключиться или emergency — enforcement@okx.com с объяснением. Нужны: подписанный court order и/или письмо на бланке органа, proof of authority, обзор инцидента, transaction hashes с
трассировкой до OKX; язык английский; адресовать 'OKX'. Жертва: поддержка OKX и полиция.
PRICING/LIMITS: Бесплатно
RISKS: По запросу самой жертвы заморозка не описана.
REPLACEABILITY: Нет
HOW VERIFIED: search snippet only
CONFIDENCE: medium
EVIDENCE: https://www.okx.com/help/okx-law-enforcement-request-guide | https://www.okx.com/en-us/help/what-should-i-do-during-or-after-a-scam

### [NEEDS-TRIAL] Bybit — Report Stolen Funds
NEED: (b) запросы к бирже
KIND: standard
LICENSE: n/a
COMMERCIAL USE: n/a
PROJECT STATE: Help Center статья 'How to Report Stolen Assets'; пресс-релиз 2025-09-29 о VIP-портале.
CLAIMED VS ACTUAL: Обработка без freezing order ограничена 'verified Bybit VIP users'. Официальный канал для органов (портал или email) на bybit.com не найден. Найден поддельный домен bybitexcai.com с 'политикой запросов' и адресом на amail.com.
CAPABILITIES: Жертва: форма Report Stolen Funds в Help Center; указать актив, сумму, адрес злоумышленника, описание, контакты; ответ до 12 часов. Без police report — сначала получить police report и freezing order.
PRICING/LIMITS: Бесплатно
RISKS: Канал для органов не подтверждён; риск фишинговых двойников.
REPLACEABILITY: Нет
HOW VERIFIED: search snippet only
CONFIDENCE: low
EVIDENCE: https://www.bybit.com/en/help-center/article/How-to-Report-Stolen-Assets | https://www.prnewswire.com/news-releases/bybit-launches-dedicated-vip-portal-for-stolen-fund-inflow-reporting-302569525.html

### [RECOMMENDED] HTX — Law Enforcement Requests
NEED: (b) запросы к бирже
KIND: standard
LICENSE: n/a
COMMERCIAL USE: n/a
PROJECT STATE: Страница htx.com/terms/legal; дата обновления не установлена.
CLAIMED VS ACTUAL: В деле Высокого суда Англии ответы HTX жертве названы 'formulaic' и 'dismissive and non-cooperative'; жертве рекомендовали обратиться в полицию.
CAPABILITIES: США: Kodex (app.kodexglobal.com/htx/signin). Материковый Китай: ls@htx-inc.com. Остальные: regulatory@htx-inc.com. Нужны: описание расследования, запрашиваемое действие, официальные письма, cryptocurrency tracing report где
уместно, контакты органа; адреса и хеши — в копируемом формате (таблица); язык английский.
PRICING/LIMITS: Бесплатно
RISKS: Неясно, какое юрлицо отвечает (спор FCA с Huobi Global S.A.).
REPLACEABILITY: Нет
HOW VERIFIED: search snippet only
CONFIDENCE: medium
EVIDENCE: https://www.htx.com/terms/legal | https://www.reedsmith.com/articles/english-high-court-grants-freezing-and-disclosure-orders-to-assist-in-attempt-to-recover-stolen-cryptocurrency/

### [RECOMMENDED] KuCoin — Law Enforcement Request Guidelines
NEED: (b) запросы к бирже
KIND: standard
LICENSE: n/a
COMMERCIAL USE: n/a
PROJECT STATE: Глобальные guidelines обновлены в июле 2025; EU-версия — в 2026.
CLAIMED VS ACTUAL: Старые объявления 2022 года указывают другой email (rbenquiries@kucoin.com) — устарело.
CAPABILITIES: KuCoin Information Request System: https://www.kucoin.com/legal/requests. ЕС: lawenforcement@kucoin.eu. Нужны: название органа и страны, proof of authority (фото удостоверения), email на государственном домене, официальный запрос
на английском; при трансграничном запросе — документы MLAT.
PRICING/LIMITS: Бесплатно
RISKS: Путь для жертвы не найден.
REPLACEABILITY: Нет
HOW VERIFIED: search snippet only
CONFIDENCE: medium
EVIDENCE: https://www.kucoin.com/legal/requests | https://www.kucoin.com/announcement/pl-pl-en-law-enforcement-request-guidelines

### [RECOMMENDED] Bitget — Law Enforcement Requests
NEED: (b) запросы к бирже
KIND: standard
LICENSE: n/a
COMMERCIAL USE: n/a
PROJECT STATE: Статья поддержки 12560603829062 в нескольких языковых версиях.
CLAIMED VS ACTUAL: Английская версия короче остальных — разделы про emergency и номер дела взяты из других языковых версий.
CAPABILITIES: Органы: документы на lawenforcement@bitget.com, затем аккаунт в Kodex; только официальный email; запросы через VPN не принимаются; Chrome или Edge; тип 'Emergency' для срочных. Жертва получает номер дела в полиции и передаёт его
Bitget.
PRICING/LIMITS: Бесплатно
RISKS: Перечень документов для заморозки не опубликован.
REPLACEABILITY: Нет
HOW VERIFIED: search snippet only
CONFIDENCE: medium
EVIDENCE: https://www.bitget.com/support/articles/12560603829062 | https://www.kodexglobal.com/customer-stories/bitget

### [RECOMMENDED] Gate — Law Enforcement Request Guidelines
NEED: (b) запросы к бирже
KIND: standard
LICENSE: n/a
COMMERCIAL USE: n/a
PROJECT STATE: Страница gate.com/legal/law-enforcement.
CLAIMED VS ACTUAL: Guidelines: не для частных расследователей и участников гражданских споров.
CAPABILITIES: Email regulatory@gate.com, английский язык, отправка с государственного домена, proof of authority, court order/subpoena/warrant или официальное письмо с печатью/подписью, хронология дела, точный перечень действий включая срок
заморозки.
PRICING/LIMITS: Бесплатно
RISKS: Путь для жертвы не найден.
REPLACEABILITY: Нет
HOW VERIFIED: search snippet only
CONFIDENCE: medium
EVIDENCE: https://gate.com/legal/law-enforcement

### [RECOMMENDED] MEXC — LEORS и Report Abnormal Funds
NEED: (b) запросы к бирже
KIND: standard
LICENSE: n/a
COMMERCIAL USE: n/a
PROJECT STATE: Портал https://www.mexc.com/support/requests/legal; статьи 'How to Report Stolen Funds Transferred into an MEXC Account' и 'Stolen Asset Handling Process'.
CLAIMED VS ACTUAL: Срок одобрения доступа в разных версиях: 3 и 15–20 рабочих дней. Одна страница требует запрос органа в течение 48 часов, другая — подтверждение принятия заявления полицией в течение 48 часов. Также требуется KYC заявителя на MEXC
или подтверждение личности.
CAPABILITIES: Органы: сначала одобрение доступа к LEORS; warrant или court order; английский или заверенный перевод; сохранение данных 90 дней. Жертва: тикет 'Report Abnormal Funds' с хронологией, видео/скриншотом вывода, адресами и TXID со
ссылками.
PRICING/LIMITS: Бесплатно
RISKS: Длительность временной заморозки — на усмотрение MEXC.
REPLACEABILITY: Нет
HOW VERIFIED: search snippet only
CONFIDENCE: medium
EVIDENCE: https://www.mexc.com/support/requests/legal | https://www.mexc.com/announcements/article/15440563148953

### [NEEDS-TRIAL] Kraken — legal inquiry form
NEED: (b) запросы к бирже
KIND: standard
LICENSE: n/a
COMMERCIAL USE: n/a
PROJECT STATE: Статья 'How do I submit a legal inquiry?' обновлена 2025-04-02. Transparency Report 2025: 7,957 запросов из 74 стран, данные выданы по 51.3%.
CLAIMED VS ACTUAL: Отдельный портал для органов, перечень документов и правила заморозки на прочитанной странице не описаны.
CAPABILITIES: Единая веб-форма для Compliance/Legal/Privacy (support.kraken.com/hc/forms/35862482750484).
PRICING/LIMITS: Бесплатно
RISKS: Канал для органов не подтверждён.
REPLACEABILITY: Нет
HOW VERIFIED: docs read (support.kraken.com) + search
CONFIDENCE: medium
EVIDENCE: https://support.kraken.com/articles/how-do-i-submit-a-legal-inquiry | https://www.payward.com/press-release/kraken-transparency-report-2025

### [NEEDS-TRIAL] Coinbase — law enforcement portal и civil subpoenas
NEED: (b) запросы к бирже
KIND: standard
LICENSE: n/a
COMMERCIAL USE: n/a
PROJECT STATE: Transparency Report 2025: 12,716 запросов, около 53% не из США.
CLAIMED VS ACTUAL: Справочные страницы разного возраста противоречат друг другу (портал или email). coinbase.com/legal/law_enforcement вернул 404, help-страница — 403.
CAPABILITIES: Органы: уголовные subpoena через app.kodexglobal.com/gov/signup; вопросы — subpoenas@coinbase.com. Гражданские subpoena — только через registered agent for service of process.
PRICING/LIMITS: Бесплатно
RISKS: USDT TRC20 на Coinbase — редкий сценарий; приоритет низкий.
REPLACEABILITY: Нет
HOW VERIFIED: search snippet only
CONFIDENCE: low
EVIDENCE: https://help.coinbase.com/en/coinbase/other-topics/legal-policies/who-do-i-contact-for-a-subpoena-request-or-dispute-or-to-send-a-legal-document | https://www.coinbase.com/blog/transparency-report-2025

### [RECOMMENDED] FBI IC3 (complaint.ic3.gov) и PSA I-082423
NEED: (b) полицейские каналы; основа шаблона заявления
KIND: standard
LICENSE: Публичный государственный ресурс США
COMMERCIAL USE: n/a. Заявление подаёт сама жертва.
PROJECT STATE: Портал отвечает 200. PSA 'FBI Guidance for Cryptocurrency Scam Victims' от 2023-08-24 — более новой версии не найдено.
CLAIMED VS ACTUAL: none found
CAPABILITIES: 'The most important information you can provide are transaction details': адреса, сумма и тип актива, дата и время, TXID. Плюс: как познакомились, переписка, домены и приложения, биржи, хронология.
PRICING/LIMITS: Бесплатно
RISKS: IC3 не гарантирует расследование; PSA предупреждает о мошеннических 'recovery'-сервисах.
REPLACEABILITY: n/a
HOW VERIFIED: docs read (PSA) + curl ic3.gov
CONFIDENCE: high
EVIDENCE: https://www.ic3.gov/PSA/2023/PSA230824 | https://complaint.ic3.gov/ | https://www.ic3.gov/CrimeInfo/CryptoCurrency

### [RECOMMENDED] Report Fraud (Великобритания; заменил Action Fraud)
NEED: (b) полицейские каналы
KIND: standard
LICENSE: Публичный государственный ресурс
COMMERCIAL USE: n/a
PROJECT STATE: Запущен 2025-12-04, оператор — City of London Police.
CLAIMED VS ACTUAL: Шотландия на момент запуска не входила (звонить 101); присоединилась ли в 2026 — не подтверждено. Hogan Lovells: суть сервиса осталась прежней.
CAPABILITIES: reportfraud.police.uk, телефон 0300 123 2040; Англия, Уэльс, Северная Ирландия; выдаётся crime reference number.
PRICING/LIMITS: Бесплатно
RISKS: Старое название 'Action Fraud' в шаблонах будет ошибкой.
REPLACEABILITY: n/a
HOW VERIFIED: search (gov.uk, techUK, Which?)
CONFIDENCE: medium
EVIDENCE: https://www.gov.uk/government/news/report-fraud-new-service-from-city-of-london-police | https://www.techuk.org/insights/news/report-fraud-service-replaces-action-fraud-as-uk-s-official-fraud-reporting-portal

### [ALTERNATIVE] Europol и INTERPOL (ориентиры)
NEED: (b) полицейские каналы
KIND: standard
LICENSE: n/a
COMMERCIAL USE: n/a
PROJECT STATE: Europol FAQ: 'Europol does not handle crime reports from citizens directly'. INTERPOL: сообщать в местную полицию; при мошенничестве сразу уведомить банк.
CLAIMED VS ACTUAL: Ни Europol, ни INTERPOL не принимают заявления от частных лиц; I-GRIP недоступен жертве напрямую. Страница Europol со списком стран рендерится на клиенте — список не прочитан.
CAPABILITIES: Europol ведёт страницу со ссылками на национальные порталы стран ЕС. INTERPOL I-GRIP — механизм остановки платежей между полицией и финансовыми организациями 196 стран.
PRICING/LIMITS: Бесплатно
RISKS: Письма 'от Europol/INTERPOL' жертве — типовой сценарий повторного обмана.
REPLACEABILITY: n/a
HOW VERIFIED: search (europol.europa.eu FAQ) + docs read (interpol.int)
CONFIDENCE: medium
EVIDENCE: https://www.europol.europa.eu/faq/can-i-report-crime-to-europol | https://www.europol.europa.eu/report-a-crime/report-cybercrime-online | https://www.interpol.int/en/Crimes/Financial-crime/Financial-crime-don-t-become-a-victim

### [NEEDS-TRIAL] Каналы стран СНГ и Центральной Азии
NEED: (b) полицейские каналы
KIND: standard
LICENSE: n/a
COMMERCIAL USE: n/a
PROJECT STATE: Официальные страницы не прочитаны; сведения из СМИ и памяток банков.
CLAIMED VS ACTUAL: Для Узбекистана онлайн-форма не найдена; для России точный URL не подтверждён; для Кыргызстана, Таджикистана, Беларуси онлайн-порталов не найдено. Нигде не найден отдельный порядок для криптовалютных краж.
CAPABILITIES: Казахстан: 102 или qamqor.gov.kz ('Подать заявление в полицию'). Украина: ticket.cyberpolice.gov.ua, callcenter@cyberpolice.gov.ua, 0 800 50 51 70. Россия: онлайн-приём МВД (региональный сайт), приложение 'МВД России', 102/112.
Узбекистан: 102, Центр кибербезопасности МВД.
PRICING/LIMITS: Бесплатно
RISKS: Всё в этом пункте — community-reported; до использования в продукте проверить по официальным сайтам.
REPLACEABILITY: n/a
HOW VERIFIED: search snippet only (СМИ, банковские памятки)
CONFIDENCE: low
EVIDENCE: https://www.bcc.kz/about/press-center/protect-against-scammers/ | https://netfreedom.org.ua/kudy-povidomyty-pro-shahrajstvo-povnyj-gajd-2026/ | https://www.spot.uz/ru/2025/05/30/cyber-crime/

### [ALTERNATIVE] SEAL 911 (Security Alliance)
NEED: (b) экстренная координация при крупных инцидентах
KIND: open-source
LICENSE: Репозиторий seal-911 — лицензия не указана
COMMERCIAL USE: n/a: волонтёрская группа, платных услуг не оказывает.
PROJECT STATE: Репозиторий обновлён 2026-10-13; контакт — Telegram bot t.me/seal_911_bot.
CLAIMED VS ACTUAL: README: тикеты берутся 'based on available bandwidth', длительную трассировку группа не ведёт и отсылает к коммерческим фирмам участников.
CAPABILITIES: Связь с доверенными специалистами по безопасности в экстренной ситуации.
PRICING/LIMITS: Бесплатно
RISKS: Не правовой канал; не для типовых розничных краж; риск поддельных ботов.
REPLACEABILITY: n/a
HOW VERIFIED: gh api (README)
CONFIDENCE: high
EVIDENCE: https://github.com/security-alliance/seal-911

### [NEEDS-TRIAL] Открытые шаблоны заявлений жертвы и freeze request
NEED: (b) шаблоны
KIND: standard
LICENSE: n/a
COMMERCIAL USE: n/a
PROJECT STATE: Готового поддерживаемого открытого набора шаблонов не найдено: поиск по GitHub дал 0 результатов. security-alliance/frameworks (pushed 2026-10-13, лицензия NOASSERTION) содержит incident-response шаблоны для команд протоколов, а
не для жертв.
CLAIMED VS ACTUAL: Шаблоны на сайтах юридических и 'recovery'-фирм — маркетинговые, без лицензии.
CAPABILITIES: Основа для собственных шаблонов: перечень полей FBI PSA I-082423 и опубликованные требования бирж (HTX, Gate, OKX, KuCoin, MEXC, Bybit).
PRICING/LIMITS: $0
RISKS: Шаблоны придётся писать самим и показывать юристу.
REPLACEABILITY: n/a
HOW VERIFIED: gh search + gh api code search
CONFIDENCE: medium
EVIDENCE: https://github.com/security-alliance/frameworks | https://www.ic3.gov/PSA/2023/PSA230824

## OPEN QUESTIONS FOR OWNER (researcher)
- В какой юрисдикции находится первая жертва? От этого зависят полицейский канал, язык шаблонов и применимый закон о персональных данных.
- Готовы ли вы подать заявку на Chainabuse Partner Access (нужен рабочий email компании)? Без неё Chainabuse нельзя использовать в коммерческом продукте.
- Кто зарегистрирует аккаунты и ключи TronScan и Brave Search API (Brave требует карту)? Я аккаунты не создавал.
- Платформа только формирует черновики запросов или должна сама отправлять их? Рекомендую в MVP только черновики.
- Где будет размещён сервер и будут ли клиенты из ЕС, Великобритании, Узбекистана, Казахстана, России? Это определяет GDPR-обязанности и локализацию данных.
- Какой потолок расходов на веб-поиск в одном расследовании? Предлагаю $0.05 по умолчанию и $0.10 максимум.
- Нужен ли в MVP модуль доменной разведки, или включать его только когда жертва называет сайт?
- Есть ли юрист, который проверит шаблоны заявлений и дисклеймеры до запуска платных тарифов?
- Планируется ли работа напрямую с правоохранительными органами как с клиентами? Тогда справочник должен содержать и путь для органов (Kodex и т.д.).
- С какой сети запускать регулярную сверку справочника получателей? С текущей машины сайты бирж недоступны.

## NOT VERIFIED (researcher)
- Точные тексты, даты и URL страниц бирж для органов (Binance, OKX, Bybit, HTX, KuCoin, Bitget, Gate, MEXC, Coinbase): прочитаны только в пересказе поиска, прямой доступ с этой машины заблокирован.
- Официальный канал Bybit для правоохранительных органов — не найден.
- Отдельный портал Kraken для органов (Kodex или иной) и требования к запросу.
- Текущая маршрутизация Coinbase (портал Kodex или subpoenas@coinbase.com): справочные страницы старые, прямое чтение дало 403/404.
- Срок предоставления police report для временной заморозки на Binance: 24 часа или 7 дней.
- Срок одобрения доступа к MEXC LEORS: 3 или 15–20 рабочих дней.
- Сообщение NYT о маршрутизации иностранных запросов Binance через ОАЭ с апреля 2025 — только пресса.
- Принимает ли Tether обращения жертв через cs.tether.to и замораживает ли без запроса органа — официального подтверждения нет.
- Порядок обращения в T3 FCU; официальный сайт не найден.
- Статистика Tether (340+ органов в 65 странах, $4.4 млрд заморожено, 2,300 или 2,900 дел) — пресса, цифры расходятся.
- TronScan: квоты и цена API key, условия использования, имена полей меток, доступность публичных комментариев через API.
- GoPlus: условия использования, фактические лимиты (два разных значения), качество данных по TRON.
- TRM Sanctions API: поддержка адресов TRON и актуальные лимиты.
- Chainabuse Partner Access: цена и условия.
- De.Fi REKT API: цена кредитов, покрытие Tron, коммерческие условия.
- SecurityTrails: цены и лимиты.
- Exa: условия использования (PDF не прочитан) и QPS.
- Brave: какой план даёт права на хранение результатов и его цена; допустимость передачи результатов в LLM для inference.
- Tavily: RPM-лимиты.
- Цены X API — только сторонние обзоры.
- SlowMist Hacked: условия использования, кроме надписи 'All Rights Reserved'.
- Каналы СНГ и Центральной Азии: онлайн-форма МВД Узбекистана, точный URL приёма МВД России, порядок qamqor.gov.kz, каналы Кыргызстана, Таджикистана, Беларуси, Армении, Азербайджана, Грузии.
- Присоединилась ли Шотландия к Report Fraud в 2026 году.
- Содержание EDPB Guidelines 02/2025 v2.0: PDF существует на сайте EDPB (200), но текст не прочитан — выводы из вторичных источников.
- Детали законов о локализации персональных данных Узбекистана, Казахстана, России — вторичные источники.
- Список стран на странице Europol 'Report cybercrime online' (рендерится на клиенте).
- Какие биржи кроме Binance, OKX, Bitget, Coinbase, HTX (США) используют Kodex.
- Надёжность crt.sh за пределами двух неудачных попыток.
- Лицензия security-alliance/frameworks (GitHub показывает NOASSERTION).