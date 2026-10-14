# AREA labels-risk: Address labels, attribution and risk data (incl. commercial analytics services)

============================================================
PART 1 - VERIFIER REPORT (takes precedence over the researcher wherever they disagree)
============================================================

## VERIFIER SUMMARY
Аудит фактологически добротен: из 25 перепроверенных утверждений 15 подтвердились по первичным источникам, включая все живые пробы, цены Bitquery, MistTrack, MetaSleuth и Nansen, лицензии репозиториев и подсчёты адресов. Но три
вывода, на которых держатся рекомендации, опровергнуты, и два из них меняют решение. **Что опровергнуто** - **Условия TronScan.** Аудит не нашёл их и рекомендовал теги TronScan как базовый слой. Terms of Service существуют
(2022-01-04) и запрещают сторонние приложения без письменного согласия и копирование данных без разрешения; разрешены только выдержки со ссылкой. Документация при этом требует API key и обещает 401 там, где сейчас отвечает 200. -
**Условия MistTrack и Bitquery.** Аудит счёл их отсутствующими. У MistTrack есть Terms of Use от 2026-10-09, прямо разрешающие клиентские PDF-отчёты, услуги расследования третьим лицам и кэширование. У Bitquery — Terms от
2026-10-12, разрешающие включение данных в отчёты. - **Открытые датасеты.** На HuggingFace есть архив заморозок Tether под CC BY 4.0 (27 538 событий, из них 18 846 на TRON), который аудит пропустил. **Что это меняет** - Базовый
слой остаётся, но без TronScan как хранимого источника до письменного согласия: опора на события Tether, OFAC (340 TRON-адресов, а не 261 + 79 как отдельные цифры) и собственный реестр PoR. - Для платной атрибуции стоит поменять
порядок: MistTrack с оплатой за вызов и лимитом 2–4 вызова на расследование — основной вариант для MVP, Bitquery — кандидат для массовой разметки после замера. Bitquery — самый непроверенный: меткам несколько месяцев, примеров
депозитных меток на TRON нет. - Рекомендации по санкциям, эвристике депозитных адресов и стоимости выдерживают проверку с поправками; шкалу достоверности нужно привести к GraphSense (эвристика не выше 0.2–0.3). **Главные
нерешённые вопросы** - Покрытие и точность меток депозитных адресов на TRON не измерены ни у одного вендора — нужен пробный прогон до выбора архитектуры. - Тестовый набор в предложенном составе не докажет 95% для класса депозитных
адресов: реально набрать 10–30 собственных адресов, а нужно минимум 73 безошибочных. **Что не удалось проверить** - Arkham (домен недоступен), бесплатные sanctions API Chainalysis и TRM, цены Phalcon (названия планов в аудите
устарели), эндпоинт Exchange Assets у CoinMarketCap. - Не подтверждено, что найденный PDF условий TronScan — действующая редакция, привязанная на сайте. - Поисковый бюджет сессии исчерпался на середине, поэтому поиск новых
участников рынка 2025–2026 годов неполон; CIS-ориентированные провайдеры (Bitrace, BitOK и подобные) не проверялись.

## BLOCKING RISKS
- Юридический блокер базового слоя: Terms of Service TronScan (2022-01-04) запрещают сторонние приложения без предварительного письменного согласия и копирование данных без письменного разрешения, разрешая лишь выдержки со ссылкой;
аудит считал условия отсутствующими. До письменного согласия TronScan теги нельзя класть в коммерческий Label Store.
- Техническая хрупкость того же слоя: официальная документация требует API key и обещает 401 для /api/account/tag без ключа, квоты ключа не опубликованы; сегодняшний keyless-доступ может исчезнуть без объявления.
- Нет ни одного проверенного источника меток депозитных адресов бирж на TRON: Bitquery (метки появились в мае–июле 2026) и MistTrack не вызывались вживую, покрытие и точность неизвестны. Ключевое обещание продукта — назвать биржу,
куда пришли средства — и цель >= 95% пока не обеспечены данными.
- Цель >= 95% недоказуема для самого важного класса: собственных депозитных адресов реально набрать 10–30, а для нижней границы Wilson >= 95% по классу нужно минимум 73 безошибочных примера. Без согласованного определения метрики
приёмка MVP зависнет.
- Фиксированная подписка против лимита $1: Bitquery $138/мес (годовая предоплата $1 656) или $198/мес превышает $1 на расследование при объёме ниже ~200 в месяц; MetaSleuth $599 и MistTrack Standard $689 — тем более.
- Условия MistTrack разрешают отчёты, но оставляют за вендором право KYB и проверки бизнес-модели и запрещают перепродажу данных как самостоятельного продукта — экспорт меток в машиночитаемом JSON-отчёте нужно согласовать письменно.
- Ни один источник не отдаёт происхождение и достоверность метки; нумерация и роли кошельков расходятся между источниками, а в открытых списках встречаются невалидные адреса (в файле Dune — три с испорченным регистром). Без
собственной нормализации и проверки base58check сверка источников даст ложные расхождения.
- Сетевая доступность: arkm.com и public.chainalysis.com недоступны и из сети исследователя, и из сети проверки; tronscan.org закрыт Cloudflare-challenge. Выбор хостинга влияет на набор доступных провайдеров.
- TronGrid без ключа ограничивает эндпоинт событий одним запросом в секунду с блокировкой на 5 секунд — первичная загрузка истории blacklist и регулярный cron требуют ключа и троттлинга, иначе джоб будет падать на 429.

## VERIFIER VERDICTS ON RECOMMENDATIONS

### NEED: (a) Слоистая стратегия меток — базовый бесплатный слой
PRIMARY: Собственный Label Store: Tether blacklist из on-chain events + OFAC SDN + реестр PoR-кошельков + TronScan tags
STANDS: False
ISSUE: Три источника из четырёх выдерживают проверку (события Tether, OFAC, PoR — подтверждены живыми запросами и юридически чисты). Четвёртый — нет: аудит объявил условия TronScan 'не найденными', а они есть и на первый взгляд запрещают
именно наш сценарий — сторонние приложения без предварительного письменного согласия (§6) и копирование данных без письменного разрешения (§8); разрешены только 'excerpts and links' с явной ссылкой. Плюс документация TronScan
прямо говорит, что /api/account/tag без ключа возвращает 401, то есть сегодняшний keyless-доступ — недокументированное послабление. Требование MVP 'лицензии и условия ДОЛЖНЫ разрешать коммерческий SaaS' для этого слоя не
выполнено. Дополнительно: шкала достоверности заявлена 'по образцу GraphSense', но расходится с ним (эвристика 0.4–0.6 против 10/100); у publicTag нет происхождения, а blueTag не заполнен даже у hot wallet Binance;
последовательный вызов /api/account/tag (0.55–0.67 с) на 1 000 адресов даёт 9–11 минут и ломает цель 5 минут.
SUGGESTED CHANGE: 1) До запуска получить письменное согласие TronScan на коммерческое использование и хранение тегов (ссылаясь на §6 и §8 ToS от 2022-01-04) и уточнить квоты ключа. 2) До ответа использовать теги TronScan только как не сохраняемую в
общий Label Store выдержку со ссылкой на страницу адреса и подписью источника; уровень L4 им не присваивать. 3) Опорой для класса 'биржа' сделать собственный реестр PoR (L2) и платную метку с явным разрешением в ToS (MistTrack).
4) Теги брать только из полей transfers, отдельный /api/account/tag — лишь для терминальных адресов. 5) Привести шкалу к GraphSense: эвристика не выше 0.2–0.3. 6) Добавить в слой бесплатные сверки: HuggingFace cryptoalert/usdt-
blacklist-archive (CC BY 4.0) против собственной таблицы blacklist. 7) В адаптере считать отсутствующие поля тега штатным случаем; валидировать base58check у всех внешних списков.

### NEED: Атрибуция депозитных адресов бирж и сервисов (платное обогащение)
PRIMARY: Bitquery Address Labels API (add-on к Pro) после trial; MistTrack Developer plan как эскалация на 1–3 терминальных адреса
STANDS: False
ISSUE: Цены и лимиты обоих вендоров подтверждены, но порядок выбран на неверной юридической посылке. Аудит считал, что ToS нет ни у кого; на деле у MistTrack есть Terms of Use от 2026-10-09, прямо разрешающие клиентские PDF-отчёты,
услуги расследования конечным клиентам и кэширование, а у Bitquery — Terms от 2026-10-12, разрешающие включение данных в отчёты (с оговоркой §3.3). Bitquery при этом самый рискованный по существу: метки появились в мае–июле 2026
года, в документации нет ни одного примера депозитной метки на TRON, живого вызова не было, а подписка $138/мес требует годовой предоплаты $1 656 (или $198 помесячно) и при менее чем ~200 расследованиях в месяц превышает $1 на
расследование. MistTrack оплачивается за вызов, не требует обязательств и исторически специализируется на TRON (у SlowMist есть открытый проект кластеризации TRON-адресов 2022 года) — но его покрытие депозитных адресов тоже не
измерено, а пакетного вызова нет.
SUGGESTED CHANGE: Поменять роли: для MVP основным платным источником сделать MistTrack Developer plan с жёстким лимитом 2–4 вызова address_labels на расследование ($0.15–0.20 за вызов на пакетах $150/$20, $0.10 на пакете $1 000 или через x402) —
это $0.30–0.80 в худшем случае и $0 при попадании в кэш. Bitquery оставить кандидатом для массовой разметки графов на 1 000 адресов и включать только после замера: в 7-дневном trial прогнать тестовый набор и убедиться, что cex-
deposit-address на TRON вообще возвращается (сначала выяснить у Bitquery, входит ли куб Labels в trial). До оплаты любого из них пройти Commercial Use Review у MistTrack (возможен KYB) и получить письменное подтверждение, что
экспорт меток в JSON-отчёте не считается 'independent data product'. Согласие двух вендоров не повышать до L3, пока не доказана независимость их методик.

### NEED: Санкции, заморозки и scam/risk-данные для TRON
PRIMARY: Tether blacklist из on-chain events (L0) + собственный разбор OFAC SDN_ADVANCED.XML (L1); опционально TRM free Sanctions API и приказы NBCTF
STANDS: True
ISSUE: Основа верна и перепроверена: события отдаются с TXID начиная с 2020-06-26, OFAC-экспорт свежий, GoPlus по TRON пуст, oracle Chainalysis заморожен, TronScan blackList отстаёт на часы. Неточности: утверждение 'нет бесплатного
источника scam-меток по TRON' завышено — у TronScan есть Security Service API (/api/security/account/data: has_fraud_transaction, fraud_token_creator, send_ad_by_memo, is_black_list; нужен бесплатный ключ, без ключа 401), который
аудит увидел только как '401' и не оценил; контрольная цифра OFAC неполна (TRX 261 и USDT-TRON 79 не пересекаются, всего 340); не учтён лимит TronGrid без ключа (1 rps, блокировка 5 с); не использован готовый независимый архив
заморозок на HuggingFace; уровень OFAC=0.95 при GraphSense authority_data=60 требует пояснения, что это достоверность факта включения в список, а не принадлежности.
SUGGESTED CHANGE: Оставить как есть, добавив: ключ TronGrid и троттлинг для первичной загрузки; сверку с cryptoalert/usdt-blacklist-archive и выборочно с isBlackListed; сбор TRON-адресов из всех тикерных списков OFAC; после урегулирования ToS —
флаги TronScan Security API как сигнал уровня L6 (происхождение флагов не раскрыто). Рассмотреть отслеживание заявок мультисига Tether до исполнения ('preban' в архиве cryptoalert) как ранний сигнал для recovery-агента — механика
на TRON в этой сессии не проверялась.

### NEED: Вывод депозитных адресов эвристикой deposit -> hot-wallet sweep и защита от ложных срабатываний
PRIMARY: Собственная детерминированная эвристика в baseline-трассировщике; результат только 'кандидат', никогда не метка 'биржа'
STANDS: True
ISSUE: Подход соответствует требованию MVP и консервативен. Замечания: достоверность 0.40–0.60 для чистой эвристики слишком высока относительно принятой таксономии; живое обоснование построено на нетипичном кошельке (TV6MuMXf — 5
входящих за 18 месяцев), хотя вывод подтверждается и на активном кошельке; условие 'адреса сущности уровня L2+' упирается в неполноту PoR-списков (операционные hot wallets в них часто отсутствуют), а TronScan-теги по ToS
использовать как опору проблематично; литература по методу известна только по аннотациям, один из идентификаторов arXiv приписан не той работе.
SUGGESTED CHANGE: Понизить confidence кандидата до 0.2–0.3 и выводить его отдельным блоком без слова 'биржа'; в отчёт всегда включать сам факт перевода на опубликованный кошелёк с TXID. Калибровать пороги на активных hot wallets, а не на архивных.
Добавить негативные признаки: адрес получает средства от многих несвязанных отправителей и рассылает на несколько сущностей; sweep идёт через промежуточный агрегатор; совпадение 'vanity'-префиксов у отправителей (в живой выборке 4
из 9 отправителей начинались на TQQ/TQq).

### NEED: (b) Независимый размеченный тестовый набор для цели >= 95%
PRIMARY: Составной набор на 400–500 адресов: собственные депозитные адреса, PoR-кошельки, ledger-immanent классы, судебные документы, Mendeley dataset, hard negatives
STANDS: True
ISSUE: Принцип (истина не из проверяемых источников) и статистика Wilson верны. Слабое место — самый важный класс: 60–100 собственных депозитных адресов на 8–10 биржах нереалистичны, обычно биржа выдаёт один TRC20-адрес на аккаунт или
суб-аккаунт, реальный выход — 10–30 адресов. Для нижней границы Wilson >= 95% по отдельному классу нужно минимум 73 безошибочных примера (30 из 30 дают лишь 88.6%), значит по классу 'депозитный адрес' цель статистически
недоказуема, а общая цифра будет вытянута лёгкими классами (hot/cold, замороженные). Классы Mendeley-набора неизвестны. Hard negatives 'из документации сервисов' собрать трудно: платёжные шлюзы и казино не публикуют депозитные
адреса.
SUGGESTED CHANGE: Заранее зафиксировать метрику как precision положительных меток по всему набору плюс отдельный отчёт по классам с интервалами, без обязательного порога для малых классов. Расширить источники истины по депозитным адресам: документы
о конфискации и судебные материалы, где биржа названа явно; собственные завершённые дела с письменным ответом биржи; партнёрские обменники, готовые подтвердить свои адреса (эти источники в сессии не проверялись — нужна отдельная
проработка). Класс 'frozen' брать из собственных событий и сверять с архивом cryptoalert. Hard negatives получать активным способом — собственными тестовыми платежами в шлюзы, swap-сервисы и казино с фиксацией TXID. Планировать
объём 600+ адресов, чтобы выдержать разбиение по классам.

### NEED: (c) Стоимость меток на одно расследование и лимиты
PRIMARY: $0 в бесплатном режиме и не более $0.10–0.30 в платном, не менее $0.70 остаётся на LLM
STANDS: True
ISSUE: Арифметика и цены подтверждены первичными страницами (Bitquery, MistTrack, Nansen, MetaSleuth). Уточнения: режим A опирается на TronScan, чьи условия требуют согласия; годовой тариф Bitquery — это предоплата $1 656; у MistTrack
нет batch, поэтому режим C стоит $0.20–0.40 только при пакетах $20/$100 и 2 вызовах, а реальный минимум $0.10 за вызов достигается пакетом $1 000 или x402 (x402 требует кошелька с USDC на Base и хранения приватного ключа на
сервере — отдельный операционный риск); расход points Bitquery на запрос меток прямо не опубликован (общее правило ~5 points за вызов, батч почти бесплатен).
SUGGESTED CHANGE: Оставить лимиты max_paid_label_calls и max_label_spend_usd, но стартовать с pay-per-call (MistTrack пакет $20 или $150) без фиксированных подписок; подписку вводить после достижения ~200 расследований в месяц и только по
результатам замера покрытия. x402 в MVP не использовать. Кэш меток с TTL учитывать в расчёте: повторные адреса (hot wallets, популярные обменники) быстро сводят платные вызовы к нулю.

## VERIFIER FACT CHECKS

- [REFUTED] TronScan tags :: Условия использования TronScan API найти не удалось; явного разрешения или запрета на коммерческое использование, кэширование и цитирование тегов нет
  CORRECT VALUE: Terms of Service существуют: PDF на официальном static-домене, 'Last updated: January 4, 2022' (HTTP Last-Modified 2022-01-04). §6 Acceptable Use запрещает 'Develop any third-party applications that interact with our Services
without our prior written consent' и автоматизированный сбор данных интерфейсами, 'not provided by us'. §8: вся 'information, data' — собственность Company; 'Unauthorized use and/or duplication of this material without express and
written permission ... is strictly prohibited. Excerpts and links may be used, provided that full and clear credit is given to TRONSCAN.io'. §1 исключает резидентов и организации материкового Китая, Тайваня, Гонконга, США и
Сингапура. §17 — право Сингапура. Не подтверждено только то, что именно этот PDF сейчас привязан в футере tronscan.org (сайт закрыт Cloudflare-challenge, обходить не стал).
  METHOD: PDF получен через WebFetch и разобран локально pypdf (11 страниц, полный текст прочитан); HEAD-запрос к файлу
  EVIDENCE: https://static.tronscan.org/pdf/TRONSCAN_Terms_of_Service.pdf

- [CORRECTED] TronScan tags :: docs.tronscan.org недоступен (Cloudflare 403); квоты ключа и уровни доступа не подтверждены
  CORRECT VALUE: docs.tronscan.org читается с обычным браузерным User-Agent (HTTP 200), есть llms.txt. Официально: 'An API Key is required for calling Mainnet endpoints'; для GET /api/account/tag прямо написано 'This endpoint requires API Key:
calls without a key return 401'; rate limiting 'global (not per-endpoint)', при 429 — Retry-After. Числовые квоты QPS/сутки в документации действительно НЕ опубликованы (страница API Keys, обновлена 2026-06-04). То есть
наблюдаемый keyless-доступ к /api/account/tag противоречит документации и может исчезнуть без объявления.
  METHOD: docs read (curl с браузерным UA: common-network-auth, api-keys, deep-analysis/account-tag, llms.txt)
  EVIDENCE: https://docs.tronscan.org/en/api/deep-analysis/account-tag

- [CORRECTED] TronScan tags :: GET /api/account/tag отвечает 200 без ключа, поля blueTag/publicTag/greyTag/redTag/chainTags/refreshTimeInfo; у санкционных и замороженных адресов redTag пустой
  CORRECT VALUE: Keyless 200 подтверждён (6 вызовов, 0.55–0.67 с): TQrY8tryqs... blueTag='Binance', publicTag='Binance 2'; TV6MuMXf... publicTag='Binance-Hot 2' при ПУСТОМ blueTag. Поправка: у адресов без тега (OFAC TA3rH2A7..., замороженный
Tether TZACYaKB...) полей blueTag/greyTag/redTag/publicTag в ответе НЕТ вообще (только chainTags и refreshTimeInfo), хотя документация помечает их как Required. Адаптер должен трактовать отсутствие ключа как 'нет тега'; blueTag
('official identifier' по документации) не заполнен даже у hot wallet Binance, поэтому фильтровать по нему нельзя.
  METHOD: API call made (keyless GET, 6 запросов)
  EVIDENCE: https://apilist.tronscanapi.com/api/account/tag?address=TZACYaKBQfwC5JdLh9xRBHisJ4teEQNywo

- [CONFIRMED] TronScan tags :: В /api/token_trc20/transfers теги приходят вместе с историей (from_address_tag/to_address_tag, riskTransaction), total ограничен 10000; депозитные адреса не размечаются
  CORRECT VALUE: Подтверждено: поля from_address_tag{from_address_tag, from_address_tag_logo}, to_address_tag{...}, riskTransaction; total=10000, rangeTotal=10000. Выборка исследователя (TV6MuMXf...) нерепрезентативна — это редко используемый
кошелёк (5 входящих за 18 месяцев). На активном кошельке TDqSquXBgUCLYvYC4XZgrprLK589dkhSCf ('Binance-Hot') за 6 минут 9 входящих sweep-переводов по ~112 USDT — все 9 отправителей без тега; 41 получатель без тега; у TNXoiAJ3...
('Binance-Hot 4') 50 из 50 получателей без тега. Вывод 'TronScan не размечает депозитные адреса' подтверждён на более показательной выборке.
  METHOD: API call made (keyless GET, 3 запроса)
  EVIDENCE: https://apilist.tronscanapi.com/api/token_trc20/transfers?limit=50&start=0&contract_address=TR7NHqjeKQxGTCi8q8ZY4pL8otSzgjLj6t&relatedAddress=TDqSquXBgUCLYvYC4XZgrprLK589dkhSCf

- [CONFIRMED] Tether frozen-address list (TronGrid events) + TronScan blackList :: TronGrid отдаёт AddedBlackList без ключа до блока 87075502; TronScan blackList total=7838 и отстаёт от сети
  CORRECT VALUE: Подтверждено: последнее событие block 87075502, block_timestamp 1791899394000 (2026-10-13 13:49:54 UTC), TXID d6520929...; hex 0x0684d2a2... = TAZgAu6wADSjXqV1gJE6AdFjPV1ptaEjLH (пересчитал base58check сам). История полная: самое
раннее событие — блок 20972943, 2020-06-26. TronScan total=7838, самая свежая запись 2026-10-12 19:01:06 UTC — события от 13.10 13:49 нет спустя ~7.8 ч. Дополнение, которого нет в аудите: без ключа на эндпоинте событий действует
allowed_rps=1 с блокировкой на 5 с (получил HTTP 429 на 2-м и 3-м запросе подряд) — для первичной загрузки и cron нужен ключ TronGrid и троттлинг.
  METHOD: API call made (TronGrid 5 GET, из них 3 с 429; TronScan blackList 2 GET)
  EVIDENCE: https://api.trongrid.io/v1/contracts/TR7NHqjeKQxGTCi8q8ZY4pL8otSzgjLj6t/events?event_name=AddedBlackList&limit=1&only_confirmed=true&order_by=block_timestamp,asc

- [CONFIRMED] OFAC SDN + 0xB10C/ofac-sanctioned-digital-currency-addresses :: MIT, 179 stars, pushed 2026-10-01; TRX.txt — 261 адрес, USDT.txt — 94 (79 TRON); SDN_ADVANCED.ZIP Last-Modified 2026-10-13 14:02 GMT
  CORRECT VALUE: Все цифры совпали (gh api: license MIT, stars 179, pushed_at 2026-10-01T07:15:12Z; 261 строк T...; USDT 94 = 79 TRON + 8 0x + прочие; контрольный адрес TA3rH2A7... присутствует; Last-Modified: Tue, 13 Oct 2026 14:02:04 GMT).
Уточнение для контрольных сумм: списки TRX и USDT НЕ пересекаются (overlap 0), полный набор TRON-адресов OFAC = объединение 340 адресов, плюс нужно просматривать остальные тикерные файлы (USDC и др.) на адреса формата T...
  METHOD: gh api + raw-файлы (подсчёт python) + HEAD к sanctionslistservice.ofac.treas.gov
  EVIDENCE: https://raw.githubusercontent.com/0xB10C/ofac-sanctioned-digital-currency-addresses/lists/sanctioned_addresses_TRX.txt

- [CONFIRMED] Bitquery Address Labels API :: Pro $69/мес (год) или $99/мес, 1M points, 90 req/min, 'Commercial-use license'; add-on Address labels $69/$99; trial 7 дней 1 000 points; до 100 адресов в запросе; типы включают cex-deposit-address; chain tron
  CORRECT VALUE: Подтверждено по pricing и docs: Personal $29/$49 ('no commercial use'), Pro $69/$99, Scale $199/$299; add-on labels $69 (год) / $99 (мес), 'stacks on any plan'; ~5 points за вызов, батч из 50 адресов стоит примерно как один; при
исчерпании — 402 или overage $35–50 за 1M. Docs: Address filter обязателен, 100 адресов, 'earlier versions are not kept'. Важно: продукт очень молодой ('Most Bitcoin labels carry 28 May 2026, the date of the first bulk load'),
единственный пример для Tron в документации — контракт USDT (token-contract); наличие и объём меток cex-deposit-address именно на TRON ничем не подтверждены. Включён ли куб Labels в trial — не указано.
  METHOD: docs read (HTML страницы скачан curl и прочитан целиком; pricing, how-billing-works, rate-limits через WebFetch). Живых вызовов нет (нужен аккаунт)
  EVIDENCE: https://docs.bitquery.io/docs/labels/address-labels-api/

- [REFUTED] Bitquery Address Labels API :: Условия перераспространения/цитирования меток не найдены: bitquery.io/terms -> 404
  CORRECT VALUE: Условия опубликованы по адресу /terms-of-service ('Updated date: October 12, 2026'; ссылка есть в футере pricing). §3.1: Subscriber may use 'any data or results obtained through the Services for any lawful commercial or non-
commercial purpose', включая 'inclusion in Subscriber's own products, services, reports, or applications' и 'use on behalf of its Clients'; лицензия non-sublicensable. §3.3 запрещает использование, которое 'directly substitutes
for the Services for a third party' или прямо конкурирует с Bitquery (оценка — на усмотрение Bitquery). Про кэширование и атрибуцию отдельных пунктов нет; §7 — нет гарантий точности.
  METHOD: terms read (WebFetch); наличие URL проверено curl (200), /terms действительно 404
  EVIDENCE: https://bitquery.io/terms-of-service

- [REFUTED] MistTrack OpenAPI (SlowMist) :: Terms of Service найти не удалось (terms-of-service.html -> 404); коммерческое использование и цитирование меток в отчётах клиентам документально не подтверждено
  CORRECT VALUE: Terms of Use опубликованы: /terms-of-use.html, 'Last Updated: October 9, 2026', раздел 'API Data Use, Commercial Applications and Redistribution'. Прямо разрешено: интеграция 'Risk Scores, Risk Levels, Address Labels ... into the
customer's own platform or services'; 'Creating customer-branded risk reports, PDF reports, charts, visualizations'; 'Providing commercial risk analysis, investigation, compliance ... services to end customers'; кэширование
('reasonably cache, store, process, and retain API results'). Ограничения: нельзя 'resell or redistribute MistTrack data itself as an independent data product'; MistTrack вправе потребовать KYB/KYC и проверить модель до начала
коммерческого использования; нельзя создавать впечатление одобрения отчёта MistTrack; право Гонконга. Это самое явное разрешение на сценарий LEDGERHUNT среди всех проверенных вендоров.
  METHOD: terms read (HTML скачан curl, раздел прочитан дословно; ссылка найдена в футере pricing.html)
  EVIDENCE: https://misttrack.io/terms-of-use.html

- [CONFIRMED] MistTrack OpenAPI (SlowMist) :: Developer plan: $20/100 вызовов ($0.20) ... $30 000/1M ($0.03), 10 rps; Standard $689/мес 1 rps 10k/сутки; Compliance $2 069/мес 5 rps 50k/сутки; trial $10 за 48 ч; x402 address_labels $0.1, risk_score $1.0; платежи не
возвращаются
  CORRECT VALUE: Все цифры совпали с pricing.html и llms-full.txt (122 897 байт). Уточнения: x402-строка risk_score в таблице ссылается на v2/risk_score (не v3); пакетного (batch) вызова меток в документации нет — 1 адрес = 1 оплачиваемый вызов;
существует ещё канал QuickNode add-on 'Address Risk Scores' (методы mt_addressLabel / mt_addressRiskScore, блокчейн TRON в списке параметров), на странице QuickNode цена 'From $99/mo', лимиты не указаны.
  METHOD: pricing через WebFetch + полный текст docs.misttrack.io/llms-full.txt скачан curl и разобран; страница QuickNode через WebFetch
  EVIDENCE: https://misttrack.io/pricing.html

- [CONFIRMED] BlockSec MetaSleuth Address Label API :: Address Label API $599/мес, Risk Score API $499/мес, 5 rps, Tron поддерживается, атрибуты DEPOSIT ADDRESS 4007 / HOT WALLET 4009, поля main_entity/comp_entity, покупка через Contact Us
  CORRECT VALUE: Подтверждено: plans — 'Address Label API $599/month ... 10k additional addresses per day', 'Risk Score API $499/month', кнопки Contact Us; docs — 'five requests per second', v3 https://aml.blocksec.com/address-label/api/v3/labels,
коды 4007 и 4009, comp_entity в схеме. Значение chain_id=-2 для Tron отдельно не перепроверял.
  METHOD: pricing через WebFetch + llms-full.txt (269 749 байт) скачан curl и разобран
  EVIDENCE: https://metasleuth.io/plans

- [CORRECTED] BlockSec Phalcon Compliance :: Планы Free / Screening Package / Standard (от $39) / Pro (от $699, API); пакет от $95 за 50 проверок
  CORRECT VALUE: В текущей документации планы называются Free, Credits (пакеты 50/100/200/500/1 000/2 000 проверок, срок 12 месяцев), Essential, Scale ('Higher screening volume, API access') и Enterprise. Названия Standard/Pro устарели. Конкретные
цены ($95, $39, $699) проверить не удалось: они на app.blocksec.com за авторизацией; маркетинговая страница даёт только 'From $0.10 per check'. Вывод аудита (API только в старшем подписочном плане) по смыслу сохраняется.
  METHOD: docs read (curl, markdown-страница) + WebFetch маркетинговой страницы; цены — не проверены
  EVIDENCE: https://docs.compliance.phalcon.blocksec.com/manual/account/plans-billing-and-payment.md

- [CONFIRMED] Dune Spellbook cex_tron.addresses :: BSL 1.1, запрет 'Data or Analytics Platform', Change Date 2027-03-03 -> GPL-3.0-or-later; 151 адрес; расхождение нумерации с TronScan
  CORRECT VALUE: Подтверждено дословно (Licensor Dune Analytics AS; Change Date Mar 3, 2027; 151 уникальный адрес; post_hook hide_spells; TQrY8tryqs... = 'Binance 7', TV6MuMXf... = 'Binance 1'). Дополнение: в файле есть заведомо невалидные адреса
с испорченным регистром (TCEM5YJJSYGW2RCXYXGE4SXLSPUUEJKQAW, TwsBSqwEEgtKMnhcLDnJowP6YpJUTEykMV, TjAQmFFRmVqtnkceGvLJrMwUPgCUfLjciu) — источник непригоден даже как справочный без проверки base58check.
  METHOD: code read (LICENSE и SQL через raw.githubusercontent.com) + gh api
  EVIDENCE: https://raw.githubusercontent.com/duneanalytics/spellbook/main/dbt_subprojects/hourly_spellbook/models/_sector/cex/addresses/chains/tron/cex_tron_addresses.sql

- [CORRECTED] GraphSense TagPacks / confidence taxonomy :: MIT; шкала ownership 100 ... authority_data 60, service_data 50, heuristic 10; уровни L0–L6 предложены 'по образцу GraphSense TagPack'
  CORRECT VALUE: Лицензии и значения шкалы подтверждены (confidence.csv прочитан; tagpack-tool archived=true, pushed 2025-09-04; graphsense-tagpacks pushed 2026-10-13). Но предложенная шкала аудита НЕ следует образцу: в GraphSense
authority_data=60 и service_data=50 (CSV от биржи), heuristic=10, а в аудите OFAC=0.95, PoR=0.90, эвристика 0.40–0.60. Эвристический кандидат с 0.6 выглядит почти как подтверждённая метка, что противоречит требованию MVP. Кроме
того, таксономия перенесена в активный graphsense-lib (MIT, pushed 2026-10-13) — ссылаться лучше на него, а не на архивный репозиторий.
  METHOD: code read (raw CSV) + gh api по трём репозиториям
  EVIDENCE: https://raw.githubusercontent.com/graphsense/graphsense-tagpack-tool/master/src/tagpack/db/confidence.csv

- [REFUTED] Открытые датасеты меток TRON на HuggingFace :: HuggingFace API по запросам tron/trc20/usdt/... не содержит пригодных датасетов; единственный релевантный — carrierone/verilex-address-labels
  CORRECT VALUE: По запросу 'usdt' HuggingFace API возвращает cryptoalert/usdt-blacklist-archive: лицензия CC BY 4.0, снимок 2026-09-07, 27 538 событий (TRON 18 846, Ethereum 8 692), 11 900 адресов, 7 946 сейчас заморожены; типы событий ban 12 179
/ preban 11 469 / destroy 2 338 / unban 1 552; файлы events.parquet, addresses.parquet, multisig_actions.parquet. Это готовая независимая сверка для собственной таблицы blacklist и источник класса 'frozen' для тестового набора.
Вывод об отсутствии открытых меток БИРЖ для TRON при этом остаётся верным.
  METHOD: API call made (huggingface.co/api/datasets, 10 поисковых запросов + карточка и README датасета); parquet-файлы не скачивались
  EVIDENCE: https://huggingface.co/datasets/cryptoalert/usdt-blacklist-archive

- [CONFIRMED] GoPlus address_security :: TRON заявлен, но для адреса из OFAC SDN все флаги 0, data_source пустой; free tier 150K CU/мес, 30k/сутки, 150/мин
  CORRECT VALUE: Подтверждено: для TA3rH2A7iHnm6pKH8gr9cK1EZnShnmZdFg все 19 флагов '0', sanctioned='0', data_source=''. Тарифная таблица: Free 150K CU/мес, 30k CU/сутки, 150 CU/мин; платные от $199/мес. Перепроверен 1 адрес из 3.
  METHOD: API call made (1 keyless GET) + pricing через WebFetch
  EVIDENCE: https://api.gopluslabs.io/api/v1/address_security/TA3rH2A7iHnm6pKH8gr9cK1EZnShnmZdFg?chain_id=tron

- [CONFIRMED] OKLink address-label API :: Explorer API закрыт: в документации остался только раздел Contract verification; Moralis сообщает о приостановке с 2025-05-20
  CORRECT VALUE: Подтверждено: в HTML oklink.com/docs/en (82 056 байт) заголовки только про Contract verification, 0 вхождений label/TRON/Explorer API; гайд Moralis: 'OKLink is suspending all their Explorer APIs on May 20th, 2025'. Официального
объявления самого OKLink не нашёл (поисковый бюджет сессии исчерпан).
  METHOD: docs read (curl, разбор HTML) + независимый источник (Moralis)
  EVIDENCE: https://docs.moralis.com/get-started/tutorials/migration-guides/migrating-from-ok-link-to-moralis

- [CONFIRMED] Chainalysis free sanctions screening :: Oracle deprecated, последнее обновление 2026-03-18, только EVM; public.chainalysis.com блокируется Cloudflare
  CORRECT VALUE: Подтверждено: 'Deprecated: The Chainalysis Sanctions Oracle is no longer supported or maintained', last update March 18, 2026, 10 EVM-сетей, TRON нет, замена — платный Address Screening. GET к public.chainalysis.com из сети
проверки вернул 403 'Sorry, you have been blocked'. Статус бесплатного REST API остаётся неизвестным.
  METHOD: docs read (WebFetch) + API call (1 keyless GET -> 403)
  EVIDENCE: https://go.chainalysis.com/chainalysis-oracle-docs.html

- [CONFIRMED] Chainabuse API :: Стандартный ключ — 10 вызовов в месяц (только search snippet); общий предел 5 000 calls/hour
  CORRECT VALUE: Подтверждено по первичной документации (readme.io, updatedAt 2025-09-08): 'standard API Key with a usage limit of 10 calls per month (1 call= maximum of 50 reports)'; partner access по заявке; 'Speed limit: max 5,000 calls/ hour'.
Там же: Chainabuse снимает с поддержки свой Sanctions API и отсылает к бесплатному Sanctions API TRM Labs.
  METHOD: docs read (curl, markdown-страница)
  EVIDENCE: https://chainabuse.readme.io/docs/getting-started-2-1.md

- [CONFIRMED] Nansen API :: Pro $49/мес (год) или $69/мес, 2 000 credits; profiler/address/labels = 100 credits, premium-labels = 500
  CORRECT VALUE: Подтверждено; уточнение — пустой ответ стоит 0 credits ('0 if the data is empty'). Поддержка TRON в labels-эндпоинте на странице не указана — остаётся непроверенной.
  METHOD: docs read (WebFetch)
  EVIDENCE: https://docs.nansen.ai/getting-started/credits.md

- [UNVERIFIABLE] Arkham Intelligence API :: Подписки от $100 или $900/мес, trial 1M credits, лимит 10 000 label lookups; arkm.com недоступен из сети аудита
  CORRECT VALUE: arkm.com недоступен и из моей сети (curl HTTP 000, WebFetch ECONNRESET), docs.intel.arkm.com и api-guide.intel.arkm.com редиректят на arkm.com/api/docs. Лично увидел только анонс 'The New Arkham API' от 2026-02-17 и страницу
codex.arkm.com (доступ через Google Form). Цены, ToS и метки депозитных адресов TRON не проверены.
  METHOD: curl (8 URL, 5 недоступны) + чтение анонса; остальное — только сниппеты
  EVIDENCE: https://info.arkm.com/announcements/the-new-arkham-api

- [CORRECTED] TronScan MCP Server :: Официальный TronScan MCP Server анонсирован 2026-03-09 (только заголовок из поиска)
  CORRECT VALUE: Статья поддержки датирована 2026-03-06 (обновлена 2026-10-08). Hosted-сервис https://mcp.tronscan.org/mcp, Streamable HTTP, протокол 2025-06-18, '119 tool interfaces', ключ опционально в заголовке TRON-PRO-API-KEY ('Default rate
limits apply'). Исходный код и лицензия не опубликованы. На него распространяются те же ToS TronScan.
  METHOD: docs read (curl) + статья support.tronscan.org
  EVIDENCE: https://docs.tronscan.org/en/mcp

- [CONFIRMED] Mendeley dataset 10.17632/62dmsngtfb.3 :: Версия 3 от 2026-08-03, CC BY 4.0, 1 150 меток, 1 024 адреса TRON TRC20-USDT, автор Meng Ling Tsai (Central Police University)
  CORRECT VALUE: Подтверждено. Классы и их количества на странице по-прежнему не раскрыты; оговорка Elsevier уточняет, что для open access 'the Creative Commons licensing terms apply'.
  METHOD: docs read (WebFetch); файлы не скачивались
  EVIDENCE: https://data.mendeley.com/datasets/62dmsngtfb

- [CORRECTED] Эвристика deposit -> hot-wallet sweep :: arXiv 2003.13399 — работа о 'fund gathering' на Ethereum; расчёт Wilson: 293/300, 389/400, 485/500 для нижней границы >= 95%
  CORRECT VALUE: Wilson-расчёт пересчитан и верен (197/200, 293/300, 389/400, 485/500, 964/1000; при ровно 95% нижняя граница 91.0% / 92.4% / 93.5%). arXiv 2003.13399 называется 'Cryptocurrency Address Clustering and Labeling' (2020-03-30) — это
не статья Victor (FC 2020); 2201.06811 — действительно Tutela. Содержание статей в этой сессии не читал.
  METHOD: arXiv API (1 GET) + собственный расчёт на python
  EVIDENCE: https://export.arxiv.org/api/query?id_list=2003.13399,2201.06811

- [UNVERIFIABLE] TRM Labs free Sanctions Screening API :: Без ключа 1 req/sec и 100 req/day; покрытие TRON
  CORRECT VALUE: Документация за логином (редирект на login.trmlabs.com). GET на api.trmlabs.com/public/v1/sanctions/screening вернул 405 — эндпоинт существует и ждёт POST; POST не делал (вне разрешённых проб). Лимиты и покрытие TRON остаются
непроверенными; косвенно существование бесплатного API подтверждает документация Chainabuse.
  METHOD: 1 keyless GET (405) + попытка чтения документации
  EVIDENCE: https://api.trmlabs.com/public/v1/sanctions/screening

## CANDIDATES MISSED BY THE RESEARCHER (found by verifier)

- TRONSCAN Terms of Service (первичный документ, пропущенный аудитом) (https://static.tronscan.org/pdf/TRONSCAN_Terms_of_Service.pdf)
  WHY: Определяет, можно ли вообще строить коммерческий продукт на тегах TronScan — рекомендованном базовом слое.
  ASSESSMENT: Прочитан полностью (11 страниц, 2022-01-04). Запрещает сторонние приложения без письменного согласия и копирование данных без разрешения; разрешает выдержки и ссылки с указанием источника; исключает резидентов США, Сингапура,
Гонконга, материкового Китая и Тайваня. Требует письменного запроса до запуска.

- TronScan Security Service API (/api/security/account/data, /api/security/transaction/data) (https://docs.tronscan.org/en/api/security-service-api/security-account)
  WHY: Бесплатные risk-флаги именно для TRON: has_fraud_transaction, fraud_token_creator, send_ad_by_memo, is_black_list — закрывает пробел 'нет бесплатного scam-источника'.
  ASSESSMENT: Документация прочитана (обновлена 2026-03-16); без ключа 401 (проверено). Нужен бесплатный API key. Происхождение и точность флагов не раскрыты, неверный адрес возвращает все false без ошибки. Пригоден как слабый сигнал L6 после
урегулирования ToS; живой вызов с ключом не делался.

- HuggingFace: cryptoalert/usdt-blacklist-archive (https://huggingface.co/datasets/cryptoalert/usdt-blacklist-archive)
  WHY: Независимый открытый архив всех действий Tether по blacklist на Ethereum и TRON — сверка собственной таблицы и готовый класс 'frozen' для тестового набора.
  ASSESSMENT: CC BY 4.0, снимок 2026-09-07, 27 538 событий (TRON 18 846), 11 900 адресов, 98 загрузок, автор cryptoalert.report. Данные не скачивал — качество и методику 'preban' нужно проверить; единственный мейнтейнер, обновление
нерегулярное. Использовать как сверку, не как первичный источник.

- MistTrack Terms of Use (первичный документ, пропущенный аудитом) (https://misttrack.io/terms-of-use.html)
  WHY: Единственные найденные условия вендора, прямо разрешающие клиентские PDF-отчёты, услуги расследования третьим лицам и кэширование результатов API.
  ASSESSMENT: Прочитан раздел 'API Data Use, Commercial Applications and Redistribution' (обновлён 2026-10-09). Ограничения: нельзя перепродавать данные как самостоятельный продукт; возможен KYB и проверка модели использования; право Гонконга.
Меняет расстановку в пользу MistTrack.

- Whale Alert Enterprise API (https://developer.whale-alert.io/api-account/documentation)
  WHY: Публичная цена и явные поля атрибуции owner, owner_type, address_type ('deposit_wallet, hot_wallet, cold_wallet'); Tron в списке сетей.
  ASSESSMENT: Enterprise API $699/мес, 500 запросов в минуту, история 90 дней; Alerts API $29.95/мес — только личное использование. Атрибуция привязана к транзакциям, а не к произвольному lookup адреса. Для MVP дорого, но это реальный источник
меток депозитных кошельков с открытым прайсом; условия перераспространения не читал.

- CoinMarketCap API — эндпоинт Exchange Assets (proof-of-reserves кошельки бирж) (https://coinmarketcap.com/api/pricing/)
  WHY: Агрегированные PoR-кошельки бирж через API с понятной лицензией — альтернатива DefiLlama-Adapters, у которого лицензии нет.
  ASSESSMENT: На странице тарифов эндпоинт 'Exchange Assets' указан в категории Exchanges; Basic бесплатно 15 000 credits/мес, в карточках планов значится 'Commercial use'. Доступность эндпоинта на бесплатном плане, наличие TRON-адресов и
условия кэширования НЕ проверены — нужен пробный вызов с ключом.

- bobslayerX/crypttrace (https://github.com/bobslayerX/crypttrace)
  WHY: Свежий (2026) открытый инструмент того же назначения: трассировка украденных средств на Ethereum, Bitcoin, Tron (TRX + USDT-TRC20), Solana, TON с модулем меток, аудитом меток и risk scoring.
  ASSESSMENT: MIT, 20 stars, создан 2026-07-21, релиз v0.16.0 от 2026-10-12, пакет на PyPI, CI selftest. В labels/known.json 82 TRON-адреса и 27 EVM, есть модули labels/audit.py и labels/bulk.py. Один автор, очень быстрый темп релизов —
зрелость низкая. Полезен как источник идей и MIT-кода для реестра меток; происхождение меток внутри файла не проверял.

- slowmist/automatic-tron-address-clustering (https://github.com/slowmist/automatic-tron-address-clustering)
  WHY: Открытая реализация SlowMist классификации TRON-адресов на hot wallet / cold wallet / common user (ML + графовые алгоритмы) — прямое отношение к задаче вывода ролей адресов.
  ASSESSMENT: Apache-2.0, 16 stars, единственный push 2022-11-11 (заброшен). Требует TRON full node + Kafka + Spark + Nebula Graph (16 ядер, 32 ГБ, 1.5 ТБ SSD) — не помещается в 'один скромный сервер'. Ценность — набор признаков и
подтверждение, что SlowMist специализируется на TRON-кластеризации.

- Open Labels Initiative (OLI) (https://github.com/openlabelsinitiative/OLI)
  WHY: Активный открытый стандарт модели данных для меток адресов — альтернатива формату GraphSense TagPack, чей инструмент заархивирован.
  ASSESSMENT: MIT, 122 stars, pushed 2026-10-02. Ориентирован на EVM; применимость к TRON и наличие TRON-меток не проверял. Рассматривать только как образец схемы.

- MistTrack через QuickNode add-on 'Address Risk Scores' (https://www.quicknode.com/add-ons/address-risk-scores)
  WHY: Альтернативный канал закупки тех же меток и risk score MistTrack с фиксированной ценой ниже плана Standard ($689/мес).
  ASSESSMENT: На странице 'From $99/mo', провайдер MistTrack; в документации MistTrack для add-on перечислен блокчейн TRON и методы mt_addressLabel / mt_addressRiskScore. Лимиты вызовов и требования к плану QuickNode не указаны — нужно
уточнение перед сравнением с pay-per-call.

- TronScan MCP Server (hosted) (https://docs.tronscan.org/en/mcp)
  WHY: Официальный MCP-доступ агентов к 119 инструментам TronScan, включая deep analysis и теги — аудит упомянул его только по заголовку из поиска.
  ASSESSMENT: https://mcp.tronscan.org/mcp, Streamable HTTP, ключ опционален. Закрытый hosted-сервис без опубликованной лицензии; действуют те же ToS и недокументированные лимиты. Для воспроизводимости и контроля расходов предпочтительнее
собственный типизированный адаптер к REST.

============================================================
PART 2 - RESEARCHER AUDIT
============================================================

## RESEARCHER RECOMMENDATIONS

### R1. NEED: (a) Слоистая стратегия меток с явными уровнями достоверности — базовый бесплатный слой
PRIMARY: Собственный локальный Label Store из первичных источников: (1) Tether blacklist из on-chain events через TronGrid; (2) OFAC SDN из официального SDN_ADVANCED.XML; (3) курируемый реестр PoR-кошельков бирж с официальных страниц бирж;
(4) TronScan tags (publicTag/blueTag и tag-поля в ответах transfers).
RATIONALE: Все четыре источника бесплатны, проверены живыми запросами 2026-10-13 и дают факты с проверяемым происхождением: заморозки — с TXID, санкции — с версией файла OFAC, кошельки бирж — со ссылкой на публикацию биржи. Теги TronScan
приходят вместе с историей переводов, то есть не добавляют ни запросов, ни задержки, что критично для целей 30 с / 2 мин / 5 мин. Ни один коммерческий провайдер не отдаёт source и confidence — значит, эти поля в любом случае
формируем сами.
ARCHITECTURE NOTES: Схема LabelRecord: address, chain, entity, category (exchange/otc/bridge/payment/mixer/scam/sanctioned/frozen/contract/unknown), subtype (hot/cold/deposit/reserve), source, source_url, raw_label, fetched_at, source_recorded_at,
confidence, method, evidence_txids[], response_hash. Уровни достоверности (по образцу GraphSense TagPack): L0 = 1.00 ledger-immanent (события Tether, тип контракта); L1 = 0.95 authority data как факт включения в список (OFAC SDN,
приказы NBCTF); L2 = 0.90 кошелёк, опубликованный самой биржей (PoR); L3 = 0.85 два независимых провайдера совпали на уровне сущности; L4 = 0.70 одна метка от провайдера (TronScan publicTag, Bitquery, MistTrack, BlockSec); L5 =
0.40-0.60 эвристический кандидат; L6 <= 0.30 пользовательские репорты и OSINT; иначе unknown. Правило отчёта: слово 'биржа' разрешено только при L4 и выше с явной меткой источника; L5 выводится как 'кандидат, не подтверждено'
отдельным блоком. Сравнение источников — только по нормализованной сущности (нумерация 'Binance 2' / 'Binance 7' у источников разная). Сырой ответ провайдера сохраняется в каждом расследовании, потому что метки меняются задним
числом.
COST: $0 переменных затрат. Трудозатраты: ~3-5 дней на джобы загрузки и схему, затем ~2-4 часа в месяц на курацию реестра PoR.
DATA QUALITY VERIFICATION: Ежедневная сверка: число записей blacklist в собственной таблице против TronScan /api/stableCoin/blackList (total) и выборочно против isBlackListed контракта; diff версий OFAC; для тегов TronScan — согласованность на уровне
сущности с реестром PoR (расхождения в отдельную очередь ручной проверки). Точность слоя измеряется на независимом тестовом наборе (см. отдельную рекомендацию).
RISKS: Условия использования TronScan не подтверждены; TronScan не размечает депозитные адреса и не помечает замороженные/санкционные адреса; списки PoR не включают все операционные кошельки; OTC и обменники СНГ не покрыты ничем
открытым.
REPLACEABILITY: Высокая: каждый источник за интерфейсом LabelProvider(address[]) -> LabelRecord[]; store переносим.
REJECTED ALTERNATIVES:
  - OKLink address-label API: Explorer API закрыт: в текущей документации остался только раздел Contract verification; Moralis сообщает о приостановке всех Explorer APIs с 2025-05-20.
  - Dune Spellbook cex_tron.addresses: BSL 1.1 с запретом использования в 'Data or Analytics Platform'; всего 151 адрес, без обновлений с 2025-08-19.
  - GoPlus address_security: TRON заявлен, но для адреса из OFAC SDN и адреса, замороженного Tether, вернул все нули.
  - GraphSense public TagPacks как источник данных: По TRON всего 8+13+4+7 адресов с датами 2022-2024; берём только шкалу confidence и формат.
  - Только коммерческий провайдер без собственного store: Нет provenance, нет истории версий меток, зависимость от одного вендора и его цен.

### R2. NEED: Атрибуция депозитных адресов бирж и сервисов (платное обогащение сверх базового слоя)
PRIMARY: Bitquery Address Labels API (add-on к плану Pro) — после 7-дневного trial с замером на независимом наборе; как эскалация для 1-3 терминальных адресов расследования — MistTrack OpenAPI Developer plan (pay-per-call).
RATIONALE: Деньги жертвы почти всегда заканчиваются на депозитном адресе, а бесплатные источники размечают только hot/cold. Из self-serve вариантов Bitquery единственный даёт фиксированную цену ($138/мес при годовой оплате или ~$198
помесячно), явный тип cex-deposit-address для tron, коммерческую лицензию в плане Pro и батч до 100 адресов — стандартное расследование закрывается одним запросом. MistTrack дороже за вызов, но тоже различает deposit/hot/cold и не
требует подписки — подходит для точечного второго мнения (уровень L3).
ARCHITECTURE NOTES: Порядок вызова: локальный store -> теги из уже полученных transfers -> батч Bitquery для неразмеченных адресов -> MistTrack только для терминальных адресов с наибольшей суммой и только если остался бюджет. Кэш меток с TTL 7-30
дней. Бюджетный guard на уровне оркестратора, а не агента.
COST: Bitquery: $138-198/мес фиксированно, на расследование около $0.46-0.66 при 300 расследованиях в месяц и $0.14-0.20 при 1 000; расход points на запрос Metadata.Labels не опубликован (ориентир ~5 points на вызов из '100k points ~
20k calls'). MistTrack: $0.20 за вызов на пакете $20, $0.10 на пакете $1 000; лимит 2-3 вызова на расследование = $0.20-0.60.
DATA QUALITY VERIFICATION: До оплаты: прогнать независимый тестовый набор через trial и посчитать precision по классу cex-deposit-address отдельно для каждой биржи с доверительным интервалом Wilson; сравнить с MistTrack (trial Standard — $10 за 48 часов) на
том же наборе; измерить долю расхождений между провайдерами. Принимать провайдера в L4 только при precision >= 95% на наборе.
RISKS: Методика депозитных меток у всех вендоров закрыта и может быть той же sweep-эвристикой — тогда согласие двух вендоров не является независимым подтверждением; нет полей source/confidence; права на цитирование меток в отчётах
третьим лицам ни у одного вендора не подтверждены; Bitquery правит метки без истории.
REPLACEABILITY: Высокая: провайдеры взаимозаменяемы за одним интерфейсом, включаются флагом и имеют отдельный бюджетный лимит.
REJECTED ALTERNATIVES:
  - BlockSec MetaSleuth Address Label API: $599/мес и покупка через 'Contact Us' при той же непрозрачности методики; оставить как запасной вариант, модель main_entity/comp_entity удачная.
  - Arkham Intel API: Цены и ToS не подтверждены (источники дают $100 и $900/мес), arkm.com недоступен из сети аудита; только после отдельного trial.
  - Nansen API: 100 credits за label lookup при 2 000 credits в плане $49 — около 20 запросов в месяц.
  - Phalcon Compliance: REST API только с плана Pro от $699/мес; малые пакеты — $1.90 за проверку.
  - AMLBot: API только в Pro+ через sales, цены противоречивы.
  - Chainalysis / TRM / Elliptic / Crystal / Scorechain / Merkle Science: Только enterprise-контракты (ориентир от $50 000 в год), вне рамок MVP.
  - slowmist/MistTrackMCP: Нет файла лицензии и тестов, ключ в аргументах командной строки, нет контроля расходов — проще собственный адаптер к двум эндпоинтам.

### R3. NEED: Санкции, заморозки и scam/risk-данные для TRON
PRIMARY: Tether blacklist из on-chain events (L0) + собственный разбор OFAC SDN_ADVANCED.XML (L1); опционально TRM free Sanctions API как независимая сверка и ручной ввод приказов NBCTF.
RATIONALE: Это единственные risk-данные, которые одновременно бесплатны, проверяемы по первичному источнику и юридически чисты. Живые проверки показали, что популярные 'бесплатные risk API' по TRON либо заморожены (Chainalysis oracle,
последнее обновление 2026-03-18, без TRON), либо пусты (GoPlus), а TronScan не ставит red tag ни санкционным, ни замороженным адресам и отстаёт от сети на часы.
ARCHITECTURE NOTES: Формулировки в отчёте строго фактические: 'адрес добавлен в blacklist контракта USDT транзакцией TXID ... от даты ...', 'адрес указан в OFAC SDN (версия файла от ...)'. Отсутствие в списках никогда не выводится как 'чистый'.
COST: $0.
DATA QUALITY VERIFICATION: Каждая запись о заморозке хранит TXID события и номер блока; тест: 100% адресов из выборки событий AddedBlackList без последующего RemovedBlackList должны давать isBlackListed = true. Для OFAC — контрольная сумма файла и число
TRX/USDT-адресов (на 2026-10-01: 261 TRX и 79 USDT на TRON).
RISKS: Нет бесплатного источника scam/phishing-меток по TRON с приемлемым качеством — категория 'scam' в MVP появится только из Chainabuse (после партнёрского доступа), ручной курации и платных провайдеров. Причина заморозки Tether on-
chain не раскрывается.
REPLACEABILITY: Высокая.
REJECTED ALTERNATIVES:
  - Chainalysis sanctions oracle / free API: Oracle deprecated и только EVM; REST API из сети аудита заблокирован Cloudflare, статус не подтверждён.
  - GoPlus address_security: Пропустил оба заведомо 'плохих' TRON-адреса.
  - OpenSanctions: CC BY-NC, для бизнеса нужна платная лицензия; основную ценность (OFAC) берём напрямую.
  - Chainabuse API: 10 вызовов в месяц на стандартном ключе; годится лишь для ручной проверки OSINT-агентом после получения партнёрского доступа.
  - Range / Webacy / HAPI / Breadcrumbs: Нет подтверждённой поддержки address risk для TRON.
  - MistTrack risk_score по x402: $1.0 за запрос — весь бюджет расследования.

### R4. NEED: Вывод депозитных адресов бирж на TRON эвристикой deposit -> hot-wallet sweep и защита от ложных срабатываний
PRIMARY: Собственная детерминированная эвристика в baseline-трассировщике, результат которой — только 'кандидат' (L5, confidence <= 0.6) и никогда не метка 'биржа'; повышение до L4+ только при явной метке deposit от провайдера.
RATIONALE: Требование MVP прямо запрещает называть адрес биржей по косвенному сходству. При этом сам факт 'адрес X переслал N USDT на кошелёк, опубликованный биржей Y, транзакцией TXID' — проверяемый и достаточен для запроса в биржу. Поэтому
в отчёт идёт факт перевода с TXID, а вывод о принадлежности — отдельной строкой с уровнем достоверности.
ARCHITECTURE NOTES: Условия кандидата (все одновременно): адрес — EOA; не менее 2 исходящих USDT-переводов; 100% исходящего объёма USDT уходит на адреса одной сущности уровня L2+; пересылка в пределах заданного окна и почти на всю полученную сумму; у
адреса нет исходящих на иные адреса; исключены адреса с признаками сервиса (очень много разных входящих контрагентов). Каждое условие сохраняется с TXID. Пороги — в конфиге и в журнале расследования.
COST: $0 на API; 1-2 дополнительных запроса истории на терминальный адрес.
DATA QUALITY VERIFICATION: Измерять precision и recall эвристики на тестовом наборе отдельно по двум классам: настоящие депозитные адреса (собственные аккаунты на биржах) и hard negatives (платёжные шлюзы, казино, OTC, swap-сервисы). Критерий допуска к
показу как 'кандидат': precision >= 90% на hard negatives; для утверждения 'депозитный адрес биржи Y' эвристика не используется вовсе.
RISKS: Платёжные процессинги, OTC/P2P-мерчанты, казино, instant-swap сервисы, omnibus-кастоди и white-label брокеры дают тот же паттерн; исходная метка hot wallet может быть ошибочной или устаревшей; биржи меняют схему сбора средств.
REPLACEABILITY: n/a (собственный код, параметры в конфигурации).
REJECTED ALTERNATIVES:
  - Правило 'любой отправитель на hot wallet = депозитный адрес': В живой выборке среди отправителей на Binance-Hot 2 были dust-переводы 0.0001 USDT и адрес с тегом другой биржи.
  - Кластеризация по общему источнику TRX/energy: Сервисы аренды energy и gas-sponsor адреса связывают несвязанных пользователей.
  - LLM-классификация адреса по 'похожести поведения': Не воспроизводима и прямо нарушает требование MVP; LLM допустим только для объяснения уже посчитанных признаков.

### R5. NEED: (b) Независимый размеченный тестовый набор (несколько сотен TRON-адресов) для проверки цели >= 95% без цикличности
PRIMARY: Составной ground-truth набор на 400-500 адресов, каждая метка которого получена НЕ из проверяемых источников: собственные депозитные адреса на биржах (ownership), кошельки из официальных PoR-публикаций (service data), ledger-
immanent классы, адреса из судебных и регуляторных документов, Mendeley judicial dataset, плюс вручную подобранные hard negatives.
RATIONALE: Цикличность возникает, когда истина берётся из того же источника или той же эвристики, что и предсказание (например, теги TronScan как эталон для разметки по TronScan). Собственные депозитные адреса — единственный способ получить
бесспорную истину по самому важному классу. Статистика: чтобы нижняя граница 95%-го интервала Wilson была не ниже 95%, нужно 293 верных из 300 (97.7%), 389 из 400 (97.25%), 485 из 500 (97.0%); при наблюдаемых ровно 95% на 400
адресах нижняя граница всего 92.4%.
ARCHITECTURE NOTES: Зафиксировать определение метрики до измерения: предлагается считать цель '>= 95%' как precision положительных меток exchange/service при обязательном отчёте о coverage; адрес без метки считается 'unknown', а не ошибкой. Те же
адреса использовать в 50+ тестовых сценариях как терминальные точки с известной истиной.
COST: Около $50-150 разово: комиссии сети и минимальные депозиты для активации адресов на 8-10 биржах, trial MistTrack $10; 5-8 человеко-дней на сбор и двойную ручную проверку.
DATA QUALITY VERIFICATION: Состав (ориентир): 60-100 собственных депозитных адресов (несколько аккаунтов и суб-аккаунтов на Binance, OKX, Bybit, HTX, KuCoin, Bitget, Gate, MEXC и 2-3 региональных; фиксируется скриншот/экспорт из кабинета и тестовый депозит
с TXID); 100-120 hot/cold из официальных PoR-страниц; 80-100 негативов уровня ledger (замороженные Tether адреса, контракты DeFi, собственные кошельки); 60-80 hard negatives (платёжные шлюзы, казино, OTC, swap-сервисы — источник:
документация и публичные адреса самих сервисов); 50-100 адресов из Mendeley dataset и судебных/seizure документов после проверки ролей. Набор заморожен и версионирован (hash), у каждой записи — источник истины и дата; разметку
независимо подтверждают два человека; набор хранится отдельно от Label Store и не попадает в него. Отчёт по метрикам: precision, recall и coverage по каждому классу и по каждой бирже, отдельно для baseline и для AI-слоя, с
интервалами Wilson. Раз в квартал — добавка свежих адресов (time split), чтобы ловить устаревание.
RISKS: Собственные аккаунты на биржах требуют KYC и дают мало адресов на аккаунт; перекос в сторону крупных бирж; Mendeley dataset может не содержать нужных классов и не проверяем по первоисточникам; PoR-кошельки и теги TronScan частично
восходят к одним и тем же публикациям бирж (это общая истина, а не цикличность, но независимость неполная).
REPLACEABILITY: n/a
REJECTED ALTERNATIVES:
  - Взять теги TronScan / Bitquery / MistTrack как эталон: Прямая цикличность: измеряется согласие источника с самим собой.
  - Dune Spellbook как эталон: Лицензия BSL и общее происхождение с другими списками.
  - Набор только из hot/cold кошельков крупных бирж: Даст завышенную точность: реальный трудный случай — депозитные адреса и похожие на них сервисы.
  - Мажоритарное голосование вендоров как истина: Вендоры могут использовать одну и ту же эвристику — ошибки коррелированы.

### R6. NEED: (c) Стоимость меток на одно расследование и лимиты
PRIMARY: Целевой бюджет на метки: $0 в бесплатном режиме и не более $0.10-0.30 в платном, чтобы не менее $0.70 оставалось на LLM-токены.
RATIONALE: Базовый слой бесплатен и не добавляет запросов (теги приходят в transfers; blacklist, OFAC и PoR — локальные таблицы). Платное обогащение выгодно только при фиксированной цене или при жёстком ограничении числа вызовов.
ARCHITECTURE NOTES: Конфигурируемые лимиты: max_paid_label_calls и max_label_spend_usd на расследование, суточный лимит на провайдера, приоритет терминальных адресов по сумме. Ключи провайдеров — только в secrets, в логах маскируются; в отчёт
попадает имя источника, но не ключ и не полный URL с параметрами авторизации.
COST: Режим A (только бесплатные источники): $0.00. Режим B (A + Bitquery labels, $138-198/мес): $0.14-0.20 на расследование при 1 000 в месяц, $0.46-0.66 при 300, $1.4-2.0 при 100 — то есть до ~200 расследований в месяц подписка не
укладывается в $1 и её следует относить к постоянным затратам. Режим C (A + MistTrack на 2 терминальных адреса): $0.20-0.40. Граф на 1 000 адресов: бесплатный слой $0; Bitquery — 10 батч-запросов; MistTrack не применять.
DATA QUALITY VERIFICATION: В журнале каждого расследования: число вызовов и стоимость по каждому провайдеру, доля адресов, размеченных из кэша, срабатывания бюджетных лимитов. Алерт при превышении $0.30 на метки.
RISKS: Цены вендоров меняются (на странице Bitquery уже два набора цифр); расход points на запрос меток не опубликован; при малом числе расследований фиксированная подписка формально нарушает лимит $1.
REPLACEABILITY: Высокая.
REJECTED ALTERNATIVES:
  - Разметка всех адресов графа через pay-per-call (MistTrack $0.10-0.20, Phalcon $1.90, Nansen ~$2.5+): 30-40 адресов дают $3-8 и более на расследование.
  - Подписка MistTrack Standard $689/мес на старте: Окупается только при ~700+ расследований в месяц с целевой долей $1.
  - Enterprise-вендоры: Фиксированные затраты от $50 000 в год.

## LIVE PROBE FINDINGS
- Время проб: 2026-10-13 21:05-21:20 UTC (заголовок Date сервера TronScan). Все запросы — keyless GET, без регистрации и ключей.
- TronScan GET /api/account/tag?address=TQrY8tryqsYVCYS3MFbtffiPp2ccyn4STm -> 200 без ключа: blueTag='Binance', publicTag='Binance 2', greyTag='', redTag='', chainTags (High Balance, Whale, Large Trader, High Activity),
refreshTimeInfo. Задержка 0.42-0.69 с (3 замера).
- TronScan GET /api/token_trc20/transfers (USDT, relatedAddress) -> 200 без ключа; в каждой записи есть from_address_tag / to_address_tag и riskTransaction; total ограничен 10000. Параметр toAddress -> 301 на
/api/new/token_trc20/transfers, который без ключа отдаёт 401.
- TronScan без ключа: /api/accountv2 -> 401, /api/security/account/data -> 401; то есть часть эндпоинтов уже закрыта, часть открыта — поведение не совпадает с формулировкой документации 'API key required'.
- TronScan не размечает депозитные адреса: из 27 входящих USDT-переводов в TV6MuMXfmLbBqPZvBHdwFsDnQeVfnmiuSi ('Binance-Hot 2') 26 отправителей без тега, 1 с тегом 'Bybit'; суммы входящих 0.0001, 1, 2, 4, 5, 6.211, 11.2, 12 USDT. 50
получателей от 'Binance 2' — все без тега.
- TronScan не помечает риск: redTag пуст у адреса из OFAC SDN (TA3rH2A7iHnm6pKH8gr9cK1EZnShnmZdFg), у адреса, замороженного Tether в 07.2025 (TZACYaKBQfwC5JdLh9xRBHisJ4teEQNywo), и у адреса, замороженного 2026-10-13
(TAZgAu6wADSjXqV1gJE6AdFjPV1ptaEjLH).
- Расхождение имён между источниками: TQrY8tryqs... — 'Binance 2' (TronScan) и 'Binance 7' (Dune Spellbook); TV6MuMXf... — 'Binance-Hot 2' (TronScan) и 'Binance 1' (Dune).
- TronGrid GET /v1/contracts/TR7NHqjeKQxGTCi8q8ZY4pL8otSzgjLj6t/events?event_name=AddedBlackList -> 200 без ключа; последнее событие в блоке 87075502 (block_timestamp 1791899394000 = 2026-10-13 13:49 UTC), TXID
d65209292728c7ad1f485eb6129d99128133effa677524b3009b5abbdda42340. События RemovedBlackList и DestroyedBlackFunds также отдаются (в последнем _balance = 517500000000, то есть 517 500 USDT).
- TronScan GET /api/stableCoin/blackList -> 200 без ключа, total=7838, limit допускается только в диапазоне [20,100]. При сортировке по времени самая свежая запись — 2026-10-12 19:01:06 UTC (совпадает со вторым по свежести событием
TronGrid); события от 2026-10-13 13:49 UTC в списке ещё не было спустя ~7.4 часа — список TronScan отстаёт от сети.
- 0xB10C/ofac-sanctioned-digital-currency-addresses (MIT, 179 stars): ветка lists обновлена 2026-10-01; sanctioned_addresses_TRX.txt — 261 адрес (все валидного формата T..., 34 символа); sanctioned_addresses_USDT.txt — 94 адреса, из
них 79 TRON и 8 в формате 0x. Официальный экспорт OFAC: HEAD https://sanctionslistservice.ofac.treas.gov/api/PublicationPreview/exports/SDN_ADVANCED.ZIP -> 200, Last-Modified 2026-10-13 14:02:04 GMT.
- GoPlus GET /api/v1/supported_chains?name=address_security -> в списке есть Tron (id 'tron'). GET /api/v1/address_security/{addr}?chain_id=tron для OFAC-адреса, для замороженного Tether адреса и для Binance hot wallet вернул
идентичный ответ: все 19 флагов '0' (sanctioned=0, blacklist_doubt=0), data_source пустой.
- Dune Spellbook: LICENSE — Business Source License 1.1, Additional Use Grant запрещает 'Data or Analytics Platform', Change Date 2027-03-03, Change License GPL-3.0-or-later. cex_tron_addresses.sql: 151 уникальный адрес, 30 бирж,
даты добавления 2024-04-19 ... 2025-08-19, депозитных адресов нет.
- DefiLlama-Adapters (license=null, 1267 stars, pushed 2026-10-13): TRON-адресов в адаптерах — gate-io 39, bitget 32, okex 30, kucoin 30, huobi 19, bitfinex 4, binance 3 статических, cex/index.js 77. Адаптер Binance использует
https://www.binance.com/bapi/apex/v1/public/apex/market/por/address — из сети аудита пустой ответ.
- GraphSense TagPacks (MIT, pushed 2026-10-13): TRON-адресов — Binance 8, Huobi 13, KuCoin 4, ofac.yaml 7; usdt_blacklist.yaml только ETH (lastmod 2023-02-22). Таксономия confidence прочитана из graphsense-tagpack-tool (репозиторий
archived).
- slowmist/MistTrackMCP: gh api license=null (файла LICENSE нет), package.json: license ISC, version 1.1.0, scripts.test = заглушка 'no test specified'; 12 MCP tools; pushed 2026-04-28.
- OKLink: HTML https://www.oklink.com/docs/en/ (82 KB) содержит только заголовки 'Developer tools', 'Contract verification', 'Contract verification plugin'; слов label / TRON / pricing нет. GET /api/v5/explorer/address/entity-label
без ключа -> 401 'Request header OK-ACCESS-KEY can not be blank'.
- Chainalysis: страница go.chainalysis.com/chainalysis-oracle-docs.html помечает Sanctions Oracle как Deprecated, 'Last oracle update was made on March 18, 2026', сети только EVM. GET
https://public.chainalysis.com/api/v1/address/{addr} -> страница 'Attention Required! | Cloudflare'.
- Arkham: arkm.com, www.arkm.com и intel.arkm.com недоступны из сети аудита (6 попыток, ECONNRESET / HTTP 000), codex.arkm.com отвечает 200 — документацию с ценами прочитать не удалось.
- HuggingFace datasets API: по запросам tron, trc20, usdt, address label, wallet labels, crypto labels, exchange addresses, blockchain labels датасетов меток TRON нет; carrierone/verilex-address-labels содержит только README ('211+
labeled Ethereum addresses').
- GitHub search (10 запросов через gh api): специализированных репозиториев меток TRON нет. Найдены свежие конкуренты-аналоги без лицензии: sidhy4rth/Exchequer (создан 2026-09-04) и rkhooda/TraceFall (создан 2026-09-05, TRON +
Ethereum, 'trace victim address to exchange') — сигнал о росте конкуренции в нише.
- Расчёт Wilson (z=1.96) для тестового набора: минимум верных ответов для нижней границы >= 95% — 197/200, 293/300, 389/400, 485/500, 964/1000; при наблюдаемых ровно 95% нижняя граница 91.0% (n=200), 92.4% (n=400), 93.5% (n=1000).

## CANDIDATES (full audit cards)

### [RECOMMENDED] TronScan tags (GET /api/account/tag + поля from_address_tag/to_address_tag в /api/token_trc20/transfers)
NEED: Базовые метки бирж/сервисов (hot/cold) для TRON
KIND: public API
URL: https://apilist.tronscanapi.com/api/account/tag
LICENSE: Проприетарный сервис; условия использования API не удалось прочитать (docs.tronscan.org и support.tronscan.org отдают Cloudflare 403)
COMMERCIAL USE: НЕ ПОДТВЕРЖДЕНО. Явного разрешения/запрета на коммерческое SaaS-использование, кэширование и цитирование тегов в отчётах найти не удалось — нужен письменный запрос в TronScan. До ответа: хранить тег как 'TronScan public tag' с
датой проверки и ссылкой на страницу адреса, не перепродавать как самостоятельный датасет.
PROJECT STATE: Сервис жив: 2026-10-13 21:05-21:20 UTC ~20 keyless GET-запросов, все 200/401 без 429. Политика API key ужесточается: объявления TronScan о mandatory API key (с 2025-08-31 QPS без ключа не гарантируется); 2026-03-09 анонсирован
официальный TronScan MCP Server (только search snippet).
CLAIMED VS ACTUAL: 1) Документация говорит 'API key required for Mainnet', фактически /api/account/tag, /api/token_trc20/transfers и /api/stableCoin/blackList отвечают 200 без ключа, а /api/accountv2, /api/security/account/data и
/api/new/token_trc20/transfers — 401. 2) Теги не являются источником санкций/заморозок: у адреса из OFAC SDN (TA3rH2A7...) и у двух адресов, замороженных Tether (TZACYaKB..., TAZgAu6w...), redTag пустой. 3) Нумерация кошельков не
совпадает с другими источниками: TQrY8tryqs... = 'Binance 2' у TronScan и 'Binance 7' у Dune; TV6MuMXf... = 'Binance-Hot 2' у TronScan и 'Binance 1' у Dune — сравнивать можно только на уровне сущности. 4) Параметр toAddress даёт
301 на /api/new/... который требует ключ.
CAPABILITIES: Поля ответа: blueTag (сущность, напр. 'Binance'), publicTag ('Binance 2'), greyTag, redTag, chainTags (поведенческие: Whale, High Activity), refreshTimeInfo. В transfers теги приходят бесплатно вместе с историей
(from_address_tag/to_address_tag, riskTransaction) — ноль дополнительных запросов. Покрывает hot/cold кошельки крупных бирж; депозитные адреса пользователей НЕ размечает (26 из 27 отправителей в Binance-Hot 2 без тега). Полей
source/confidence/date у тега нет.
INFRA: Бесплатный API key в заголовке TRON-PRO-API-KEY (хранить в secrets, маскировать в логах), локальный кэш меток с TTL и снимком сырого ответа.
PRICING/LIMITS: Бесплатно; точные квоты ключа (QPS/сутки) и наличие платных планов не подтверждены. Замер: /api/account/tag 0.42-0.69 с на запрос. transfers: total ограничен 10000, limit<=50; blackList: limit в диапазоне [20,100].
RISKS: Нет provenance и confidence у тега; нет истории изменений; условия использования не подтверждены; часть эндпоинтов закрыта без ключа; отставание списка blacklist от сети (см. live probes); нет депозитных адресов, OTC, обменников
СНГ.
REPLACEABILITY: Средняя: за адаптером LabelProvider; заменяется Bitquery/MistTrack/BlockSec, но бесплатного аналога с тегами прямо в transfers нет.
HOW VERIFIED: API call made (keyless, ~20 запросов); docs — только search snippets (страницы закрыты Cloudflare)
CONFIDENCE: high
EVIDENCE: https://apilist.tronscanapi.com/api/account/tag?address=TQrY8tryqsYVCYS3MFbtffiPp2ccyn4STm | https://docs.tronscan.org/en/api/common-network-auth | https://support.tronscan.org/hc/en-us/articles/49272903085465-Follow-up-Announcement-on-the-Mandatory-Requirement-of-API-Key-for-All-Requests | https://support.tronscan.org/hc/en-us/articles/55764103590553-TronScan-MCP-Server-Official-Launch-Announcement

### [RECOMMENDED] Tether frozen-address list из on-chain events USDT-TRC20 (AddedBlackList / RemovedBlackList / DestroyedBlackFunds) через TronGrid
NEED: Замороженные Tether адреса (первичный источник, ledger-immanent)
KIND: public API
URL: https://api.trongrid.io/v1/contracts/TR7NHqjeKQxGTCi8q8ZY4pL8otSzgjLj6t/events
LICENSE: Публичные данные блокчейна; TronGrid — сервис TRON DAO со своими условиями
COMMERCIAL USE: Данные блокчейна свободны; ограничения только по rate limits TronGrid (условия TronGrid в этой области не проверялись — см. аудит blockchain-data).
PROJECT STATE: Работает: 2026-10-13 keyless GET вернул события до блока 87075502 (2026-10-13 13:49 UTC). Все три события существуют и отдаются с TXID и block_timestamp.
CLAIMED VS ACTUAL: none found (события соответствуют ABI контракта). Замечание: адреса в событиях в hex (0x...), нужна конвертация в base58check с префиксом 41.
CAPABILITIES: Каждый факт заморозки имеет TXID (100% backing). Позволяет вести собственную таблицу blacklisted_at / unblacklisted_at / destroyed_amount. Для сверки: TronScan /api/stableCoin/blackList total=7838 записей; BlockSec сообщает 9 597
адресов на Ethereum+Tron на 2026-07-26.
INFRA: Фоновый джоб (cron 5-15 мин) + таблица в локальной БД; TronGrid API key.
PRICING/LIMITS: Бесплатно. Первичная загрузка ~7.8k событий = ~40 страниц по 200; дальше инкрементально по fingerprint/min_block_timestamp.
RISKS: Заморозка — не то же самое, что scam/санкции: причина блокировки on-chain не указана. Нужно учитывать RemovedBlackList (разморозки).
REPLACEABILITY: Высокая: любой TRON full node / другой indexer отдаёт те же события.
HOW VERIFIED: API call made (3 keyless GET к TronGrid, 4 к TronScan blackList)
CONFIDENCE: high
EVIDENCE: https://api.trongrid.io/v1/contracts/TR7NHqjeKQxGTCi8q8ZY4pL8otSzgjLj6t/events?event_name=AddedBlackList&limit=3&only_confirmed=true | https://apilist.tronscanapi.com/api/stableCoin/blackList?limit=20&start=0 | https://blocksec.com/blog/usdt-blacklist-explained-2026

### [RECOMMENDED] OFAC SDN digital-currency addresses (официальный SDN_ADVANCED.XML) + 0xB10C/ofac-sanctioned-digital-currency-addresses как образец парсера
NEED: Санкционные адреса (authority data)
KIND: dataset
URL: https://github.com/0xB10C/ofac-sanctioned-digital-currency-addresses
LICENSE: Данные OFAC — public domain правительства США; репозиторий 0xB10C — MIT
COMMERCIAL USE: Разрешено (MIT + государственные данные).
PROJECT STATE: 0xB10C: 179 stars, не archived, pushed 2026-10-01, CI workflow generate-lists.yml (cron '24 1 * * *'), ветка lists обновлена 2026-10-01 (предыдущее 2026-09-10); тестов нет. Официальный экспорт OFAC SLS жив: HEAD 200, Last-Modified
2026-10-13 14:02 GMT.
CLAIMED VS ACTUAL: README заявляет ночное обновление; фактически коммит появляется только при изменении списка (последний 2026-10-01) — это нормально, но дату свежести надо брать из самого SDN-файла, а не из репозитория.
CAPABILITIES: В ветке lists: sanctioned_addresses_TRX.txt — 261 TRON-адрес (все T..., 34 символа); sanctioned_addresses_USDT.txt — 94 адреса, из них 79 TRON. Формат TXT/JSON.
INFRA: Ежесуточный джоб, хранение версии файла (hash + Last-Modified) для воспроизводимости.
PRICING/LIMITS: Бесплатно, без лимитов (один файл в сутки).
RISKS: Только OFAC; EU/UK/UN списки крипто-адресов почти не содержат. Зависимость от стороннего репозитория нежелательна — лучше парсить SDN_ADVANCED.XML самим (скрипт ~150 строк, логика видна в workflow).
REPLACEABILITY: Высокая (bitnob/ofac-address-feed MIT, pushed 2026-10-13, 2 stars — альтернативный парсер; либо собственный).
HOW VERIFIED: code read (workflow) + API call (gh api, raw-файлы, HEAD к sanctionslistservice.ofac.treas.gov)
CONFIDENCE: high
EVIDENCE: https://github.com/0xB10C/ofac-sanctioned-digital-currency-addresses/tree/lists | https://raw.githubusercontent.com/0xB10C/ofac-sanctioned-digital-currency-addresses/main/.github/workflows/generate-lists.yml | https://sanctionslistservice.ofac.treas.gov/api/PublicationPreview/exports/SDN_ADVANCED.ZIP

### [RECOMMENDED] Exchange proof-of-reserves wallets (официальные PoR-публикации бирж; агрегировано в DefiLlama/DefiLlama-Adapters)
NEED: Hot/cold кошельки бирж с происхождением от самой биржи; ground truth для тестового набора
KIND: dataset
URL: https://github.com/DefiLlama/DefiLlama-Adapters
LICENSE: DefiLlama-Adapters: файл LICENSE отсутствует (gh api: license=null). Сами адреса — факты, опубликованные биржами.
COMMERCIAL USE: Адреса как факты использовать можно, но копировать код/конфиги репозитория без лицензии нельзя. Рекомендация: брать адреса с официальных PoR-страниц бирж (источник = биржа), а DefiLlama использовать как указатель и средство
сверки.
PROJECT STATE: 1267 stars, pushed 2026-10-13, не archived, очень активен.
CLAIMED VS ACTUAL: Адаптер Binance ссылается на https://www.binance.com/bapi/apex/v1/public/apex/market/por/address — из сети аудита endpoint вернул пустое тело (не подтверждён). PoR-списки покрывают резервные кошельки, но не обязательно все
операционные hot wallets.
CAPABILITIES: Подсчёт TRON-адресов (regex по raw-файлам): gate-io 39, bitget 32, okex 30, kucoin 30, huobi 19, bitfinex 4, coinex 1, binance 3 статических + динамический PoR endpoint; cex/index.js — 77 уникальных TRON-адресов в ~63 inline-
конфигах. Только reserve/hot/cold; депозитных адресов нет.
INFRA: Ручная/полуавтоматическая курация YAML-реестра (entity, address, source_url, published_at, checked_at).
PRICING/LIMITS: Бесплатно.
RISKS: Нет лицензии у агрегатора; биржи меняют кошельки; PoR-адрес может быть кастодиальным (omnibus у Ceffu/Cobo/Fireblocks); покрытие мелких бирж и обменников нулевое.
REPLACEABILITY: Высокая: первоисточник — сами биржи.
HOW VERIFIED: code read (raw index.js нескольких адаптеров, подсчёт адресов) + gh api
CONFIDENCE: medium
EVIDENCE: https://raw.githubusercontent.com/DefiLlama/DefiLlama-Adapters/main/projects/okex/index.js | https://raw.githubusercontent.com/DefiLlama/DefiLlama-Adapters/main/projects/binance/index.js | https://raw.githubusercontent.com/DefiLlama/DefiLlama-Adapters/main/cex/index.js

### [NEEDS-TRIAL] Bitquery Address Labels API (cube Metadata.Labels)
NEED: Атрибуция депозитных адресов бирж на TRON (self-serve, фиксированная цена)
KIND: commercial SaaS
URL: https://docs.bitquery.io/docs/labels/address-labels-api/
LICENSE: Проприетарный; планы Pro/Scale включают 'Commercial-use license' (pricing page)
COMMERCIAL USE: Да на Pro и выше (Personal — 'no commercial use'). Условия перераспространения/цитирования меток в отчётах третьим лицам не найдены (bitquery.io/terms -> 404) — уточнить письменно.
PROJECT STATE: API новый: примеры в документации с RecordedAt 2026-07-22 и 2026-07-31. Документация и pricing доступны.
CLAIMED VS ACTUAL: Заявлено определение per-user deposit address, но методология (эвристика или подтверждённые данные), объём и точность меток по TRON не раскрыты; полей source и confidence нет; RecordedAt — дата записи в таблицу, а не дата
идентификации; метки исправляются/удаляются на месте без истории. Ценовые цифры на одной странице расходятся (карточки $29/$69/$199 — годовая оплата; FAQ $49/$99/$299 — помесячная).
CAPABILITIES: Цепи: ethereum, bsc, polygon, arbitrum, base, avalanche-c, fantom, ethpow, bitcoin, tron, solana. Типы: cex-hot-wallet, cex-cold-wallet, cex-deposit-address, token-contract, token-clone, contract, gambling, issuer-blocked-usdt,
issuer-blocked-usdc. Поля: Address, Chain, Label.Type, Label.Value (slug сущности), RecordedAt. До 100 адресов в одном запросе — весь стандартный кейс (несколько десятков адресов) закрывается одним вызовом.
INFRA: OAuth Bearer token, GraphQL-клиент, батчи по 100 адресов.
PRICING/LIMITS: Pro $69/мес (годовая) или $99/мес: 1M points (~200k вызовов), 90 req/min; add-on Address labels $69/мес (годовая) или $99/мес; Scale $199/$299; Enterprise — labels включены. Trial 7 дней: 1 000 points, без карты. Обязателен фильтр
Address; перечислить все адреса с меткой нельзя.
RISKS: Чёрный ящик по методике депозитных меток — нельзя принимать как единственное основание без проверки на независимом наборе; нет provenance; нет истории версий (нужно сохранять снимок ответа в каждом расследовании).
REPLACEABILITY: Высокая: тот же интерфейс LabelProvider, что у MistTrack/BlockSec.
HOW VERIFIED: docs only (страница документации прочитана curl-ом целиком; pricing через WebFetch). Живых вызовов не делал — нужен аккаунт.
CONFIDENCE: medium
EVIDENCE: https://docs.bitquery.io/docs/labels/address-labels-api/ | https://bitquery.io/pricing

### [ALTERNATIVE] MistTrack OpenAPI (SlowMist)
NEED: Метки (включая deposit/hot/cold) и risk score для TRON, self-serve, оплата за вызов
KIND: commercial SaaS
URL: https://docs.misttrack.io/openapi/overview
LICENSE: Проприетарный; Terms of Service найти не удалось (misttrack.io/terms-of-service.html -> 404)
COMMERCIAL USE: Не подтверждено документально: на pricing-странице политики коммерческого использования нет. Перед цитированием меток в отчётах клиентам — запросить письменное разрешение.
PROJECT STATE: Документация актуальна (llms-full.txt 122 KB, есть v3 risk_score, sandbox, x402). Экосистема: slowmist/MistTrackMCP (pushed 2026-04-28), slowmist/misttrack-skills (MIT, 36 stars, pushed 2026-04-28).
CLAIMED VS ACTUAL: Маркетинг: '400M+ labeled addresses', '19 blockchains' — не проверено. В ответе нет полей source/confidence/даты метки. Маркетинговое 'API from $20/year' = пакет из 100 вызовов ($0.20 за вызов), а не безлимит.
CAPABILITIES: TRON: TRX, USDT-TRC20, USDC-TRC20, USDD-TRC20. v1/address_labels возвращает label_list (имя сущности + тип адреса: deposit / hot / cold + on-chain/off-chain теги) и label_type (exchange, defi, mixer, nft или пусто). v3/risk_score:
score 3-100, risk_level, detail_list, risk_detail с hop-путями, address_label. Sandbox https://sandbox-api.misttrack.io: ETH и TRX, 10 rps, 10 000/сутки (нужен api_key).
INFRA: API key; rate limiter 1-10 rps.
PRICING/LIMITS: Developer plan (pay-per-call, срок 1 год, 10 rps): $20/100 ($0.20), $100/500, $150/1 000 ($0.15), $1 000/10 000 ($0.10), $5 000/100 000 ($0.05), $10 000/250 000 ($0.04), $30 000/1M ($0.03). Standard $689/мес: 1 rps, 10k
вызовов/сутки на ключ. Compliance $2 069/мес: 5 rps, 50k/сутки. Basic $229/мес — без OpenAPI. Trial Standard: $10 за 48 часов. x402 (USDC на Base): address_labels $0.1, address_overview $0.5, risk_score $1.0,
transactions_investigation $1.0. Платежи не возвращаются.
RISKS: При $0.10-0.20 за адрес разметка всех 30-40 адресов расследования стоит $3-8 — превышает лимит $1; годится только как эскалация на 1-3 терминальных адреса или по фиксированной подписке. risk_score по x402 ($1.0) один съедает весь
бюджет. Нет provenance.
REPLACEABILITY: Высокая (адаптер LabelProvider).
HOW VERIFIED: docs only (полный текст docs.misttrack.io/llms-full.txt прочитан; pricing.html через WebFetch). Живых вызовов нет.
CONFIDENCE: high
EVIDENCE: https://docs.misttrack.io/llms-full.txt | https://misttrack.io/pricing.html | https://docs.misttrack.io/openapi/overview

### [REJECTED] slowmist/MistTrackMCP (npm-пакет 'misttrack')
NEED: MCP-доступ агентов к меткам/риску MistTrack
KIND: open-source
URL: https://github.com/slowmist/MistTrackMCP
LICENSE: В репозитории нет файла LICENSE (gh api: license=null); package.json указывает ISC и перечисляет LICENSE в files — несоответствие
COMMERCIAL USE: Формально ISC по package.json, но без текста лицензии в репозитории — юридически неоднозначно. Сам сервер бесполезен без платного плана MistTrack.
PROJECT STATE: 39 stars, создан 2025-05-07, pushed 2026-04-28, v1.1.0, 1 open issue, не archived. Тестов нет (scripts.test = 'no test specified'), CI workflows нет. Node >= 18.
CLAIMED VS ACTUAL: Лицензия заявлена в package.json, файла нет. Рекурсивный анализ ограничен глубиной 3 — не заменяет собственный tracer на 10+ hops.
CAPABILITIES: 12 tools: get_address_labels, get_risk_score (GET /v3/risk_score), check_malicious_funds, get_address_counterparty, analyze_transactions_recursive (max_depth 1-3) и др. Тонкая обёртка над OpenAPI с rate limit 1 rps по умолчанию.
INFRA: Node 18+, npx; ключ MistTrack.
PRICING/LIMITS: Сам MCP бесплатен; каждый вызов тарифицируется как вызов OpenAPI.
RISKS: Ключ передаётся через аргумент --key (попадает в список процессов) — использовать только переменную окружения. Агент может бесконтрольно тратить платные вызовы — нужен бюджетный guard. Нет тестов.
REPLACEABILITY: Высокая: проще и безопаснее собственный типизированный адаптер к 2 эндпоинтам с кэшем, лимитами и журналом.
HOW VERIFIED: code read (README, package.json через raw.githubusercontent.com) + gh api
CONFIDENCE: high
EVIDENCE: https://github.com/slowmist/MistTrackMCP | https://raw.githubusercontent.com/slowmist/MistTrackMCP/main/package.json

### [ALTERNATIVE] BlockSec MetaSleuth Address Label API (v3) и Risk Score API
NEED: Метки с атрибутом DEPOSIT ADDRESS для TRON
KIND: commercial SaaS
URL: https://docs.metasleuth.io/llms-full.txt
LICENSE: Проприетарный
COMMERCIAL USE: Документация позиционирует API для использования 'in your service'; условия перераспространения не найдены. Покупка add-on идёт через 'Contact Us'.
PROJECT STATE: Документация актуальна (v3: https://aml.blocksec.com/address-label/api/v3/labels). Связанный репозиторий blocksecteam/metasleuth_resources заброшен (pushed 2023-06-14, только README).
CLAIMED VS ACTUAL: Маркетинг: 400M+ labels — не проверено; реальное покрытие TRON-депозитов неизвестно. Полей confidence/source/date нет.
CAPABILITIES: 25 цепей, Tron = chain_id -2. Ответ: main_entity (+main_entity_info), comp_entity (дополнительная сущность, напр. клиент биржи), name_tag, attributes с кодами: DEPOSIT ADDRESS 4007, HOT WALLET 4009, ATTACKER 4001 и др. Модель
'главная сущность = биржа, дополнительная = пользователь' хорошо ложится на наш кейс.
INFRA: API key в заголовке API-KEY.
PRICING/LIMITS: Address Label API $599/мес ('10k additional addresses per day'); Risk Score API $499/мес; 5 rps. Бесплатной квоты API на странице планов не указано.
RISKS: Дороже Bitquery в ~4 раза при той же непрозрачности методики; продажа через контакт.
REPLACEABILITY: Высокая.
HOW VERIFIED: docs only (llms-full.txt 270 KB прочитан; metasleuth.io/plans через WebFetch)
CONFIDENCE: medium
EVIDENCE: https://docs.metasleuth.io/llms-full.txt | https://metasleuth.io/plans

### [REJECTED] BlockSec Phalcon Compliance (address/transaction screening + hosted MCP server)
NEED: Risk-screening адреса (sanctioned, scam, blocked by USDT, exposure) для TRON
KIND: commercial SaaS
URL: https://docs.compliance.phalcon.blocksec.com/llms-full.txt
LICENSE: Проприетарный
COMMERCIAL USE: Платные планы предназначены для бизнеса; условия пересказа результатов в отчётах клиентам не найдены.
PROJECT STATE: Документация свежая (changelog, MCP Server, записи с датами 2026-03).
CLAIMED VS ACTUAL: Маркетинг: 'from $0.10 / transaction check'; по документации минимальный пакет Screening Package — от $95 за 50 screenings (= $1.90 за проверку). REST API/webhook есть только в Pro и Enterprise, хотя MCP заявлен для всех планов.
CAPABILITIES: Tron chain_id -2. Результат: riskIndicator, riskLevel, detail (например 'Blocked by USDT', 'Fake_Phishing'), interaction risk c minHop и exposure. Hosted MCP https://mcp.blocksec.com/mcp (OAuth, read-and-screen only, доступен на
всех планах).
INFRA: API-Key либо OAuth для MCP.
PRICING/LIMITS: Free: 3 screenings/мес, только ETH и TRON. Screening Package: 50-2 000 разовых, от $95, срок 12 мес. Standard: 25-500/мес от $39/мес (без API). Pro: 750-5 000/мес от $699/мес (API). Лимиты: 50 вызовов/мин на screen-эндпоинты, 120
screenings/мин.
RISKS: $1.90 за проверку на малых пакетах несовместимо с лимитом $1 на расследование; API только с $699/мес.
REPLACEABILITY: Высокая.
HOW VERIFIED: docs only (llms-full.txt 444 KB прочитан)
CONFIDENCE: high
EVIDENCE: https://docs.compliance.phalcon.blocksec.com/llms-full.txt | https://blocksec.com/phalcon/crypto-aml-compliance

### [NEEDS-TRIAL] Arkham Intelligence API
NEED: Метки сущностей и депозитных адресов, TRON
KIND: commercial SaaS
URL: https://arkm.com/api
LICENSE: Проприетарный; ToS не прочитаны
COMMERCIAL USE: НЕ ПОДТВЕРЖДЕНО — условия перераспространения меток не удалось получить.
PROJECT STATE: Сервис существует, есть LLM-гайды (arkm.com/llms/guides/*.md), но arkm.com и intel.arkm.com из сети аудита недоступны (6 попыток: ECONNRESET / HTTP 000), доступен только codex.arkm.com.
CLAIMED VS ACTUAL: Источники противоречат друг другу: getting-access guide (snippet) — подписки 'start at $100'; APIs.io (транскрипция от 2026-07-18) — 'starting at $900/mo'. x402 '$0.20 per credit' при весах 1-2 credits за строку /transfers
выглядит неправдоподобно дорого — вероятна ошибка транскрипции. Не проверено.
CAPABILITIES: По search snippets: Tron в списке поддерживаемых цепей, заявленное покрытие 57% объёма (хотя бы одна сторона размечена). Intelligence-эндпоинты: теги, сущности, predicted addresses.
INFRA: API key; возможно хостинг в другой юрисдикции.
PRICING/LIMITS: По snippets: trial 1 000 000 credits (individual) / 10 000 000 (organization); лимит label lookups: 10 000 уникальных адресов за период на trial, 1 000 000 на платном individual; повторный lookup того же адреса в периоде считается
один раз; неуспешные запросы не тарифицируются.
RISKS: Недоступность домена из текущей сети (возможна гео/сетевая блокировка) — операционный риск; цены и ToS не подтверждены; доступ через заявку.
REPLACEABILITY: Высокая.
HOW VERIFIED: search snippet only + сторонняя транскрипция (apis.io); прямое чтение документации не удалось
CONFIDENCE: low
EVIDENCE: https://apis.io/plans/arkham/arkham-plans/ | https://arkm.com/llms/guides/credit-pricing.md | https://arkm.com/llms/guides/rate-limits.md | https://codex.arkm.com/arkham-api

### [REJECTED] OKLink address-label API (Explorer API, /api/v5/explorer/address/entity-label)
NEED: Метки сущностей TRON
KIND: public API
URL: https://www.oklink.com/docs/en/
LICENSE: Проприетарный
COMMERCIAL USE: Неактуально — сервис, по всем признакам, закрыт.
PROJECT STATE: Текущая документация oklink.com/docs/en содержит только разделы 'Developer tools / Contract verification / Contract verification plugin' (3 заголовка H1/H2, ни одного упоминания label или TRON). Migration guide Moralis: 'OKLink is
suspending all their Explorer APIs on May 20th, 2025'.
CLAIMED VS ACTUAL: Маркетплейсы и старые страницы всё ещё рекламируют Explorer API с метками; документации на него больше нет. Endpoint отвечает 401 'OK-ACCESS-KEY can not be blank' — шлюз жив, но получить ключ и тариф негде.
CAPABILITIES: Ранее заявлялось 3.4 млрд+ address labels (листинг Huawei Cloud, без даты).
PRICING/LIMITS: Не публикуются.
RISKS: Строить на этом нельзя.
REPLACEABILITY: n/a
HOW VERIFIED: docs read (HTML страницы документации скачан и разобран) + API call (keyless 401) + независимый источник (Moralis guide)
CONFIDENCE: medium
EVIDENCE: https://www.oklink.com/docs/en/ | https://docs.moralis.com/get-started/tutorials/migration-guides/migrating-from-ok-link-to-moralis | https://marketplace.huaweicloud.com/intl/product/OFFI895921530795642880

### [REJECTED] Chainalysis free sanctions screening (on-chain oracle + REST API public.chainalysis.com)
NEED: Бесплатная проверка санкционных адресов
KIND: public API
URL: https://go.chainalysis.com/chainalysis-oracle-docs.html
LICENSE: Проприетарный, бесплатный
COMMERCIAL USE: Oracle был 'available for anyone to use'; для REST API условия не проверены.
PROJECT STATE: Oracle официально DEPRECATED: 'no longer supported or maintained', 'Last oracle update was made on March 18, 2026', 'not recommended for new integrations'. Старая страница free-cryptocurrency-sanctions-screening-tools теперь
описывает платный Address Screening.
CLAIMED VS ACTUAL: Сторонние каталоги и статьи 2022 года до сих пор описывают инструменты как действующие и бесплатные; oracle заморожен с 2026-03-18. Статус REST API не ясен: public.chainalysis.com из сети аудита вернул страницу блокировки
Cloudflare.
CAPABILITIES: Oracle развёрнут только на EVM-сетях (Ethereum, Polygon, BNB, Avalanche, Optimism, Arbitrum, Fantom, Celo, Blast, Base) — TRON нет.
PRICING/LIMITS: Бесплатно (исторически).
RISKS: Заморожен, без TRON, возможна сетевая блокировка.
REPLACEABILITY: n/a — заменяется прямым парсингом OFAC SDN
HOW VERIFIED: docs read (WebFetch страницы oracle, дважды) + API call (keyless GET -> Cloudflare block)
CONFIDENCE: medium
EVIDENCE: https://go.chainalysis.com/chainalysis-oracle-docs.html | https://www.chainalysis.com/free-cryptocurrency-sanctions-screening-tools/

### [ALTERNATIVE] TRM Labs free Sanctions Screening API (POST /public/v1/sanctions/screening)
NEED: Вторичная сверка санкционного статуса
KIND: public API
URL: https://docs.trmlabs.com/api/sanctions/screening/submit-one-or-more-addresses-to-be-screened
LICENSE: Проприетарный, бесплатный
COMMERCIAL USE: Заявлен как бесплатный инструмент для участников рынка; точные условия не прочитаны (docs.trmlabs.com редиректит на login.trmlabs.com).
PROJECT STATE: Запущен 2022-03; документация существует, но сейчас за логином.
CLAIMED VS ACTUAL: Покрытие TRON подтверждается только маркетинговым текстом; каталог API Evangelist пишет про HTTP Basic auth, а OpenAPI-спека — про API key.
CAPABILITIES: Возвращает признак sanctions exposure по адресу; маркетинг: 'TRON, Solana and 23 other blockchains'.
PRICING/LIMITS: Без ключа: 1 req/sec, 100 req/day; с ключом: 1000 req/sec, 100K req/day (search snippet из документации).
RISKS: 100 запросов в сутки без ключа — годится только как выборочная сверка; ничего не даёт сверх собственного разбора OFAC SDN, кроме независимого подтверждения.
REPLACEABILITY: Высокая.
HOW VERIFIED: search snippet only (прямое чтение — редирект на логин); живых вызовов нет (POST не входил в разрешённые keyless GET)
CONFIDENCE: low
EVIDENCE: https://www.trmlabs.com/post/trms-free-sanctions-screening-tool-goes-live | https://docs.trmlabs.com/api/sanctions/screening/submit-one-or-more-addresses-to-be-screened.md

### [REJECTED] Enterprise-аналитика: Chainalysis Address Screening / TRM Labs / Elliptic
NEED: Полная атрибуция и риск-данные TRON (включая депозитные адреса)
KIND: commercial SaaS
URL: https://www.chainalysis.com/
LICENSE: Проприетарные, годовые контракты
COMMERCIAL USE: Только по договору; перераспространение меток в продукте для третьих лиц обычно требует отдельной reseller/OEM-лицензии (не проверено по текстам договоров).
PROJECT STATE: Лидеры рынка, все поддерживают TRON.
CLAIMED VS ACTUAL: Цены не публикуются; агрегаторы расходятся (Chainalysis: CostBench $50-200k/год против медианы Vendr ~$19k/год).
CAPABILITIES: Самое глубокое покрытие, включая депозитные адреса и кластеры.
PRICING/LIMITS: Elliptic на AWS Marketplace: Tier 1 $50 000/год, Tier 2 $100 000/год (12-месячный контракт). TRM: $50K-$500K/год по CostBench, бесплатного плана нет. Chainalysis: годовая подписка + overage за screening.
RISKS: Только через sales, минимальный чек несовместим с MVP и лимитом $1 за расследование.
REPLACEABILITY: n/a
HOW VERIFIED: search snippet only (агрегаторы цен, AWS Marketplace)
CONFIDENCE: low
EVIDENCE: https://aws.amazon.com/marketplace/pp/prodview-6odrg7umycz5u | https://costbench.com/software/crypto-compliance/trm-labs | https://costbench.com/software/crypto-compliance/chainalysis

### [REJECTED] Enterprise-аналитика второго эшелона: Crystal Intelligence / Scorechain / Merkle Science
NEED: Атрибуция и риск TRON
KIND: commercial SaaS
URL: https://www.scorechain.com/resources/crypto-glossary/scorechain-pricing
LICENSE: Проприетарные
COMMERCIAL USE: Только по договору.
PROJECT STATE: Действующие продукты; TRON поддерживается (Crystal — с 2022-12, TRX + 45 TRC20; Scorechain и Merkle Science — отдельные анонсы).
CLAIMED VS ACTUAL: Продукта 'Crystal Lite' с публичной ценой не найдено. Scorechain прямо пишет, что прайс-листа нет.
PRICING/LIMITS: Не публикуются, 'contact sales'.
RISKS: Нет self-serve, нет цен, длинный цикл закупки.
REPLACEABILITY: n/a
HOW VERIFIED: search snippet only
CONFIDENCE: low
EVIDENCE: https://www.scorechain.com/resources/crypto-glossary/scorechain-pricing | https://crystalintelligence.com/product-updates/product-update-crystal-adds-tron-support-in-the-latest-product-update | https://www.merklescience.com/blog/transforming-blockchain-security-introducing-our-advanced-clustering-algorithms-and-heuristics-for-bitcoin-and-smart-contract-chains-such-as-ethereum-and-tron

### [REJECTED] AMLBot
NEED: AML-проверка адреса TRON с именами сущностей
KIND: commercial SaaS
URL: https://amlbot.com/api-integration
LICENSE: Проприетарный (User Agreement в PDF не читался)
COMMERCIAL USE: Не подтверждено.
PROJECT STATE: Действующий сервис; планы Lite / Pro / Pro+.
CLAIMED VS ACTUAL: Search snippet приписывает странице api-integration тарифы Growth $1 500/5 000 проверок ($0.30), Business $3 750/15 000 ($0.25), Premium $10 000/50 000 ($0.20); при прямой загрузке страницы цен нет, только 'Book a Demo'. Блог: API
('KYT & KYC API Access') только в Pro+, цены Pro/Pro+ 'available on request'.
CAPABILITIES: Отчёт с risk score и источниками риска; '99.5% data accuracy from 3 reliable sources' (заявление вендора, провайдеры не названы).
PRICING/LIMITS: Не подтверждены; ориентир $0.20-0.45 за проверку.
RISKS: API только в старшем плане через sales; даже $0.20 за проверку не укладывается в бюджет при проверке всех адресов; источник данных непрозрачен.
REPLACEABILITY: Высокая.
HOW VERIFIED: docs only (две страницы через WebFetch) + search snippet (цены, противоречие)
CONFIDENCE: low
EVIDENCE: https://amlbot.com/api-integration | https://blog.amlbot.com/amlbot-plans-explained/

### [REJECTED] GoPlus Security — Malicious Address API (address_security)
NEED: Бесплатные risk-флаги адреса (sanctioned, phishing, blacklist) для TRON
KIND: public API
URL: https://api.gopluslabs.io/api/v1/address_security/{address}?chain_id=tron
LICENSE: Проприетарный, бесплатный tier; сайт называет сервис 'open, license-free'
COMMERCIAL USE: Условия коммерческого использования не найдены.
PROJECT STATE: Сервис жив, отвечает без ключа.
CLAIMED VS ACTUAL: TRON заявлен как поддерживаемый, но в живой проверке API вернул все нули для: адреса из OFAC SDN (TA3rH2A7..., sanctioned=0), адреса, замороженного Tether (TZACYaKB..., blacklist_doubt=0), и hot wallet Binance; data_source пустой.
Выборка 3 адреса, но оба заведомо 'плохих' адреса пропущены.
CAPABILITIES: /api/v1/supported_chains?name=address_security включает Tron (id 'tron'). 19 флагов: sanctioned, blacklist_doubt, phishing_activities, money_laundering, mixer и др., поле data_source.
PRICING/LIMITS: Free: по одним данным 100 call credits/min, по другим 150K CU/мес, 30k CU/сутки, 150 CU/мин (страницы GoPlus расходятся).
RISKS: Ложное чувство безопасности: 'все флаги 0' нельзя трактовать как 'чисто'. Для TRON практически бесполезен.
REPLACEABILITY: n/a
HOW VERIFIED: API call made (4 keyless GET)
CONFIDENCE: medium
EVIDENCE: https://api.gopluslabs.io/api/v1/supported_chains?name=address_security | https://gopluslabs.io/security-api

### [ALTERNATIVE] Chainabuse API (TRM Labs)
NEED: Пользовательские scam-репорты по адресу (OSINT-сигнал)
KIND: public API
URL: https://docs.trmlabs.com/guides/chainabuse/getting-started
LICENSE: Проприетарный
COMMERCIAL USE: Бесплатный ключ предназначен для проверки адресов перед транзакцией; для продуктов — partner access через hello@chainabuse.com. Коммерческие условия не опубликованы.
PROJECT STATE: Действует; документация перенесена на docs.trmlabs.com (сейчас за логином).
CLAIMED VS ACTUAL: Позиционируется как открытая платформа, но стандартный ключ — 10 вызовов в месяц (1 вызов = до 50 репортов).
CAPABILITIES: Отчёты пострадавших по адресам и доменам, категории мошенничества. Покрытие TRON отдельно не документировано.
PRICING/LIMITS: Standard key: 10 calls/month; общий предел 5 000 calls/hour; premium — только партнёрам.
RISKS: 10 вызовов в месяц непригодны для автоматического пайплайна; репорты не верифицированы (confidence низкий); нужен партнёрский доступ.
REPLACEABILITY: Средняя.
HOW VERIFIED: search snippet only (документация за логином)
CONFIDENCE: low
EVIDENCE: https://docs.trmlabs.com/guides/chainabuse/getting-started-2-1.md | https://docs.trmlabs.com/guides/chainabuse/getting-started.md

### [REJECTED] Nansen API (profiler/address/labels)
NEED: Метки адресов, TRON
KIND: commercial SaaS
URL: https://docs.nansen.ai/getting-started/credits
LICENSE: Проприетарный
COMMERCIAL USE: Не проверено.
PROJECT STATE: API активно развивается (changelog 2026-03-31 'Premium Labels Flag'); TRON добавлен в Nansen 2024-11-19.
CLAIMED VS ACTUAL: Поддержка TRON именно в labels-эндпоинте не подтверждена. Две версии документации о кредитах противоречат друг другу (1 000 против 2 000 стартовых кредитов).
PRICING/LIMITS: Pro $49/мес (годовая) или $69/мес, 2 000 credits; profiler/address/labels = 100 credits за вызов, premium-labels = 500 credits. То есть в подписку входит ~20 lookups в месяц.
RISKS: Стоимость одного lookup ~$2.5-3.5 в пересчёте на включённые кредиты — несовместимо с бюджетом.
REPLACEABILITY: n/a
HOW VERIFIED: docs only (WebFetch docs.nansen.ai)
CONFIDENCE: medium
EVIDENCE: https://docs.nansen.ai/getting-started/credits.md | https://release.nansen.ai/changelog/tron-now-available-on-nansen-rocket

### [REJECTED] Dune Spellbook — cex_tron.addresses (labels для TRON)
NEED: Открытый список кошельков бирж на TRON
KIND: dataset
URL: https://github.com/duneanalytics/spellbook/blob/main/dbt_subprojects/hourly_spellbook/models/_sector/cex/addresses/chains/tron/cex_tron_addresses.sql
LICENSE: Business Source License 1.1 (Licensor Dune Analytics AS); Additional Use Grant запрещает использование для 'Data or Analytics Platform'; Change Date 2027-03-03 -> GPL-3.0-or-later
COMMERCIAL USE: НЕТ для нашего случая: LEDGERHUNT даёт третьим лицам доступ к результатам на основе данных — прямо подпадает под запрет. После 2027-03-03 — GPLv3 (copyleft).
PROJECT STATE: 1519 stars, pushed 2026-10-12. Файл TRON: 151 адрес, 30 бирж (MaskEX 19, HTX 18, Binance 16, OKX 15, CoinDCX 13, Bitget 11, Bybit 8...), последние добавления 2025-08-19, последний коммит файла 2026-01-28 ('bulk hide curated
datasets' — добавлен post_hook hide_spells).
CLAIMED VS ACTUAL: Воспринимается как 'open labels', но лицензия BSL исключает коммерческое SaaS-использование; таблица помечена к скрытию.
CAPABILITIES: Только hot/cold; депозитных адресов нет; колонки: address, cex_name, distinct_name, added_by, added_date.
PRICING/LIMITS: Бесплатно для чтения.
RISKS: Лицензионный блокер; малое покрытие; отсутствие обновлений год.
REPLACEABILITY: n/a
HOW VERIFIED: code read (LICENSE и SQL-файл через raw.githubusercontent.com, подсчёт адресов) + gh api
CONFIDENCE: high
EVIDENCE: https://raw.githubusercontent.com/duneanalytics/spellbook/main/LICENSE | https://raw.githubusercontent.com/duneanalytics/spellbook/main/dbt_subprojects/hourly_spellbook/models/_sector/cex/addresses/chains/tron/cex_tron_addresses.sql

### [ALTERNATIVE] GraphSense public TagPacks + TagPack confidence taxonomy
NEED: Открытый стандарт формата меток и шкалы достоверности; открытые метки
KIND: standard
URL: https://github.com/graphsense/graphsense-tagpacks
LICENSE: MIT (и tagpacks, и graphsense-tagpack-tool)
COMMERCIAL USE: Разрешено (MIT).
PROJECT STATE: graphsense-tagpacks: 39 stars, pushed 2026-10-13, активные PR. graphsense-tagpack-tool: 10 stars, archived=true, pushed 2025-09-04 (инструмент заархивирован).
CLAIMED VS ACTUAL: Покрытие TRON в публичных паках крошечное: Binance 8 адресов, Huobi 13, KuCoin 4, ofac.yaml 7 (lastmod 2022-11 и 2024-02); usdt_blacklist.yaml — только ETH (lastmod 2023-02-22).
CAPABILITIES: Таксономия confidence (confidence.csv): ownership 100, ledger_immanent 100, manual_transaction 90, service_api 70, forensic_investigation 70, authority_data 60, trusted_provider 50, service_data 50, forensic 50,
untrusted_transaction 40, web_crawl 20, heuristic 10, unknown 5. Формат YAML с полями source, lastmod, confidence, category, is_cluster_definer, actor.
PRICING/LIMITS: Бесплатно.
RISKS: Как источник данных по TRON почти бесполезен; ценность — в схеме и шкале достоверности. Инструмент валидации заархивирован.
REPLACEABILITY: Высокая: схема простая, переносится в собственную модель.
HOW VERIFIED: code read (raw YAML/CSV, подсчёт адресов) + gh api
CONFIDENCE: high
EVIDENCE: https://github.com/graphsense/graphsense-tagpacks/tree/master/packs | https://raw.githubusercontent.com/graphsense/graphsense-tagpack-tool/master/src/tagpack/db/confidence.csv

### [REJECTED] Webacy / HAPI / Breadcrumbs / Range (risk APIs)
NEED: Risk score адреса TRON
KIND: commercial SaaS
URL: https://docs.range.org/risk-api/product-info/supported-chains
LICENSE: Проприетарные
COMMERCIAL USE: Не проверялось — отсеяны по покрытию.
PROJECT STATE: Действующие сервисы.
CLAIMED VS ACTUAL: Webacy: в списке цепей Ethereum, Polygon, Optimism, Arbitrum, Base, BSC, Solana, TON, Sei, Sui, Stellar, Hedera, Bitcoin — TRON нет. Range: TRON только в мониторинге token blacklist (Tether/Circle), в таблице address risk его нет.
HAPI: упоминается лишь партнёрство с TRON, поддержка в API не подтверждена. Breadcrumbs: список цепей не опубликован, примеры про Bitcoin.
PRICING/LIMITS: Цены не опубликованы.
RISKS: Нет подтверждённого покрытия TRON.
REPLACEABILITY: n/a
HOW VERIFIED: search snippet only (прямые URL документации дали 404)
CONFIDENCE: low
EVIDENCE: https://docs.webacy.com/essentials/supported-blockchains | https://docs.range.org/risk-api/product-info/supported-chains | https://jentic.com/apis/breadcrumbs

### [REJECTED] OpenSanctions (crypto addresses в сводном датасете)
NEED: Агрегированные санкционные адреса из многих юрисдикций
KIND: dataset
URL: https://www.opensanctions.org/licensing/
LICENSE: CC BY-NC 4.0; коммерческое использование — только по платной лицензии
COMMERCIAL USE: Нет без лицензии ('any business purposes requires a licensing agreement'); для встраивания в продукт нужен reseller/wholesale-тип лицензии. Цены не опубликованы, есть скидки стартапам.
PROJECT STATE: Активный проект; 13 925 crypto addresses в датасете (по странице licensing).
CLAIMED VS ACTUAL: 'Open' в названии не означает свободного коммерческого использования. Доля TRON-адресов не выяснена.
PRICING/LIMITS: По запросу.
RISKS: Лицензионный блокер для MVP; основная ценность (OFAC) получается напрямую бесплатно.
REPLACEABILITY: Высокая.
HOW VERIFIED: search snippet only (официальные страницы opensanctions.org)
CONFIDENCE: medium
EVIDENCE: https://www.opensanctions.org/licensing/ | https://www.opensanctions.org/faq/commercial/paying-for-use/

### [NEEDS-TRIAL] Mendeley Data: Judicially Grounded Virtual Asset Address Labels and TRON TRC20-USDT Behavioral Analysis Dataset (DOI 10.17632/62dmsngtfb.3)
NEED: Независимые размеченные адреса TRON для тестового набора
KIND: dataset
URL: https://data.mendeley.com/datasets/62dmsngtfb
LICENSE: CC BY 4.0 (на странице также стоит общая оговорка платформы 'All rights are reserved, including those for text and data mining, AI training')
COMMERCIAL USE: CC BY 4.0 разрешает коммерческое использование с атрибуцией; противоречащую оговорку платформы нужно зафиксировать и при сомнении уточнить у автора.
PROJECT STATE: Версия 3 опубликована 2026-08-03; автор Meng Ling Tsai, Central Police University (Тайвань).
CLAIMED VS ACTUAL: Список классов/ролей и их количества на странице не указаны; файловый список на странице пуст — содержимое не инспектировалось. Неизвестно, есть ли класс 'exchange deposit'.
CAPABILITIES: 1 150 меток адресов с единственной ролью, основанных на судебных решениях по делам о мошенничестве и отмывании; поднабор из 1 024 адресов TRON TRC20-USDT; словари данных и скрипты анализа. Деидентифицирован (без номеров дел и URL
источников).
PRICING/LIMITS: Бесплатно.
RISKS: Происхождение меток нельзя перепроверить по первичным документам (ссылки удалены); региональный перекос (Тайвань); роли могут не совпадать с нашей таксономией.
REPLACEABILITY: Средняя.
HOW VERIFIED: docs only (страница датасета через WebFetch); файлы не скачивались
CONFIDENCE: medium
EVIDENCE: https://data.mendeley.com/datasets/62dmsngtfb

### [REJECTED] Открытые датасеты меток TRON на HuggingFace / Kaggle / GitHub
NEED: Готовые открытые списки меток TRON
KIND: dataset
URL: https://huggingface.co/api/datasets?search=tron
LICENSE: n/a
COMMERCIAL USE: n/a
PROJECT STATE: Не найдено пригодных. HuggingFace API (запросы: tron, trc20, usdt, address label, wallet labels, crypto labels, exchange addresses, blockchain labels): единственный релевантный — carrierone/verilex-address-labels (MIT, 11
загрузок, только README, '211+ labeled Ethereum addresses', реклама платного API). GitHub search (10 запросов): специализированных репозиториев меток TRON нет. Kaggle — веб-поиск ничего не дал.
CLAIMED VS ACTUAL: Ожидание 'есть открытые label-репозитории, реально покрывающие TRON' не подтвердилось: EVM-репозитории (etherscan-labels и т.п.) TRON не покрывают, а TRON-специфичных нет.
CAPABILITIES: Найдены смежные: ai-decisions/openlabels (Apache-2.0, создан 2026-08-26, 1 star, 10 коммитов, 15 тестовых файлов, CI) — инструментарий (схема меток, парсер OFAC, конвертер адресов TRON, генератор TagPack) без самих данных; его
README прямо предупреждает, что производные от OpenSanctions (CC-BY-NC) и Dune Spellbook (BSL) включать нельзя — независимое подтверждение лицензионных выводов.
PRICING/LIMITS: n/a
RISKS: Собственный реестр придётся курировать самим.
REPLACEABILITY: n/a
HOW VERIFIED: API call made (HuggingFace datasets API, GitHub search API через gh) + web search для Kaggle
CONFIDENCE: medium
EVIDENCE: https://huggingface.co/datasets/carrierone/verilex-address-labels | https://github.com/ai-decisions/openlabels

### [ALTERNATIVE] Israel NBCTF administrative seizure orders (списки кошельков)
NEED: Authority-метки terror-financing для TRON
KIND: dataset
URL: https://www.elliptic.co/blog/israeli-authorities-link-42-crypto-addresses-to-terrorism
LICENSE: Публичные государственные документы; пересказы Elliptic — их авторское содержание
COMMERCIAL USE: Факты из официальных приказов использовать можно; место официальной публикации PDF не подтверждено.
PROJECT STATE: Приказы выходят нерегулярно (2021-2025); за 2026 год свежих не нашёл.
CLAIMED VS ACTUAL: По приказу на 137 кошельков источники расходятся в формате адресов (Ethereum или TRON).
CAPABILITIES: ASO 5/24: 42 адреса, все на TRON (13 из них ранее заморожены Tether); приказ по PIJ: 26 TRON-кошельков; Reuters: 143 TRON-кошелька заморожено с 07.2021 по 10.2023.
PRICING/LIMITS: Бесплатно; ручной ввод.
RISKS: Нет машинно-читаемого фида; ручная курация; политически чувствительные метки — в отчёте формулировать строго как 'указан в приказе NBCTF № ...'.
REPLACEABILITY: Средняя.
HOW VERIFIED: search snippet only
CONFIDENCE: low
EVIDENCE: https://www.elliptic.co/blog/israeli-authorities-link-42-crypto-addresses-to-terrorism | https://www.elliptic.co/blog/analysis/israel-orders-seizure-of-crypto-wallets-worth-94-million-linked-to-palestinian-islamic-jihad

### [NEEDS-TRIAL] Эвристика 'deposit -> hot-wallet sweep' (deposit address reuse / fund gathering) для вывода депозитных адресов бирж на TRON
NEED: Вывод депозитных адресов, когда провайдер метки не дал
KIND: standard
URL: https://arxiv.org/pdf/2003.13399
LICENSE: Метод из открытых публикаций; реализация собственная
COMMERCIAL USE: Без ограничений.
PROJECT STATE: Метод описан для Ethereum (Victor, FC 2020 — deposit address reuse; arXiv 2003.13399 — fund gathering; Tutela arXiv 2201.06811 — пороги по сумме и времени между получением и пересылкой, исключение известных сущностей). TRON-
специфичной рецензируемой работы с измеренной ошибкой не найдено; работа 2025 года отмечает, что у эвристик кластеризации нет известной частоты ошибок из-за отсутствия ground truth.
CLAIMED VS ACTUAL: Живая проверка: среди 27 входящих USDT-переводов в 'Binance-Hot 2' (TV6MuMXf...) были суммы 0.0001, 1, 2, 4, 5, 12 USDT и один отправитель с тегом 'Bybit' — то есть 'отправил на hot wallet' само по себе не означает 'депозитный
адрес' (dust/address poisoning, прямые переводы, чужие сервисы).
CAPABILITIES: Признаки кандидата: EOA; 100% исходящих USDT уходит на 1-2 адреса, размеченных как кошельки одной биржи; пересылка быстро и почти на всю сумму; TRX/energy для sweep поступает от адреса того же кластера; много таких адресов с
одинаковым поведением вокруг одного hot wallet.
PRICING/LIMITS: Бесплатно, но требует истории исходящих переводов кандидата (1-2 запроса на адрес).
RISKS: Ложные срабатывания: платёжные шлюзы и процессинги с per-invoice адресами; OTC-деск или P2P-мерчант, пересылающий на свой депозит; казино и кастодиальные кошельки с per-user адресами; instant-swap сервисы (депозит принадлежит
аккаунту сервиса, а не вора); omnibus-кастоди (Ceffu, Cobo, Fireblocks) и white-label/broker-программы, делящие инфраструктуру с биржей; сервисы аренды energy и gas-sponsor адреса, создающие ложные связи; ошибочная исходная метка
hot wallet; ротация кошельков. Даже верный вывод называет биржу, но не владельца аккаунта.
REPLACEABILITY: n/a (собственный код)
HOW VERIFIED: search snippet only по литературе + API call (выборка переводов TronScan)
CONFIDENCE: medium
EVIDENCE: https://arxiv.org/pdf/2003.13399 | https://arxiv.org/pdf/2201.06811 | https://www.merklescience.com/blog/transforming-blockchain-security-introducing-our-advanced-clustering-algorithms-and-heuristics-for-bitcoin-and-smart-contract-chains-such-as-ethereum-and-tron

## OPEN QUESTIONS FOR OWNER (researcher)
- Что именно означает цель '>= 95% точности меток': precision положительных меток биржа/сервис (предлагаю так, с обязательным отчётом о coverage) или общая accuracy по всем адресам, включая unknown? От этого зависит размер и состав
тестового набора.
- Готова ли команда открыть (с KYC) аккаунты на 8-10 биржах, чтобы получить собственные депозитные адреса TRC20 как бесспорный ground truth? На каких биржах это возможно юридически и практически?
- Допустим ли на этапе MVP фиксированный месячный расход на метки: Bitquery ~$138-198/мес? До ~200 расследований в месяц он формально не укладывается в $1 за расследование, если относить его к переменным затратам.
- Как показывать в отчёте эвристических 'кандидатов в депозитные адреса' (L5): отдельным блоком 'не подтверждено' или не показывать вовсе? И можно ли на их основании формировать черновик запроса в биржу?
- Кто ведёт переписку с TronScan, Bitquery и MistTrack о письменном разрешении цитировать их метки в отчётах, передаваемых третьим лицам (биржам, полиции)? Без этого метки вендоров в PDF — юридический риск.
- Где будет размещён production-сервер? Из текущей сети недоступны arkm.com и public.chainalysis.com (сброс соединения / блок Cloudflare) — это влияет на выбор провайдеров и хостинга.
- Нужны ли в MVP метки OTC-десков, P2P-мерчантов и обменников СНГ? Ни один открытый источник их не даёт; потребуется ручная курация реестра с собственными правилами доказательности.
- Подтверждаете ли, что enterprise-вендоры (Chainalysis, TRM, Elliptic, Crystal, от ~$50 000 в год) вне рамок до появления платных тарифов? Если нет — с кем из них начинать переговоры о стартап-программе?
- Допустимо ли в отчётах использовать политически чувствительные authority-метки (приказы NBCTF) и в какой формулировке?
- Нужно ли хранить сырые ответы провайдеров меток в составе evidence-пакета каждого расследования (рекомендую да, так как Bitquery и TronScan меняют метки без истории) — и на какой срок?

## NOT VERIFIED (researcher)
- Условия использования TronScan API (коммерческое использование, кэширование, цитирование тегов в отчётах третьим лицам), квоты и цены API key: docs.tronscan.org и support.tronscan.org отдают Cloudflare 403; сведения об
обязательности ключа — только из search snippets.
- Arkham Intel API: все факты (trial 1M credits, лимит 10 000 label lookups, цены $100 или $900/мес, x402 $0.20 за credit, покрытие Tron 57%) — из search snippets и сторонней транскрипции apis.io; ToS и наличие меток депозитных
адресов TRON не проверены.
- Текущий статус бесплатного REST Sanctions API Chainalysis и его поддержка TRON (ответ заблокирован Cloudflare).
- TRM free Sanctions API: лимиты (1 req/s и 100 req/day без ключа) и покрытие TRON — из search snippet и маркетинга; документация за логином; живой вызов не делался (POST).
- Bitquery Address Labels: объём, методика и точность меток cex-deposit-address по TRON; расход points на запрос Metadata.Labels; условия перераспространения (bitquery.io/terms -> 404). Живых вызовов не было.
- MistTrack: Terms of Service не найдены; реальная точность и покрытие меток по TRON; заявление о 400M+ меток.
- BlockSec MetaSleuth Address Label API: фактическое покрытие TRON-депозитов; условия перераспространения; есть ли бесплатная квота API.
- OKLink: официального объявления о закрытии Explorer API не найдено — вывод основан на текущем содержимом документации и гайде Moralis (заинтересованная сторона).
- Binance PoR endpoint (пустой ответ из сети аудита) и соответствие адресов в DefiLlama-Adapters официальным PoR-страницам каждой биржи по отдельности не сверялись.
- AMLBot: тарифы Growth/Business/Premium из search snippet не подтвердились при прямой загрузке страницы; покрытие TRON и поставщики данных не названы.
- Chainabuse: лимит 10 вызовов в месяц — только search snippet; покрытие TRON и условия партнёрского доступа неизвестны.
- Mendeley dataset 10.17632/62dmsngtfb.3: классы меток, их количество и файлы не инспектировались (файлы не скачивались); совместимость оговорки платформы 'All rights are reserved...' с CC BY 4.0.
- GoPlus: проверено только 3 адреса; возможно, отдельные категории (phishing) по TRON заполнены.
- Kaggle: поиск только через веб-поиск, без прямого API; отсутствие датасетов меток TRON там не доказано.
- NBCTF: место официальной публикации приказов и машинно-читаемый формат не подтверждены; количества адресов — из пересказов Elliptic и СМИ.
- Метод isBlackListed(address) контракта USDT не вызывался (требует POST triggerconstantcontract); полный подсчёт событий AddedBlackList на TronGrid не выполнялся — использовано total=7838 от TronScan.
- Вывод 'TronScan не размечает депозитные адреса' основан на выборке 27 отправителей в один кошелёк Binance и 50 получателей от другого.
- Цены Elliptic / TRM / Chainalysis / Crystal / Scorechain / Merkle Science — из агрегаторов и AWS Marketplace, без подтверждения от вендоров.
- Nansen: поддержка TRON именно в эндпоинте profiler/address/labels; цена докупаемых credits.
- Литература по эвристике депозитных адресов: статьи Victor (FC 2020), arXiv 2003.13399 и 2201.06811 известны по аннотациям и пересказам в поиске, полные тексты не читались; TRON-специфичной оценки частоты ошибок не найдено.
- Плакат FIT VUT 2025 об открытой TRON-forensics платформе с '51M address attributions' из веб-скрейпинга — не изучался (источник и законность скрейпинга неизвестны).
- Официальный TronScan MCP Server (анонс 2026-03-09) — только заголовок из поиска, возможности и лицензия не проверены.