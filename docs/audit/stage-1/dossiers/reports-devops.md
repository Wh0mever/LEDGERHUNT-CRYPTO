# AREA reports-devops: Report generation (JSON, PDF) and deployment, monitoring, logs, backups, secrets

============================================================
PART 1 - VERIFIER REPORT (takes precedence over the researcher wherever they disagree)
============================================================

## VERIFIER SUMMARY
Проверено самостоятельно по первичным источникам более 25 утверждений (gh api, чтение LICENSE и исходников, официальные страницы цен и документации, публичный каталог OVH API, GitLab/PyPI/Docker Hub API, по одному GET к календарю
OpenTimestamps и Sigstore TSA). Сторонний код не запускался, POST-запросы не отправлялись. Общий вывод: фактическая часть аудита добротная — версии, даты, лицензии и цены почти везде совпали с первоисточниками (WeasyPrint,
Gotenberg, Typst, pgBackRest, restic, SOPS/age, VictoriaMetrics/VictoriaLogs/Alloy/Grafana, GlitchTip, Compose/Caddy, Backblaze B2, Hetzner, netcup, GitHub Actions, Coolify/Dokploy/Kamal). Восемь из девяти рекомендаций устояли. Не
устояла в описанном виде одна — схема integrity seal: в ней цикл хешей (manifest содержит хеш PDF, а PDF печатает и вкладывает хеш manifest). Набор инструментов при этом верный, нужна двухуровневая схема manifest. Найденные ошибки
и неточности: - PR #2808 WeasyPrint не слит; цифра 0.94 с — с форка автора, замеров на 70.0 нет. Оптимизация вошла через PR #2813. - PDF/A в WeasyPrint поддерживается с 56.0, а не с 67.0. - Тезис «опубликованного крипто-расширения
STIX нет» опровергнут: есть muchdogesec/stix2extensions. - OVH VPS-2: €7.21 — только при оплате за 12 месяцев вперёд, без обязательств €8.49. - rfc3161-client имеет Windows-wheel; playwright-python уже v1.64.0; у pgBackRest 9
спонсоров, и апгрейд не чинит уже созданные слабые subkeys. - Критерий «много security advisories» применён к Coolify/Dokploy, но не к запасному Gotenberg (20 advisories за 2026, включая critical RCE) и к рекомендованному Uptime
Kuma (19). - Не замечено ограничение rfc8785.py на целые больше 2^53 — суммы TRC20 должны быть строками. Что стоит добавить в рассмотрение: PlutoPrint (быстрый движок PDF с Windows-wheels), Databasus (PITR + проверка
восстановлением), netcup RS 1000 G12.5 (выделенные ядра для эталонных замеров), docker-rollout, Gatus, Beszel, Sigstore TSA, TRM Beacon Network, veraPDF. Не удалось подтвердить: требования Binance/OKX/Tether к запросам (страницы
недоступны), апрельское повышение цен Hetzner, цены Hetzner Object Storage и IPv4, ToS бесплатных тиров, совместимость pgBackRest с B2. Лимит WebSearch исчерпан после двух запросов, поэтому поиск новых кандидатов 2025-2026
неполон. Рабочие файлы проверки (сырые данные, не отчёты): C:\Users\Asus\AppData\Local\Temp\claude\C--LEDGERHUNT-CRYPTO\912b2cf7-a304-454a-a85d-20eefb54cc33\scratchpad\ovh_vps.json, wp_changelog.rst, vl_readme.md, vlagent.md,
databasus.md, restic030.rst.

## BLOCKING RISKS
- Схема integrity seal в описанном виде содержит цикл хешей: manifest включает sha256(report.pdf), а хеш manifest печатается в колонтитуле того же PDF и manifest вкладывается в PDF/A-3. Без разделения на content-manifest (внутри
PDF) и package-manifest (снаружи) реализовать нельзя.
- RFC 8785 (rfc8785.py) отказывает на целых вне +-(2^53-1): если суммы TRC20 или другие uint256 попадут в report.json числами, каноникализация и подпись упадут или потеряют точность. Суммы обязаны быть строками — это надо
зафиксировать в схеме до написания кода.
- Производительность WeasyPrint на многостраничных таблицах не измерена никем: единственная цифра взята из неслитого PR #2808 с форка автора. Мейнтейнер заявляет, что скорость не приоритет. Для графа на 1 000 адресов рендер PDF
может не уложиться в отведённое время и память на 8-ГБ сервере — нужен бенчмарк-гейт до фиксации выбора и запасной движок.
- В HTML отчёта попадают строки, контролируемые злоумышленником (имена токенов, memo, внешние метки), а оба PDF-движка имеют свежие серьёзные уязвимости: WeasyPrint — RCE через EPS/Ghostscript и SSRF (2026), Gotenberg — 20
advisories за 2026, включая critical unauthenticated RCE. Рендер без сетевой изоляции и autoescape недопустим; Gotenberg нельзя выставлять за пределы внутренней сети.
- pgBackRest: проект в апреле 2026 был объявлен неподдерживаемым (bus-factor остаётся); версии до 2.59.3 создают слабые ключи шифрования, и апгрейд их не заменяет; официального Docker-образа нет; работа с Backblaze B2 и Object Lock
в этой сессии первичным источником не подтверждена. До продакшена обязателен тестовый restore на B2.
- Требования бирж, Tether и LE-порталов к содержанию запросов не подтверждены ни одним первичным источником (страницы Binance и OKX дают ECONNRESET и у исследователя, и у меня; у Tether — 404). Шаблоны писем нельзя выпускать как
'соответствующие требованиям получателя' без ручной сверки — иначе нарушается принцип 'ничего не выдумывать'.
- Эталон REF-1 на shared vCPU OVH с нераскрытой моделью CPU не обеспечивает воспроизводимость замеров; цена €7.21 требует оплаты за 12 месяцев вперёд (без обязательств €8.49). Оценка ~6 ГБ RAM для 13 контейнеров не измерена; с
графовой БД и пиками рендера 8 ГБ может не хватить.
- Инструменты наблюдаемости сами расширяют поверхность атаки: Uptime Kuma — 19 advisories (high unauthenticated DoS от 2026-10-09). Все панели (Grafana, GlitchTip, Kuma, возможный Databasus) должны быть доступны только через VPN;
age-ключ и ключ подписи отчётов на том же хосте означают, что компрометация сервера обесценивает и секреты, и подпись.
- Условия коммерческого использования бесплатных сервисов, на которые опирается нулевая смета (healthchecks.io Hobbyist, Grafana Cloud Free, FreeTSA, публичные календари OpenTimestamps, публичный Sigstore TSA), по ToS не проверены
ни исследователем, ни мной — только страницы цен. Для платного продукта заложить платные тарифы (healthchecks.io Business $20/мес, коммерческий TSA).
- Ограничение самой проверки: общий лимит WebSearch исчерпан после двух запросов, поэтому поиск пропущенных кандидатов 2025-2026 выполнен через gh api и прямое чтение официальных страниц и неполон (не проверены, в частности,
коммерческие TSA, квалифицированные eIDAS-провайдеры, актуальные LE-регламенты бирж и альтернативные VPS-провайдеры). При необходимости поиск можно продолжить отдельным запуском.

## VERIFIER VERDICTS ON RECOMMENDATIONS

### NEED: PDF-рендеринг evidence-отчёта и писем
PRIMARY: WeasyPrint 70.0 + Jinja2 HTML/CSS в Linux-контейнере (PDF/A-3 с вложенными report.json и manifest.json)
STANDS: True
ISSUE: Лицензия, статус и функции подтверждены, но обоснование по производительности опирается на некорректно процитированный источник: PR #2808 не слит, цифра 0.94 с — с форка автора, на релизе 70.0 замеров нет; мейнтейнер прямо
говорит, что скорость не приоритет, а docs — что многостраничные таблицы медленные. Для графа на 1 000 адресов (тысячи-десятки тысяч строк TXID) время и память рендера неизвестны. Вторая проблема — безопасность: в отчёт попадают
строки, контролируемые атакующим (имена токенов, memo, внешние метки), а у WeasyPrint 4 advisories за 2026 (включая RCE через EPS -> Ghostscript и два SSRF), у запасного Gotenberg — 20 advisories за 2026, включая critical
unauthenticated RCE. На Windows-деве библиотека требует MSYS2 + Pango, а готовый exe, по docs, регулярно помечается антивирусами как malware.
SUGGESTED CHANGE: Оставить WeasyPrint >= 70.0, но: (1) до фиксации выбора прогнать бенчмарк 1k/5k/10k/50k строк на эталонном сервере с порогами времени и RSS; (2) вынести рендер PDF из SLA '30 с / 2 мин' в асинхронную задачу; (3) длинные таблицы
верстать с table-layout: fixed или блоками, а полный список TXID при превышении порога отдавать вложением CSV/JSON в PDF/A-3, оставляя в теле отчёта агрегаты; (4) контейнер рендера без исходящей сети, без Ghostscript в образе,
свой URLFetcher deny-all, autoescape, закреплённая версия; (5) Gotenberg, если понадобится, — только во внутренней сети, с отключёнными webhook/downloadFrom, никогда не публиковать порт; (6) добавить в trial PlutoPrint 0.22.0
(MIT, нативный C++-движок, готовые wheels для Windows/Python 3.13) как кандидата на быстрый движок за тем же интерфейсом render(html) -> pdf.

### NEED: JSON-отчёт: схема и версионирование
PRIMARY: Pydantic 2.14 -> публикуемый JSON Schema 2020-12 с schema_version (SemVer) + python-jsonschema 4.26 в CI
STANDS: True
ISSUE: Выбор подтверждён (Pydantic 2.14.1 от 2026-10-11, jsonschema 4.26.0, обе MIT). Упущен технический запрет: каноникализация RFC 8785 (rfc8785.py) бросает IntegerDomainError для целых вне +-(2^53-1), а сырые значения TRC20 — uint256.
Кроме того, утверждение 'опубликованного крипто-расширения STIX нет' неверно (есть muchdogesec/stix2extensions), хотя на выбор основного формата это не влияет.
SUGGESTED CHANGE: Закрепить в схеме: все суммы и raw value — строки (decimal string) + отдельное поле decimals; запрет float в модели (strict); тест 'report.json каноникализуется rfc8785 без исключений' на всех 50+ сценариях. Для будущего STIX-
экспорта переиспользовать определения cryptocurrency-wallet / cryptocurrency-transaction из muchdogesec/stix2extensions, следить за UCO #675.

### NEED: Целостность доказательств (integrity seal)
PRIMARY: manifest.json (SHA-256 каждого артефакта) -> RFC 8785 -> Ed25519 -> RFC 3161 (rfc3161-client 1.0.9) -> опционально OpenTimestamps; хеш печатается в колонтитуле PDF
STANDS: False
ISSUE: Набор компонентов подтверждён и остаётся верным, но схема в описанном виде нереализуема: manifest включает sha256 файла report.pdf, и одновременно хеш этого manifest печатается в колонтитуле PDF, а сам manifest вкладывается в
PDF/A-3. Это цикл: содержимое PDF зависит от хеша, который зависит от содержимого PDF. Дополнительно: FreeTSA как дефолт MVP — сервис одного частного лица без ToS, сменивший сертификат в 03.2026; подписывающий Ed25519-ключ лежит
на том же сервере, что и всё остальное, поэтому подпись доказывает меньше, чем заявлено; цены квалифицированных TSA подтверждены только сниппетами.
SUGGESTED CHANGE: Двухуровневая схема: (A) content-manifest = хеши report.json, graph.png и сырых ответов API (без PDF) -> его хеш печатается в колонтитуле и он вкладывается в PDF/A-3; (B) package-manifest = хеши report.pdf + content-manifest +
версии моделей -> JCS -> Ed25519 -> RFC 3161 -> OTS, лежит рядом в evidence-zip. Рендер PDF делать детерминированным (WeasyPrint поддерживает reproducible PDF с 55.0, pdf_identifier). TSA — список из конфига с минимум двумя
независимыми операторами (в trial: публичный Sigstore TSA и/или собственный sigstore/timestamp-authority, коммерческий TSA для платных тарифов), хранить цепочку сертификатов рядом с токеном; отчёт без метки времени помечать
'timestamp pending'.

### NEED: Шаблоны писем биржам / Tether / правоохранительным органам
PRIMARY: Собственные Jinja2-шаблоны (RU/EN) с реестром получателей; PDF через WeasyPrint, опционально DOCX через docxtpl
STANDS: True
ISSUE: Подход верный, но фактическая база слабая: первичные страницы Binance и OKX недоступны и мне (ECONNRESET), страница Tether — 404, то есть обязательные поля запросов никем не подтверждены по первоисточнику. Формулировка 'ни один
канал не принимает обращения не от LE' слишком широкая: TRM Beacon Network заявляет доступ для 'verified investigators (exchanges, law enforcement, and security firms)'. docxtpl: последний релиз 0.20.2 от 2025-11-13, LGPL-2.1 —
для SaaS без распространения допустимо.
SUGGESTED CHANGE: В реестре получателей хранить для каждого поля источник и дату ручной проверки; запись без подтверждённого первичного источника помечать 'unverified' и не выдавать шаблон как 'требования биржи' (иначе нарушается правило 'ничего не
выдумывать'). Добавить в план recovery-агента оценку вступления в TRM Beacon Network как verified investigator — это канал, не требующий статуса госоргана. Письма не должны обещать заморозку.

### NEED: Деплой и CI/CD
PRIMARY: Docker Compose v5 на одном VPS + Caddy + GitHub Actions (build -> GHCR -> ssh: docker compose pull && up -d --wait)
STANDS: True
ISSUE: Версии, лицензии, цены Actions и аргументы против Coolify/Dokploy подтверждены первичными данными. Замечания: (1) 'ноль поверхностей атаки' преувеличено — у Compose есть advisory CVE-2025-62725 (high), а SSH-деплой с GitHub-hosted
runner требует открыть SSH для широких диапазонов адресов; (2) простой при пересоздании контейнера решается без Kamal — пропущен docker-rollout (MIT, v0.14 от 2026-07-12); (3) не рассмотрен Uncloud (Apache-2.0, v0.21.0 от
2026-10-02) как Compose-совместимый путь к нескольким хостам.
SUGGESTED CHANGE: Оставить Compose. Деплой — через self-hosted runner на сервере или pull-модель, SSH закрыть firewall-ом/VPN; образы закреплять по digest; для web/api использовать docker-rollout, когда секунды простоя станут проблемой; Uncloud и
Kamal записать как варианты для второго хоста.

### NEED: VPS-провайдер и эталонная конфигурация
PRIMARY: REF-1: 4 shared vCPU, 8 ГБ RAM, >=75 ГБ NVMe; OVHcloud VPS-2 от €7.21/мес
STANDS: True
ISSUE: Цена подтверждена, но с условием: €7.21 — только при оплате за 12 месяцев вперёд; без обязательств €8.49, на 6 месяцев €8.06 (публичный каталог OVH). Для 'фиксированной эталонной конфигурации' shared vCPU с нераскрытой моделью CPU
— слабая база: разброс steal сделает замеры '30 с / 2 мин / 5 мин' невоспроизводимыми. Оценка ~6 ГБ RAM на 13 контейнеров не измерена; с графовой БД, Chromium/LibreOffice (если понадобится Gotenberg) и пиками WeasyPrint 8 ГБ не
хватит. Встроенный бэкап OVH реплицируется в том же датацентре.
SUGGESTED CHANGE: Продакшен-сервер MVP — OVH VPS-2 (бюджет считать по €8.49, пока нет решения о 12-месячном платеже). Эталонные замеры производительности вести на плане с выделенными ядрами: netcup RS 1000 G12.5 (4 dedicated cores AMD EPYC 9645, 8
ГБ, 128 ГБ NVMe, €21.73/мес при 12 мес) либо фиксировать в протоколе модель CPU, steal и sysbench и публиковать p95. Заложить переход на 16-24 ГБ (OVH VPS-4 8/24/200, €19.96 upfront12), как только определится хранилище графа.

### NEED: Мониторинг, логи, ошибки, uptime
PRIMARY: VictoriaMetrics + VictoriaLogs + Grafana + Alloy; GlitchTip; Uptime Kuma + healthchecks.io
STANDS: True
ISSUE: Все лицензии, версии и ограничения подтверждены. Но это не 'самый лёгкий' вариант: шесть сервисов наблюдаемости на одном 8-ГБ сервере рядом с приложением, RAM-оценка не измерена, у Alloy 1 273 открытых issue. Uptime Kuma: 19
advisories (high unauthenticated DoS от 2026-10-09), конфигурация живёт в БД через UI — плохо сочетается с требованием воспроизводимости. loki.secretfilter при заданном processing_timeout по умолчанию пересылает запись
неотредактированной. Коммерческое использование free-тира healthchecks.io подтверждено только отсутствием запрета на странице цен, ToS не читались.
SUGGESTED CHANGE: Вводить по этапам: MVP — VictoriaLogs + Alloy + Grafana + GlitchTip + внешний heartbeat; VictoriaMetrics/vmalert добавлять вместе с SLO-дашбордом. Вместо Uptime Kuma рассмотреть Gatus (Apache-2.0, v5.37.0, конфигурация в YAML в
git) либо держать Kuma только за VPN. Для лёгких host/container-метрик оценить Beszel (MIT, v0.21.0). В Alloy явно задать drop_on_timeout = true и свои правила Gitleaks под UUID-ключи TronGrid/Tronscan. Все UI — только за
VPN/basic-auth, memory limits на каждый контейнер, замерить RSS стека до фиксации REF-1.

### NEED: Бэкапы
PRIMARY: pgBackRest >= 2.59.3 + restic 0.19.1 -> Backblaze B2 (S3 API, Object Lock)
STANDS: True
ISSUE: Факты подтверждены (MIT, история 'не поддерживается -> продолжается', уязвимость subkeys, цены B2). Недооценено: (1) официального Docker-образа pgBackRest нет, нужен собственный образ PostgreSQL; пакет из стокового репозитория
дистрибутива может быть старее 2.59.3 и оставаться уязвимым; (2) связка pgBackRest + B2 в этой сессии не подтверждена первичным источником (подтверждён только механизм versioning + Object Lock + repo-target-time на S3); (3) под
Object Lock lifecycle-правила B2 не удаляют скрытые версии — фактический объём и счёт будут выше оценки '50 ГБ ~ $0.28'; (4) пропущен сильный новичок 2025-2026: Databasus (ex-Postgresus), Apache-2.0, 8 980 stars, v3.61.0 от
2026-10-10 — физические full/incremental бэкапы, WAL streaming с PITR и встроенная проверка восстановлением.
SUGGESTED CHANGE: Оставить pgBackRest как основной, ставить только из apt.postgresql.org с проверкой версии >= 2.59.3 в CI; провести trial restore именно на B2 (expire, repo-target-time, Object Lock governance) до продакшена и пересчитать стоимость
с учётом retention. Параллельно прогнать Databasus как кандидата на замену или второй контур (учесть: молодой проект, один основной автор, web-панель на сервере — только за VPN). Ночной pg_dump через restic сохранить как
независимый третий путь.

### NEED: Секреты и редакция ключей в логах/отчётах
PRIMARY: SOPS 3.13 + age 1.3 -> Compose secrets (/run/secrets); structlog-процессор + Alloy loki.secretfilter + scrubber sentry-sdk + gitleaks в CI
STANDS: True
ISSUE: Все утверждения о SOPS/age/Compose secrets/secretfilter подтверждены по исходникам и документации. Слабые места: (1) правило 'секреты только из файлов, не из env' не выполнится для сторонних образов, которые читают только
переменные окружения (для GlitchTip и части остальных это не проверено) — нужен перечень исключений с sops exec-env; (2) age-ключ на том же сервере: компрометация хоста раскрывает всё, включая ключ подписи отчётов; (3) секрет в
query-строке URL и INFO-логирование HTTP-клиента — главный реальный путь утечки, тест на него должен быть обязательным гейтом, а не пожеланием; (4) gitleaks v8.30.1 не обновлялся с 2026-03-21, стандартные правила не ловят ключи
формата UUID.
SUGGESTED CHANGE: Оставить SOPS + age. Добавить: таблицу 'сервис -> способ доставки секрета (_FILE / exec-env)'; ключ подписи отчётов держать отдельно от прочих секретов (отдельный age-получатель, по возможности вне сервера приложений); canary-тест
утечки ключей как обязательный CI-гейт по stdout, VictoriaLogs, GlitchTip, report.json и PDF; запрет передачи ключей в query-строке на уровне HTTP-адаптера. fnox (MIT, v1.39.0) и dotenvx (BSD-3-Clause, v2.34.2) зафиксировать как
рассмотренные альтернативы — причин менять SOPS нет.

## VERIFIER FACT CHECKS

- [CONFIRMED] WeasyPrint 70.0 :: Лицензия BSD-3-Clause, релиз v70.0 от 2026-09-08 (security), репозиторий жив, 9 676 stars, 151 open issue
  CORRECT VALUE: BSD-3-Clause (текст LICENSE прочитан), v70.0 опубликован 2026-09-08T12:31Z, pushed 2026-10-13, archived=false, 9 676 stars, 151 open issues. PyPI 70.0: requires_python >=3.10; в main уже >=3.11 (следующий релиз), классификаторы
3.11-3.15. CLI-опции --attachment, --attachment-relationship, --pdf-variant, --pdf-identifier присутствуют в weasyprint/__main__.py.
  METHOD: gh api repos/Kozea/WeasyPrint + releases/latest; чтение LICENSE через contents API; PyPI JSON API; чтение weasyprint/__main__.py и pyproject.toml с raw.githubusercontent.com
  EVIDENCE: https://github.com/Kozea/WeasyPrint/blob/main/LICENSE

- [CORRECTED] WeasyPrint 70.0 :: PDF/A-1..4 поддерживается с v67.0 (2025-12-02)
  CORRECT VALUE: PDF/A появился в 56.0b1 (с финансированием Blueshoe), PDF/UA — в 57.0b1, вложения для PDF/A — в 61.0, варианты PDF/A-?u — в 62.0. В v67.0 (2025-12-02) добавлены только уровни a (PDF/A-1a/2a/3a) и PDF/A-4e/4f. Функция зрелее, чем
написано; docs при этом прямо говорят: 'the result is not guaranteed' — валидатор (veraPDF) обязателен.
  METHOD: скачан и разобран python-скриптом docs/changelog.rst (157 КБ), grep по 'PDF/A', 'attachment' с привязкой к заголовкам версий; чтение docs/common_use_cases.rst
  EVIDENCE: https://raw.githubusercontent.com/Kozea/WeasyPrint/main/docs/changelog.rst

- [CORRECTED] WeasyPrint 70.0 :: По PR #2808 (2026-06) таблица 1200 строк рендерится ~0.9-1.9 с
  CORRECT VALUE: PR #2808 закрыт 2026-07-01 БЕЗ слияния (merged=false). 1935 мс — время на main до оптимизаций, 940 мс — на форке автора PR (warm, in-process, машина автора, число колонок не указано). Мейнтейнер liZe cherry-pick-нул 2 коммита и
вынес главную оптимизацию в свой PR #2813 'Share computed styles between elements' (merged 2026-07-05, milestone 70.0, есть в changelog 70.0). Замеров на релизе 70.0 нет. Мейнтейнер в том же треде: 'speed is not WeasyPrint's main
goal ... we often prefer simple code to fast code'. Docs: 'Tables are known to be slow, especially when they are rendered on multiple pages'. Issue #578 открыт с 2018-02-22.
  METHOD: gh api repos/Kozea/WeasyPrint/pulls/2808 и /issues/2808/comments, /pulls/2813, /issues/578; чтение changelog и common_use_cases.rst. Код не запускался.
  EVIDENCE: https://github.com/Kozea/WeasyPrint/pull/2808

- [CORRECTED] WeasyPrint 70.0 и Gotenberg 8.37.0 (движки PDF) :: Риски безопасности: у WeasyPrint 'частые security-релизы', у Gotenberg — 'SSRF-поверхность, если в HTML попадают внешние URL'; при этом Coolify/Dokploy отвергнуты по числу advisories
  CORRECT VALUE: Критерий применён непоследовательно. Gotenberg: 21 GitHub Security Advisory, из них 20 опубликованы в 2026 (03-28...06-17), включая critical: CVE-2026-42589 'Unauthenticated RCE via ExifTool Metadata Key Injection',
CVE-2026-40281, CVE-2026-40280, CVE-2026-42596 (unauthenticated SSRF), а также high SSRF через LibreOffice (CVE-2026-55229) и чтение файлов /tmp через file:// (CVE-2026-42597). WeasyPrint: 5 advisories, 4 в 2026 — CVE-2026-106443
high 'EPS images reach the Ghostscript interpreter resulting in RCE' (исправлено в 70.0), CVE-2026-55073 SSRF, CVE-2026-49452 CSS injection, CVE-2025-68616 high SSRF bypass. Рекомендованный Uptime Kuma: 19 advisories, 4 в 2026,
последний — high unauthenticated DoS от 2026-10-09. Docker Compose: 1 advisory (CVE-2025-62725, high, path traversal).
  METHOD: gh api repos/{gotenberg/gotenberg,Kozea/WeasyPrint,louislam/uptime-kuma,docker/compose}/security-advisories?per_page=100 с подсчётом по severity и дате
  EVIDENCE: https://github.com/gotenberg/gotenberg/security/advisories

- [CONFIRMED] Gotenberg 8.37.0 :: MIT, v8.37.0 от 2026-09-11, образ gotenberg/gotenberg:8 ~703 МБ
  CORRECT VALUE: MIT (LICENSE прочитан, Copyright Julien Neuhart), v8.37.0 опубликован 2026-09-11, 13 274 stars, 32 open issues; Docker Hub tag 8 обновлён 2026-09-11, amd64 703 МБ, arm64 696 МБ.
  METHOD: gh api + contents/LICENSE; GET Docker Hub API
  EVIDENCE: https://hub.docker.com/v2/repositories/gotenberg/gotenberg/tags/8

- [CONFIRMED] Typst 0.15.1 :: Apache-2.0, v0.15.1 (2026-07-17), PDF/A a-1b...a-4e, ua-1, pdf.attach требует PDF/A-3 или A-4f
  CORRECT VALUE: Apache-2.0, v0.15.1 от 2026-07-17, 56 601 stars. Docs: PDF/A a-1b, a-1a, a-2b, a-2u, a-2a, a-3b, a-3u, a-3a, a-4, a-4f, a-4e; только PDF/UA-1; функция pdf.attach; PDF/A-2 вложения не допускает. typst-py 0.15.0 (2026-06-16) имеет
wheels win/manylinux/mac.
  METHOD: gh api repos/typst/typst, messense/typst-py; WebFetch официальной документации; PyPI JSON
  EVIDENCE: https://typst.app/docs/reference/pdf/

- [CORRECTED] rfc8785 0.1.4 (JCS, Trail of Bits) :: claimed_vs_actual: none found; каноникализация manifest/отчёта по RFC 8785
  CORRECT VALUE: В src/rfc8785/_impl.py: _INT_MAX = 2**53 - 1, _INT_MIN = -(2**53)+1; для целых вне диапазона бросается IntegerDomainError ('exceeds safe integer domain for JSON floats'), для NaN/Inf — FloatDomainError. Сырые значения TRC20
(uint256; USDT с 6 знаками переполняет 2^53 при ~9.007 млрд USDT, токены с 18 знаками — практически сразу) нельзя сериализовать числами: суммы в схеме отчёта обязаны быть строками (decimal string), иначе каноникализация упадёт или
потеряет точность. Версия 0.1.4 от 2024-09-27, Apache-2.0, 13 stars — подтверждено.
  METHOD: чтение исходного кода (grep по _INT_MAX, IntegerDomainError), gh api, PyPI JSON
  EVIDENCE: https://raw.githubusercontent.com/trailofbits/rfc8785.py/main/src/rfc8785/_impl.py

- [CORRECTED] rfc3161-client 1.0.9 :: Apache-2.0, v1.0.9 от 2026-09-14, wheels manylinux/musllinux/macOS, библиотека не делает сетевых вызовов
  CORRECT VALUE: Apache-2.0, v1.0.9 от 2026-09-14, 7 stars, 2 open issues — подтверждено; README: 'This library does not perform any network activity' — подтверждено. Поправка: на PyPI есть и Windows-wheel (cp39-abi3 win) помимо
manylinux/musllinux/macOS, то есть на dev-машине Windows 11 + Python 3.13 ставится без Rust-тулчейна.
  METHOD: PyPI JSON API (разбор списка файлов по платформам), gh api, чтение README
  EVIDENCE: https://pypi.org/pypi/rfc3161-client/json

- [CONFIRMED] FreeTSA :: Endpoint https://freetsa.org/tsr, SHA-256/384/512, сертификат обновлён 2026-03-16 (до 02.2040, ECC P-384), оператор — частное лицо, ToS/SLA нет
  CORRECT VALUE: Всё подтверждено: endpoint /tsr, старый сертификат 2016-2026 недействителен с 03.2026 (tsa.crt_expired), новый — ECC P-384 до 02.2040; явных условий использования нет, 'do not abuse'; для компаний — связаться с оператором
(busindre). Дополнительно: поддержаны также SHA-1/SHA-224.
  METHOD: WebFetch официальной страницы. Запросы к TSA не отправлялись.
  EVIDENCE: https://freetsa.org/index_en.php

- [CORRECTED] OpenTimestamps :: Календари живы; среднее время между транзакциями 1.68 ч (bob) и 5.79 ч (finney), proof через 1.7-5.8 ч
  CORRECT VALUE: alice.btc.calendar.opentimestamps.org на 2026-10-14: Calendar Server v0.7.1, best-block 971311, 330 pending commitments, среднее время между транзакциями за неделю 0.7 ч, баланс 153 447 сат. То есть диапазон по календарям 0.7-5.8
ч плюс ожидание подтверждений Bitcoin; вывод 'не мгновенно, нужен отложенный upgrade' остаётся верным. Значения bob/finney сам не перепроверял.
  METHOD: один GET (WebFetch) к странице календаря
  EVIDENCE: https://alice.btc.calendar.opentimestamps.org/

- [REFUTED] STIX 2.1 :: Опубликованного крипто-SCO/расширения для адресов и транзакций не найдено
  CORRECT VALUE: В официальном oasis-open/cti-stix-common-objects (extension-definition-specifications) крипто-расширений действительно нет. Но опубликованные community Extension Definition существуют: muchdogesec/stix2extensions (Apache-2.0,
pushed 2026-07-27, всего 5 stars) содержит SCO cryptocurrency-wallet и cryptocurrency-transaction с JSON-схемами, extension-definitions и утилитой crypto2stix. Вывод 'STIX не основной формат' не меняется, но будущий экспорт-
адаптер следует строить на этих определениях, а не изобретать свои.
  METHOD: gh api search/code в обоих репозиториях, gh api repos/muchdogesec/stix2extensions, листинг каталога extension-definition-specifications
  EVIDENCE: https://github.com/muchdogesec/stix2extensions

- [CONFIRMED] CASE 1.5.0 / UCO 1.5.0 :: Версии 1.5.0 от 2026-07-24; крипто-классов нет; issue UCO #675 открыт с 2026-03-26
  CORRECT VALUE: UCO 1.5.0 и CASE 1.5.0 опубликованы 2026-07-24; поиск 'cryptocurrency' по коду UCO — 0 совпадений; issue #675 'Cryptocurrency Address and Transaction Representation' open, 5 комментариев, без milestone, последнее обновление
2026-07-08. В теле issue целевым релизом указан UCO 1.5.0 — в вышедший 1.5.0 предложение не попало.
  METHOD: gh api releases/latest, issues/675, search/code
  EVIDENCE: https://github.com/ucoProject/UCO/issues/675

- [CORRECTED] OVHcloud VPS-2 :: 4 vCore / 8 ГБ / 75 ГБ NVMe, 'From €7.21 ex. VAT/month', срок обязательств не указан (предположительно 12 мес upfront)
  CORRECT VALUE: Публичный каталог OVH API (subsidiary IE, EUR, план vps-2027-model2 'VPS-2 2027'): без обязательств €8.49/мес; 6 мес upfront €8.06/мес; 12 мес upfront €7.21/мес (то есть ~€86.52 + НДС единовременно). VPS-1: €4.49 / €4.26 / €3.81.
SLA 99.9%, 1 IPv4, в каталоге доступны образы Ubuntu 24.04 и 26.04. Спецификация 4/8/75 и включённый ежедневный бэкап (реплика в том же датацентре) подтверждены страницей сайта.
  METHOD: keyless GET к публичному каталогу OVH, разбор pricings по mode (default/upfront6/upfront12) python-скриптом; WebFetch ovhcloud.com/en-ie/vps
  EVIDENCE: https://eu.api.ovh.com/v1/order/catalog/public/vps?ovhSubsidiary=IE

- [CONFIRMED] Hetzner Cloud :: Два повышения цен в 2026 (1 апреля и 15 июня); CX33 €6.49->€8.49, CPX32 €13.99->€35.49, CCX13 €15.99->€42.99; CX/CAX недоступны к заказу; уведомление 'Limited availability' с 2026-06-26
  CORRECT VALUE: Страница price-adjustment (создана 2026-06-15, изменена 2026-07-08): с 15 июня 2026 CX23 3.99->5.49, CX33 6.49->8.49, CX43 11.99->15.99, CAX21 7.99->10.49, CPX22 7.99->19.49, CPX32 13.99->35.49, CPX42 25.49->69.49, CCX13
15.99->42.99 (EUR, DE/FI, без НДС и IPv4). Страница cost-optimized: у всех CX/CAX кнопка 'This product is currently unavailable. Please check back later.' status.hetzner.com: 'Limited availability of cloud instances' с 2026-06-26,
'Object Storage in location HEL1 partially degraded' с 2026-09-09. Апрельское повышение на этой странице не описано — сам я его не подтверждал. Цены IPv4 и Object Storage на официальных страницах не отрисовались.
  METHOD: WebFetch трёх официальных страниц Hetzner (price-adjustment, cloud/cost-optimized, status)
  EVIDENCE: https://docs.hetzner.com/general/infrastructure-and-availability/price-adjustment/

- [CONFIRMED] netcup VPS 1000 G12.5 :: 4 vCore / 8 ГБ / 128 ГБ; €14.50 и €16.68 incl. VAT при 12-месячном контракте
  CORRECT VALUE: VPS 500 €8.26/€9.50, VPS 1000 €14.50/€16.68, VPS 2000 €26.92/€30.96 (12 мес, -13%; 24 мес -26%; есть и 1-месячный срок, цена не показана). Числа на странице не сходятся как простые 19% НДС — проверять в корзине. Пропущено аудитом:
линейка Root Server G12.5 с выделенными ядрами AMD EPYC 9645 — RS 1000: 4 dedicated cores / 8 ГБ / 128 ГБ NVMe, €21.73 (€25.00 incl. VAT) при 12 мес.
  METHOD: WebFetch netcup.com/en/server/vps и /en/server/root-server
  EVIDENCE: https://www.netcup.com/en/server/root-server

- [CONFIRMED] Backblaze B2 :: $6.95/ТБ/мес, первые 10 ГБ бесплатно, egress бесплатно до 3x, далее $0.01/ГБ, вызовы классов A-C бесплатны, Object Lock без доплаты
  CORRECT VALUE: Подтверждено дословно: '$6.95/TB/30-days', 'First 10GB storage is always free', egress до 3x среднего объёма бесплатно, далее $0.01/ГБ; Class A/B/C бесплатны, Class D $0.004 за 10 000 (2 500/день бесплатно); нет минимального срока
хранения. Object Lock: governance/compliance/legal hold, без доплаты, работает через S3-совместимый API, не отключается после включения, срок 1-3000 дней. Важный нюанс: 'Locked files are protected from lifecycle rules' — скрытые
версии под lock не удаляются до истечения retention и оплачиваются.
  METHOD: WebFetch страницы цен и docs cloud-storage-object-lock
  EVIDENCE: https://www.backblaze.com/cloud-storage/pricing

- [CONFIRMED] pgBackRest 2.59.3 :: MIT; 2026-04-27 объявлен неподдерживаемым, 2026-05-18 'Will Continue' (AWS, Supabase, pgEdge, Tiger Data, Percona, Eon.io); 2026-10-04 уязвимость 'Weak Encryption Subkeys and Salts', исправлено в 2.59.3
  CORRECT VALUE: MIT (LICENSE прочитан; GitHub API отдаёт NOASSERTION), release/2.59.3 от 2026-10-04, 4 437 stars, 30 open issues. Хронология новостей подтверждена, плюс промежуточный 'Maintenance Update' 2026-05-04. Уточнения: в релизах 2.59.x
спонсоров уже 9 (AWS, Supabase, pgEdge, Tiger Data, Percona, Eon, Xata, Dalibo, Data Egret); апгрейд НЕ заменяет уже созданные слабые subkeys — при слабом subkey нужно пересоздать stanza в новом репозитории; репозитории без
шифрования не затронуты. В issue #2795 (2026-06) обсуждается Object Lock + versioning и опция repo-target-time. Совместимость именно с B2 в этой сессии не подтверждена (в репозитории есть только issue #1039 от 2020).
  METHOD: WebFetch pgbackrest.org/news.html; gh api (метаданные, LICENSE, search/issues, issue #2795)
  EVIDENCE: https://pgbackrest.org/news.html

- [CONFIRMED] restic 0.19.1 :: BSD-2-Clause, v0.19.1 от 2026-07-05; документация рекомендует B2 через S3-совместимый API
  CORRECT VALUE: BSD-2-Clause (LICENSE прочитан), v0.19.1 от 2026-07-05, 36 547 stars. Docs: 'the recommended way to utilize Backblaze B2 is by using its S3-compatible API'. Уточнение, которого нет в аудите: S3-backend в B2 только СКРЫВАЕТ
ненужные файлы; restic рекомендует lifecycle-правило 'Keep only the last version of the file' — а оно не действует на файлы под Object Lock, поэтому расчёт стоимости хранения должен учитывать скрытые версии на весь срок retention.
  METHOD: gh api + чтение LICENSE и исходника документации
  EVIDENCE: https://raw.githubusercontent.com/restic/restic/master/doc/030_preparing_a_new_repo.rst

- [CONFIRMED] VictoriaMetrics + VictoriaLogs + Grafana + Grafana Alloy :: VictoriaMetrics v1.154.0, VictoriaLogs v1.53.0, Alloy v1.20.1 — Apache-2.0; Grafana v13.2.4 — AGPL-3.0; retention VictoriaLogs по умолчанию 7 дней; loki.secretfilter с предупреждением 'Don't rely solely on this component'
  CORRECT VALUE: Версии, даты и лицензии совпали (LICENSE VictoriaLogs прочитан). Docs: retention по умолчанию 7 дней (-retentionPeriod от 1d до 100y), заявление 'up to 30x less RAM' — вендорское. loki.secretfilter: stage general-availability;
дословно 'Don't rely solely on this component to redact sensitive information', 'can increase CPU usage significantly'. Нюанс, не отмеченный в аудите: drop_on_timeout по умолчанию false — запись, не уложившаяся в
processing_timeout, пересылается НЕОТРЕДАКТИРОВАННОЙ; аргумент rate допускает выборочную обработку. vlagent (свой агент VictoriaLogs) умеет discovery только Kubernetes-подов, для Docker-логов нужен Alloy/Vector.
  METHOD: gh api (4 репозитория), чтение исходников документации VictoriaLogs README.md, vlagent.md и Alloy loki.secretfilter.md
  EVIDENCE: https://raw.githubusercontent.com/grafana/alloy/main/docs/sources/reference/components/loki/loki.secretfilter.md

- [CONFIRMED] GlitchTip 6.2.6 / Sentry self-hosted :: GlitchTip MIT, v6.2.6 от 2026-08-07, 512 МБ RAM, PostgreSQL 14+; Sentry self-hosted требует 4 ядра, 16 ГБ RAM + 16 ГБ swap, лицензия FSL
  CORRECT VALUE: GitLab API: лицензия MIT, тег v6.2.6 (2026-08-07), 359 stars, last_activity 2026-10-13. Docs: 'Recommended system requirements: 512 MB RAM', минимум 256 МБ, PostgreSQL 14+, Valkey/Redis 7+ опционален, retention 90 дней. Sentry: '4
CPU Cores', '16 GB RAM + 16 GB swap', рекомендовано 32 ГБ, FSL с запретом продавать self-hosted как предложение; self-hosted 26.9.0 от 2026-09-16.
  METHOD: GitLab REST API (project?license=true, repository/tags); WebFetch glitchtip.com и develop.sentry.dev/self-hosted; gh api
  EVIDENCE: https://glitchtip.com/documentation/install

- [CONFIRMED] Docker Compose v5.6.0 + Caddy 2.11.7 + GitHub Actions :: Compose v5.6.0 (2026-10-02), Caddy v2.11.7 (2026-10-03), обе Apache-2.0; secrets только для Linux-контейнеров, в /run/secrets; GitHub Free 2 000 мин/мес, Linux 2-core $0.006/мин, self-hosted runner бесплатен
  CORRECT VALUE: Версии и лицензии совпали. Docs Docker: 'Secrets are mounted as a file in /run/secrets/<secret_name>', 'Secrets are supported on Linux containers only'. GitHub: Free 2 000 мин + 500 МБ артефактов, Pro/Team 3 000; Linux 1-core
$0.002, Linux 2-core $0.006, Windows 2-core $0.010, macOS $0.062 за минуту; 'GitHub Actions usage is free for self-hosted runners and for public repositories'.
  METHOD: gh api; WebFetch docs.docker.com/compose/how-tos/use-secrets и двух страниц docs.github.com/billing
  EVIDENCE: https://docs.github.com/en/billing/reference/actions-runner-pricing

- [CONFIRMED] Coolify 4.4.6 / Dokploy 0.30.8 / Kamal 2.12.0 :: Coolify: 70+ advisories с critical/high в 06-07.2026; Dokploy: 60, пачка critical от 2026-07-21, лицензия Apache-2.0 + /proprietary; Kamal: 0 advisories, issue #1350 про Windows открыт
  CORRECT VALUE: Coolify: 70 advisories (21 critical, 26 high; 61 опубликованы в 2026, последний 2026-07-02), CVE-2026-57498 critical, CVE-2026-41896 и CVE-2026-42204 high — найдены. Dokploy: 60 (34 critical, 17 high; 56 в 2026, последний
2026-07-21), CVE-2026-72864 и CVE-2026-72737 critical; LICENSE.MD: Apache-2.0 + каталоги /proprietary под LICENSE_PROPRIETARY. Kamal: 0 advisories, v2.12.0 (2026-06-18), MIT; #1350 — открытый PR от 2025-01-10 'Fix secrets adapters
failing fetch on Windows'; docs установки: нужен Ruby либо запуск в контейнере 'though this has some limitations', Windows/WSL не упомянуты.
  METHOD: gh api security-advisories?per_page=100 с агрегацией, contents/LICENSE.MD, issues/1350; WebFetch kamal-deploy.org/docs/installation
  EVIDENCE: https://github.com/coollabsio/coolify/security/advisories

- [CONFIRMED] SOPS 3.13.3 + age 1.3.2 :: SOPS MPL-2.0, v3.13.3 (2026-07-23); age BSD-3-Clause, v1.3.2 (2026-08-29); exec-env/exec-file, SOPS_AGE_KEY / _FILE / _CMD; гибридные post-quantum ключи age
  CORRECT VALUE: Всё подтверждено по исходникам: age/keysource.go объявляет SOPS_AGE_KEY, SOPS_AGE_KEY_FILE, SOPS_AGE_KEY_CMD (и SOPS_AGE_RECIPIENT, SOPS_AGE_SSH_PRIVATE_KEY_FILE/_CMD); cmd/sops/main.go — подкоманды exec-env и exec-file; README
age: 'age-keygen -pq', поддержка встроена с v1.3.0.
  METHOD: gh api (метаданные, LICENSE SOPS), grep исходников SOPS и README age
  EVIDENCE: https://raw.githubusercontent.com/getsops/sops/main/age/keysource.go

- [CONFIRMED] healthchecks.io / Grafana Cloud Free :: healthchecks.io Hobbyist: 20 проверок бесплатно, Business $20/мес (100 проверок), условий про коммерческое использование нет; Grafana Cloud Free: 10k series, 50 ГБ логов, 14 дней, 3 пользователя; Pro $19/мес + usage
  CORRECT VALUE: healthchecks.io: Hobbyist $0 / 20 checks / 100 log entries, Supporter $5, Business $20 ($192/год) / 100 checks, Business Plus $80 / 1 000; запрета коммерческого использования на странице нет (есть только запрет обходить лимиты
несколькими аккаунтами). Сам сервис open-source (healthchecks/healthchecks, BSD-3-Clause, v4.4). Grafana Cloud Free: 10k series, по 50 ГБ logs/traces/profiles, retention 14 дней, 3 пользователя, 100k API synthetic executions; Pro
$19 + $6.50/1k series, логи $0.05 + $0.40 + $0.10 = ~$0.55/ГБ (в аудите ~$0.50). ToS обоих сервисов не читались.
  METHOD: WebFetch официальных страниц цен; gh api healthchecks/healthchecks
  EVIDENCE: https://healthchecks.io/pricing/

- [CORRECTED] Playwright (playwright-python) :: playwright-python v1.63.0 (2026-09-15)
  CORRECT VALUE: GitHub releases/latest microsoft/playwright-python: v1.64.0, опубликован 2026-10-13 (вчера) — данные аудита устарели на один релиз. Apache-2.0. На решение не влияет.
  METHOD: gh api repos/microsoft/playwright-python + releases/latest
  EVIDENCE: https://github.com/microsoft/playwright-python/releases

- [UNVERIFIABLE] Каналы запросов: Binance / OKX / Tether / Kodex :: Kodex 'trusted by 15K+ government agencies', клиенты Coinbase, Bitfinex, Bitget; порталы только для госорганов; ни один канал не принимает обращения от частных лиц; у Tether публичной процедуры нет
  CORRECT VALUE: Kodex подтверждён дословно ('Trusted by 15K+ government agencies worldwide'; Coinbase, Bitfinex, Bitget). Страницы Binance (support/law-enforcement) и OKX (law-enforcement-request-guide) у меня тоже вернули ECONNRESET;
tether.io/law-enforcement/ — 404. Требования к полям запросов из первичных источников не подтверждены никем. Утверждение 'ни один канал не принимает не-LE' слишком широкое: TRM Beacon Network на своей странице заявляет, что
помечать адреса могут 'Verified investigators (exchanges, law enforcement, and security firms)', а базовое членство бесплатно для проверенных бирж и crypto service providers.
  METHOD: WebFetch kodexglobal.com и trmlabs.com/beacon-network; три неудачные попытки открыть первичные страницы Binance/OKX/Tether
  EVIDENCE: https://www.trmlabs.com/beacon-network

- [CONFIRMED] Cloudflare R2 / Infisical / Railway / Fly.io (отвергнутые альтернативы) :: R2 $0.015/ГБ, Class A $4.50/млн, Class B $0.36/млн, free 10 ГБ; Infisical Free 5 identities, Pro $20/$23 за identity; Railway $10/ГБ RAM и $20/vCPU; Fly shared-cpu-1x 1 ГБ $6.70, Managed Postgres от $38, free tier нет
  CORRECT VALUE: Все числа совпали с официальными страницами. Дополнение по непроверенному в аудите пункту: R2 поддерживает Bucket Locks (retention на срок, до даты или бессрочно, до 1 000 правил, перекрывают lifecycle), но настраиваются через
dashboard/Wrangler/Cloudflare API — совместимость с S3 Object Lock API на странице не заявлена. Promtail EOL 'as of March 2, 2026' и формулировка Loki про Docker-установку ('evaluating, testing, or developing', для production —
Helm или Tanka; Loki 3.7.0) также подтверждены.
  METHOD: WebFetch developers.cloudflare.com/r2/pricing и /r2/buckets/bucket-locks, infisical.com/pricing, docs.railway.com/reference/pricing/plans, docs.fly.io/about/pricing, grafana.com/docs/loki
  EVIDENCE: https://developers.cloudflare.com/r2/buckets/bucket-locks/

## CANDIDATES MISSED BY THE RESEARCHER (found by verifier)

- PlutoPrint 0.22.0 / PlutoBook 0.19.0 (https://github.com/plutoprint/plutoprint)
  WHY: Новый (2024-2026) HTML/CSS paged-media движок на C++ без браузера с Python-биндингом: прямой конкурент WeasyPrint по главному риску — скорости длинных таблиц; готовые wheels для win_amd64/manylinux/macOS под cp310-cp314 (dev-
машина Windows 11 + Python 3.13 без MSYS2).
  ASSESSMENT: plutoprint: MIT, v0.22.0 от 2026-08-04, 1 165 stars, 7 open issues; plutobook: MPL-2.0, v0.19.0, pushed 2026-10-13. JavaScript не поддерживается (в планах). PDF/A и вложения в README не заявлены; скорость подтверждена только
отзывом пользователя в README ('10x'). Версия 0.x. Вердикт: needs-trial — включить в тот же бенчмарк 1k-50k строк; не готов заменить WeasyPrint там, где нужен PDF/A-3 с вложениями. Проверено: gh api + PyPI JSON + README plutobook;
код не запускался.

- Databasus v3.61.0 (ex-Postgresus) (https://github.com/databasus/databasus)
  WHY: Сильный новичок 2025 года в бэкапах PostgreSQL: физические full/incremental бэкапы, WAL streaming с PITR, встроенная проверка бэкапа реальным восстановлением, S3/R2/SFTP, уведомления в Telegram — закрывает требование 'еженедельный
restore-тест' из коробки и снижает зависимость от bus-factor pgBackRest.
  ASSESSMENT: Apache-2.0, 8 980 stars, создан 2025-06-05, v3.61.0 от 2026-10-10, 3 open issues, PostgreSQL 14-18. Риски: проекту 16 месяцев, фактически один основной автор, web-панель с доступом к БД и учёткам хранилища на том же сервере
(держать за VPN), Object Lock не заявлен. Вердикт: needs-trial рядом с pgBackRest. Проверено: gh api + README; не запускался.

- netcup Root Server RS 1000 G12.5 (https://www.netcup.com/en/server/root-server)
  WHY: Эталонная конфигурация для замеров производительности требует предсказуемого CPU; это ближайший к REF-1 план с выделенными ядрами и раскрытой моделью процессора.
  ASSESSMENT: 4 dedicated cores AMD EPYC 9645 (до 3.7 ГГц), 8 ГБ RAM, 128 ГБ NVMe, €21.73/мес (€25.00 incl. VAT) при 12-месячном контракте; есть сроки 1/12/24 мес. В 3 раза дороже OVH VPS-2, но в 1.6 раза дешевле Hetzner CPX32 и с выделенными
ядрами. Числа на странице не сходятся как 19% НДС — проверить в корзине. Вердикт: кандидат на роль эталонного стенда для замеров. Проверено: WebFetch страницы netcup.

- docker-rollout v0.14 (https://github.com/wowu/docker-rollout)
  WHY: Закрывает единственный названный минус Compose ('секунды простоя при пересоздании контейнера') без перехода на Kamal: Docker CLI-плагин, заменяющий docker compose up -d на docker rollout с ожиданием healthcheck.
  ASSESSMENT: MIT, 3 353 stars, v0.14 от 2026-07-12, pushed 2026-10-08, 9 open issues; один shell-скрипт. В README есть раздел Caveats (ограничения на сервисы; текст раздела не читал). Вердикт: лёгкое дополнение к рекомендованному стеку.
Проверено: gh api + README.

- Uncloud v0.21.0 (https://github.com/psviderski/uncloud)
  WHY: Появившийся в 2024-2026 инструмент деплоя Compose-файлов на несколько Docker-хостов без control plane (WireGuard mesh, ingress с HTTPS, rolling updates) — естественный следующий шаг после одного сервера, альтернатива Kamal и k3s.
  ASSESSMENT: Apache-2.0, 5 527 stars, v0.21.0 от 2026-10-02, 87 open issues, версия 0.x; README: автоматический rollback 'coming soon'. Вердикт: записать в раздел 'что меняется на масштабе' рядом с Kamal; для MVP не нужен. Проверено: gh api +
README.

- Gatus v5.37.0 (https://github.com/TwiN/gatus)
  WHY: Uptime/health-мониторинг с конфигурацией в YAML (в git, воспроизводимо) вместо Uptime Kuma с настройкой через UI и 19 security advisories.
  ASSESSMENT: Apache-2.0, 12 298 stars, v5.37.0 от 2026-09-24, один Go-бинарь; проверки HTTP/ICMP/TCP/DNS с условиями, алерты (Slack, Telegram и др.). Вердикт: предпочтительнее Uptime Kuma для команды, которой важны config-as-code и минимальная
поверхность атаки. Проверено: gh api + README.

- Beszel v0.21.0 (https://github.com/henrygd/beszel)
  WHY: Лёгкий мониторинг хоста и Docker-контейнеров (история, алерты) — кандидат на 'самый лёгкий' контур метрик вместо VictoriaMetrics + Grafana на первом этапе.
  ASSESSMENT: MIT, 26 167 stars, создан 2024-07, v0.21.0 от 2026-10-02, hub на PocketBase + agent. Не заменяет прикладные метрики/SLO (стоимость расследования, доля успешных запросов) — только инфраструктурные. Вердикт: вариант для этапа 0,
если RAM в дефиците. Проверено: gh api + README.

- Sigstore timestamp-authority v2.1.4 (и публичный экземпляр timestamp.sigstore.dev) (https://github.com/sigstore/timestamp-authority)
  WHY: RFC 3161 TSA под управлением проекта Sigstore (OpenSSF) — более институциональная альтернатива FreeTSA как бесплатный TSA и/или self-hosted TSA; аудит проверил Sigstore только на уровне метаданных Rekor.
  ASSESSMENT: Apache-2.0, v2.1.4 от 2026-10-07, 140 stars. GET https://timestamp.sigstore.dev/api/v1/timestamp/certchain вернул HTTP 200 и PEM-цепочку (1 519 байт) — публичный экземпляр жив. Политика использования, rate limits и SLA публичного
TSA в этой сессии не найдены (docs.sigstore.dev/logging/overview их не описывает) — перед включением в fallback-список прочитать условия. Вердикт: needs-trial как второй TSA. Проверено: gh api + один keyless GET.

- TRM Labs Beacon Network (https://www.trmlabs.com/beacon-network)
  WHY: Сеть оперативного обмена сигналами о похищенных средствах между биржами, эмитентами стейблкоинов и LE; прямо относится к recovery-контуру и опровергает тезис аудита, что все каналы закрыты для не-госорганов.
  ASSESSMENT: По странице TRM: помечать адреса могут 'Verified investigators (exchanges, law enforcement, and security firms)'; уровни Affiliate (Free), Partner, DeFi; на странице логотипы Coinbase, Binance, Kraken, OKX, PayPal, Stripe, Ripple.
Дата запуска, процедура верификации и цена уровня Partner на странице не указаны; доступ через форму запроса демо. Вердикт: изучить условия вступления как отдельную задачу. Проверено: только WebFetch маркетинговой страницы TRM,
независимого подтверждения нет.

- muchdogesec/stix2extensions (STIX 2.1 SCO cryptocurrency-wallet / cryptocurrency-transaction) (https://github.com/muchdogesec/stix2extensions)
  WHY: Опубликованные Extension Definition для крипто-кошельков и транзакций — аудит утверждал, что таких нет; пригодится для STIX-экспорта.
  ASSESSMENT: Apache-2.0, pushed 2026-07-27, всего 5 stars; JSON-схемы, extension-definitions и утилита crypto2stix. Не стандарт OASIS, экосистема крошечная. Вердикт: не основной формат, но готовая база для экспорт-адаптера. Проверено: gh api
search/code.

- veraPDF v1.30.3 (https://github.com/veraPDF/veraPDF-library)
  WHY: Аудит рекомендует PDF/A-3 и сам пишет, что валидность 'не гарантируется', но валидатор не аудировал; без него требование PDF/A непроверяемо.
  ASSESSMENT: GitHub API: GPL-3.0, v1.30.3 от 2026-10-09, 346 stars, pushed 2026-10-12. Использование как отдельного CLI в CI/контейнере copyleft-обязательств на код платформы не создаёт (так же, как Barman в аудите). Требует JVM — запускать в
CI или отдельным образом, не в рантайме рендера. Проверено: gh api (метаданные); условия двойного лицензирования не читал.

- fnox v1.39.0 / dotenvx v2.34.2 (https://github.com/jdx/fnox)
  WHY: Новые (2025) инструменты шифрованных секретов в git с age-провайдером (fnox) и шифрованных .env (dotenvx) — не упомянуты в аудите секретов.
  ASSESSMENT: fnox: MIT, создан 2025-10-18, 2 271 stars, v1.39.0 от 2026-10-06; README предупреждает: без настроенного провайдера 'fnox set writes a plaintext default'. dotenvx: BSD-3-Clause, 5 834 stars, v2.34.2 от 2026-10-09. Оба моложе и
менее проверены, чем SOPS (CNCF, 23 377 stars). Вердикт: причин менять SOPS + age нет; зафиксировать как рассмотренные. Проверено: gh api + README fnox.

============================================================
PART 2 - RESEARCHER AUDIT
============================================================

## RESEARCHER RECOMMENDATIONS

### R1. NEED: PDF-рендеринг evidence-отчёта и писем
PRIMARY: WeasyPrint 70.0 + Jinja2-шаблоны HTML/CSS в Linux-контейнере (PDF/A-3 с вложенными report.json и manifest.json)
RATIONALE: Один HTML/CSS-шаблон обслуживает и web-версию, и PDF; BSD-3-Clause; чистый Python (3.13 поддержан) без браузера; нативные @page-счётчики страниц, повторяющиеся заголовки таблиц, кликабельные ссылки на explorer, PDF/A и вложения
файлов — можно вшить машинно-читаемый JSON и manifest прямо в PDF. Проект жив (релиз 2026-09-08, коммиты вчера).
ARCHITECTURE NOTES: Отдельный worker-контейнер report-renderer (python:3.13-slim + libpango + шрифты Noto/DejaVu/PT). Письма биржам/Tether/LE — те же Jinja2-шаблоны (RU/EN) -> PDF; если юристам нужен редактируемый Word — добавить docxtpl 0.20.2
(LGPL-2.1) с конвертацией через LibreOffice.
COST: $0 лицензий и API; CPU сервера. На отчёт: секунды CPU (по данным PR #2808 ~1–2 с на 1 200 строк; собственный замер обязателен).
DATA QUALITY VERIFICATION: Golden-тесты в CI: (1) извлечь текст PDF (pypdf 6.20.1) и проверить, что каждый TXID из report.json присутствует и число link-аннотаций равно числу TXID; (2) проверка отсутствия .notdef/tofu на смешанном кириллица+латиница наборе
и встраивания шрифтов; (3) валидация PDF/A-3 внешним валидатором (veraPDF — не аудировался); (4) бенчмарк рендера на 100 / 1 000 / 5 000 / 10 000 строк на эталонном сервере с порогом (например <=20 с на 5 000 строк); (5) sha256
вложенного report.json внутри PDF совпадает с manifest.
RISKS: Медленные многостраничные таблицы (признано в docs); ограниченный SVG — граф вставлять PNG 2x или упрощённым SVG; на Windows-деве рендерить в Docker; регулярные security-обновления; HTML отчёта формировать только из проверенных
данных с автоэкранированием Jinja2 и запретом сетевых загрузок (свой URLFetcher).
REPLACEABILITY: Высокая: интерфейс render(html, assets) -> pdf; замена на Gotenberg — смена адаптера без переписывания шаблонов.
REJECTED ALTERNATIVES:
  - Gotenberg 8.37 / Playwright (Chromium): Не отвергнуты, а оставлены запасным движком за тем же интерфейсом render(html)->pdf: +700 МБ образ и 0.5–1 ГБ RAM, PDF/A только пост-обработкой; брать, если WeasyPrint не уложится по
  - времени на таблицах 5–10 тыс. строк или нужен JS-граф.
  - Typst 0.15.1: Быстрый и с PDF/A, но отдельный язык шаблонов (двойная вёрстка с web-отчётом) и версия 0.x с ломающими изменениями; needs-trial как план Б для очень больших отчётов.
  - ReportLab 5.0.1: Императивная вёрстка в коде; шаблонный RML только в коммерческом ReportLab PLUS.
  - wkhtmltopdf: Репозиторий archived, последний релиз 2020-06-10, проект сам запрещает недоверенный HTML.
  - react-pdf / pdfmake / Paged.js / LaTeX: Второй рантайм (Node) или отдельный язык, нет PDF/A и вложений; у Paged.js нет релизов с 2023-07.

### R2. NEED: JSON-отчёт: схема и версионирование
PRIMARY: Pydantic 2.14 модели -> публикуемый JSON Schema 2020-12 с полем schema_version (SemVer) + проверка python-jsonschema 4.26 в CI
RATIONALE: Обе библиотеки MIT, активны, поддерживают Python 3.13; модель делает правило «каждый факт имеет TXID, каждая метка — source/checked_at/confidence» структурно обязательным (отчёт без TXID просто не сериализуется). Существующие
стандарты обмена доказательствами крипто-расследования не покрывают: в STIX 2.1 нет SCO для адресов/транзакций, в CASE/UCO 1.5.0 крипто-классы только предложены (issue #675 открыт), IVMS101 — про Travel Rule.
ARCHITECTURE NOTES: В отчёт включать блок provenance: версии моделей LLM, параметры, список источников данных с временем запроса, идентификатор запуска, ссылку на журнал действий агентов (в PostgreSQL, не в логах). Сырые ответы API хранить как
отдельные артефакты и включать их sha256 в manifest.
COST: $0.
DATA QUALITY VERIFICATION: CI: все 50+ тестовых сценариев сериализуются и валидируются по опубликованной схеме; тест обратной совместимости (отчёты предыдущих minor-версий читаются); property-тест «нет Fact без txid»; хеш каноничного JSON (RFC 8785)
стабилен между запусками при одинаковом входе.
RISKS: Собственная схема = нет готовых потребителей; смягчается публикацией schema + примеров и адаптерами экспорта (STIX/CASE) при появлении спроса.
REPLACEABILITY: Высокая: наружу отдаётся стандартный JSON Schema.
REJECTED ALTERNATIVES:
  - STIX 2.1 как основной формат: Нет стандартных объектов для криптовалютных адресов и транзакций; получатели (биржи, Tether) STIX не требуют. Возможен как дополнительный экспорт позже.
  - CASE/UCO 1.5.0: Проверено по онтологии: 0 вхождений «crypto» в observable.ttl, предложение #675 не принято; RDF/SHACL-стек тяжёл для MVP.
  - IVMS101: Стандарт данных отправителя/получателя между VASP, не формат доказательств.

### R3. NEED: Целостность доказательств (integrity seal)
PRIMARY: manifest.json (SHA-256 каждого артефакта) -> каноникализация RFC 8785 -> подпись Ed25519 ключом платформы -> RFC 3161 timestamp хеша manifest (rfc3161-client 1.0.9; TSA по конфигу) -> опционально OpenTimestamps-proof; хеш
печатается в колонтитуле PDF
RATIONALE: Каждый слой отвечает на свой вопрос: хеши — «не изменено», подпись — «выпущено платформой», RFC 3161 — «существовало не позже момента T» по общепринятому у юристов стандарту, OpenTimestamps — независимая от TSA привязка к Bitcoin.
Все компоненты Apache-2.0/MIT/LGPL-как-библиотека, стоимость около нуля. Календари OTS живы (проверено GET-запросами 2026-10-14).
ARCHITECTURE NOTES: Токен .tsr, цепочку сертификатов TSA, .ots-proof и публичный ключ класть в evidence-пакет (zip) рядом с report.json/report.pdf и вкладывать manifest в PDF/A-3. Запросы к TSA содержат только хеш — данные расследования наружу не
уходят.
COST: MVP: $0 (FreeTSA + OTS). Production: ~€0.03–0.04 за отчёт при квалифицированной метке (цены по сниппетам, не подтверждены) — в пределах бюджета $1 на расследование.
DATA QUALITY VERIFICATION: Автотест: пересчитать sha256 всех артефактов по manifest; проверить подпись Ed25519; проверить TSA-токен через VerifierBuilder с закреплённым корневым сертификатом TSA и совпадением message imprint; отложенная задача ots
upgrade/verify через 24 ч; негативный тест — изменение одного байта отчёта должно проваливать проверку. Публичная страница/CLI verify для получателя отчёта.
RISKS: Компрометация или потеря подписывающего ключа (хранить в SOPS/age, ротация с публикацией старых публичных ключей); недоступность TSA (fallback-список, отчёт выпускается с пометкой «timestamp pending», без выдумывания); юридическая
сила зависит от юрисдикции.
REPLACEABILITY: Высокая: TSA и слой OTS меняются конфигурацией; формат manifest свой и простой.
REJECTED ALTERNATIVES:
  - Только OpenTimestamps: Подтверждение через 1.7–5.8 ч (по страницам календарей), нет SLA, малоизвестен судам; оставлен как дополнительный слой.
  - Только FreeTSA как единственный TSA: Оператор — частное лицо, нет ToS/SLA, сертификат менялся в 03.2026; для платных отчётов нужен коммерческий/квалифицированный TSA с fallback.
  - pyHanko PAdES-подпись PDF в MVP: Требует X.509-сертификата организации; README автора называет проект beta; оставлен как needs-trial для платных тарифов.
  - rfc3161ng: Последний релиз 2020-10-30, заброшен.

### R4. NEED: Шаблоны писем биржам / Tether / правоохранительным органам
PRIMARY: Собственные Jinja2-шаблоны (RU/EN) с реестром получателей: канал, обязательные поля, дата проверки, источник; PDF через тот же WeasyPrint, опционально DOCX через docxtpl
RATIONALE: Готовых открытых шаблонов и машинного стандарта запроса не найдено (поиск по GitHub — 0 результатов; порталы Kodex/Binance LERS принимают запросы только от верифицированных госорганов). Значит, реалистичный продукт — проект письма
и evidence-пакет для передачи жертвой/юристом в полицию и биржу, а не «отправка запроса на заморозку».
COST: $0 инструментов; разовая юридическая вычитка шаблонов (вне оценки).
DATA QUALITY VERIFICATION: Каждое поле письма заполняется только из верифицированных фактов отчёта (TXID, адрес, сумма, время UTC, ссылка на explorer); тест «нет незаполненных плейсхолдеров»; реестр получателей с датой проверки и автоматическим
предупреждением, если запись старше N дней; в письме явно разделять факты и предположения (метки с confidence).
RISKS: Регламенты бирж меняются; первичные страницы Binance/OKX/Tether в ходе аудита открыть не удалось — поля шаблонов нужно сверить вручную; юридические формулировки зависят от юрисдикции; риск создать у пользователя ложное ожидание
возврата средств.
REPLACEABILITY: Высокая (шаблоны — текстовые файлы).
REJECTED ALTERNATIVES:
  - Прямая подача через Kodex / Binance LERS: Доступ только для проверенных правоохранительных органов; частная платформа подать запрос не может.
  - Прямое обращение в Tether/T3 FCU от имени жертвы: По всем найденным источникам Tether действует по запросам LE; официальной публичной процедуры для частных лиц не найдено.
  - STIX/CASE-пакет как формат запроса: Получатели его не запрашивают; в стандартах нет крипто-объектов.

### R5. NEED: Деплой и CI/CD
PRIMARY: Docker Compose v5 на одном VPS + Caddy (TLS) + GitHub Actions (build -> GHCR -> ssh: docker compose pull && up -d --wait)
RATIONALE: Тот же compose.yaml работает на dev-машине (Windows 11 + Docker) и на сервере; ноль дополнительных управляющих сервисов и поверхностей атаки; Apache-2.0; 2 000 бесплатных минут Actions в месяц для приватного репозитория. Панели
Coolify и Dokploy отвергнуты по фактическим данным GitHub Security Advisories за 2026 год.
ARCHITECTURE NOTES: Сервисы: caddy, api, worker(s), report-renderer, web, postgres (+pgBackRest), valkey/redis, victoria-metrics, victoria-logs, grafana, alloy, glitchtip, uptime-kuma. Наружу открыты только 80/443 (Caddy) и SSH;
Grafana/GlitchTip/Kuma — за basic-auth/VPN. Лимиты памяти и restart-политики на каждый контейнер.
COST: $0/мес (Compose, Caddy, GitHub Actions в пределах 2 000 мин; сверх — $0.006/мин Linux 2-core).
DATA QUALITY VERIFICATION: CI-гейты до деплоя: тесты, 50+ сценариев с ground truth, сравнение AI-слоя с baseline, gitleaks-скан репозитория, сборка образов с фиксированными digest; после деплоя — smoke-тест /healthz и синтетическое расследование известного
TXID; образы помечаются git SHA для воспроизводимости и отката.
RISKS: Секунды простоя при обновлении; единая точка отказа (один сервер); SSH-ключ деплоя в GitHub Secrets — ограничить отдельным пользователем без sudo, только docker compose в каталоге проекта.
REPLACEABILITY: Высокая: те же образы запускаются Kamal или k3s.
REJECTED ALTERNATIVES:
  - Kamal 2.12.0: Хороший вариант №2 (zero-downtime, 0 advisories), но требует Ruby/WSL на Windows (issue #1350 открыт), registry и отдельного управления accessories — лишний слой для одного сервера. Перейти, когда понадобится
  - деплой без простоя или второй хост.
  - Coolify 4.4.6: 70+ advisories, включая critical/high RCE до root и cross-team IDOR, опубликованные в 06–07.2026; панель с root-доступом рядом с API-ключами и материалами расследований.
  - Dokploy 0.30.8: Пачка critical advisories от 2026-07-21 (root на хосте, утечка S3-учёток бэкапов); смешанная лицензия Apache + proprietary.
  - k3s: Kubernetes-операционка не окупается на одном сервере; вариант для масштаба.
  - Fly.io / Railway / Render: В 5–20 раз дороже VPS при постоянно работающем стеке (Railway ~ $160/мес за 4 vCPU/8 ГБ; Fly Managed Postgres от $38/мес); данные у третьей стороны.

### R6. NEED: VPS-провайдер и эталонная конфигурация
PRIMARY: Эталон REF-1 по спецификации: 4 shared vCPU x86-64, 8 ГБ RAM, >=75 ГБ NVMe, 1 Гбит/с, EU, Ubuntu 24.04 LTS + Docker Engine/Compose v5. Самый дешёвый проверенный SKU под неё — OVHcloud VPS-2 (от €7.21/мес без НДС, ежедневный бэкап
включён)
RATIONALE: Рынок VPS в 2026 нестабилен (дефицит памяти, повышения цен): Hetzner поднял цены 1 апреля и 15 июня, дешёвые CX/CAX недоступны к заказу с лета (статус-уведомление с 2026-06-26), CPX32 стоит €35.49. Поэтому эталон надо фиксировать
спецификацией, а не SKU одного провайдера, и записывать в протокол замеров модель CPU, steal и результаты sysbench. Сетевые цели (<=30 с, <=2 мин, <=5 мин) ограничены в основном rate-limit источников, а не CPU.
ARCHITECTURE NOTES: Оценка RAM (не измерено): PostgreSQL 1.5 ГБ, api+workers 1.5, web 0.4, valkey 0.2, renderer пик 0.5, VictoriaMetrics+VictoriaLogs 0.6, Grafana 0.3, Alloy 0.25, GlitchTip 0.5, Kuma 0.15 => ~6 ГБ. На масштабе: вынести PostgreSQL на
отдельный узел/managed, воркеры — на отдельные узлы (Kamal multi-host или k3s), мониторинг — на отдельный узел или Grafana Cloud Pro ($19/мес + usage).
COST: Сервер: ~€7–9/мес (OVH VPS-2, вероятно при оплате за 12 мес) | ~€15–17/мес (netcup) | ~€36/мес (Hetzner CPX32 + IPv4 €0.50). Весь минимальный контур: сервер + B2 (<=10 ГБ бесплатно, далее ~$0.007/ГБ) + домен (~$1/мес, не
проверено) => ориентир €9–18/мес, либо ~€38/мес на Hetzner. При росте до 16 ГБ RAM: OVH VPS-4 (8 vCore/24 ГБ) €19.96 или netcup VPS 2000 €26.92.
DATA QUALITY VERIFICATION: Протокол замеров производительности: фиксировать SKU, CPU model (lscpu), steal% за время теста, sysbench cpu/fileio, версии образов (digest), лимиты и фактический RPS источников; каждый целевой показатель (30 с / 2 мин / 5 мин на
1 000 адресов) мерить >=5 раз и публиковать медиану и p95; повторять замер после смены провайдера/тарифа.
RISKS: Shared vCPU даёт разброс; 8 ГБ впритык, если в стек добавится графовая БД (тогда 16 ГБ); 12-месячные обязательства; ценовая волатильность 2026 года; один сервер = единая точка отказа (RTO определяется временем восстановления из
бэкапа на новый VPS).
REPLACEABILITY: Высокая: весь стек в Compose, перенос = новый VPS + restore из pgBackRest/restic.
REJECTED ALTERNATIVES:
  - Hetzner CPX32 (€35.49) / CX33 (€8.49, недоступен): Не отвергнут технически (почасовая оплата, API, снапшоты), но в 5 раз дороже OVH/netcup при тех же 4/8, а дешёвая линейка недоступна новым клиентам. Разумен как альтернатива,
  - если нужен hourly billing; CCX13 (dedicated, €0.0689/ч) удобен для разовых контрольных замеров на выделенных vCPU.
  - netcup VPS 1000 G12.5 (~€14.5–16.7/мес, 12 мес): Хорошая альтернатива с 128 ГБ диска; вдвое дороже OVH и с контрактным сроком; точную net-цену нужно проверить в корзине.
  - Contabo Cloud VPS 4 (€4.40–5.50): Цена при 24-месячном сроке; сообщения о высокой вариативности CPU — плохо для эталонных замеров.
  - DigitalOcean Basic 8 ГБ ($48/мес): В 5–6 раз дороже при тех же спецификациях.

### R7. NEED: Мониторинг, логи, ошибки, uptime
PRIMARY: Self-hosted: VictoriaMetrics + VictoriaLogs + Grafana + Grafana Alloy; ошибки — GlitchTip 6.2 (sentry-sdk); uptime — Uptime Kuma + внешний heartbeat (healthchecks.io)
RATIONALE: Single-binary компоненты под Apache-2.0 (Grafana — AGPL без модификаций), приём стандартных протоколов (Loki push, OTLP, remote-write), простой retention флагом; логи и ошибки с данными расследований не покидают сервер. GlitchTip
(MIT) требует ~512 МБ против 16 ГБ + 16 ГБ swap у self-hosted Sentry. Внешний heartbeat закрывает слепую зону «сервер упал целиком».
ARCHITECTURE NOTES: Журнал действий агентов и версии моделей (требование воспроизводимости) хранить в PostgreSQL (append-only таблица, попадает в PITR-бэкап), а не в лог-системе с коротким retention. Retention логов 14–30 дней, метрик 90 дней.
COST: $0/мес (всё self-hosted, healthchecks.io Hobbyist 20 проверок). Опции: healthchecks.io Business $20/мес, Sentry Team $26/мес, Grafana Cloud Pro от $19/мес.
DATA QUALITY VERIFICATION: Ежемесячный «fire drill»: остановить контейнер и убедиться, что алерт дошёл в Telegram/e-mail за <N минут; остановить cron бэкапа — должен сработать heartbeat; канареечный секрет в логах должен появиться в VictoriaLogs только в
замаскированном виде; дашборд SLO по целям MVP (доля успешных получений >=99%, длительность расследований p50/p95, стоимость на расследование, число запросов к каждому источнику).
RISKS: Заявления VictoriaLogs о ресурсах — вендорские, не проверены; алерты для логов задаются файлами vmalert, а не через Grafana UI; у Alloy 1 273 открытых issue; мониторинг делит RAM с приложением.
REPLACEABILITY: Высокая: Alloy переключается на Loki/Prometheus/Grafana Cloud сменой endpoint; GlitchTip <-> Sentry/Bugsink сменой DSN.
REJECTED ALTERNATIVES:
  - Prometheus + Loki + Grafana: Рабочая альтернатива, но docs Loki относят Compose-установку к evaluation/dev, конфигурация сложнее, Loki под AGPL; Promtail EOL с 2026-03-02.
  - Grafana Cloud Free: Самый лёгкий вариант (10k series, 50 ГБ логов, 14 дней, 3 пользователя), но логи расследований уходят третьей стороне и retention 14 дней; оставлен как альтернатива, если владелец согласен и RAM в дефиците.
  - SigNoz: >=4 ГБ RAM (ClickHouse + Keeper + Postgres), compose-путь deprecated с v0.130.0.
  - OpenObserve: AGPL-3.0, последний тег — release candidate (v1.1.0-rc2).
  - Sentry self-hosted / SaaS: Self-hosted: 4 ядра/16 ГБ + 16 ГБ swap, лицензия FSL. SaaS Developer: 1 пользователь, 5k ошибок; Team $26/мес — разумный платный вариант позже.
  - Better Stack Free / UptimeRobot Free: Бесплатные тиры описаны как «for personal projects» и «hobby and non-profit projects» — для коммерческого продукта сомнительны.

### R8. NEED: Бэкапы
PRIMARY: pgBackRest >=2.59.3 (WAL-архив + PITR, шифрование) для PostgreSQL и restic 0.19.1 для файлов/томов -> Backblaze B2 (S3 API, Object Lock), у другого провайдера, чем сервер
RATIONALE: pgBackRest (MIT) даёт PITR, verify и блочные инкременты напрямую в S3; restic (BSD-2) — шифрованные дедуплицированные снапшоты отчётов, конфигов и томов. B2: $6.95/ТБ/мес, первые 10 ГБ бесплатно, Object Lock без доплаты — защита
от удаления бэкапов при взломе сервера. Провайдер бэкапов отличается от провайдера сервера.
ARCHITECTURE NOTES: Расписание: full еженедельно, diff ежедневно, WAL непрерывно; retention 2 full. Ключ приложения B2 — только запись/чтение в один бакет без права удаления версий. Встроенный ежедневный бэкап OVH VPS считать дополнительным, а не
основным.
COST: <=10 ГБ — $0; 50 ГБ ~ $0.28/мес; 200 ГБ ~ $1.3/мес (B2 $6.95/ТБ).
DATA QUALITY VERIFICATION: Еженедельный автоматический restore-тест: pgbackrest restore во временный контейнер + сравнение контрольных счётчиков строк и последней записи аудита; pgbackrest verify; restic check --read-data-subset; heartbeat в healthchecks.io
после каждого успешного бэкапа; раз в квартал — полное восстановление на новый VPS с замером RTO. Для репозиториев, созданных до 2.59.3, — проверка subkeys по инструкции из новости от 2026-10-04.
RISKS: Bus-factor pgBackRest (в апреле 2026 проект был объявлен неподдерживаемым, спасён коалицией спонсоров); потеря ключей шифрования репозиториев = потеря бэкапов (ключи хранить в SOPS и офлайн); Object Lock конфликтует с правом на
удаление данных (GDPR) — согласовать срок retention.
REPLACEABILITY: Средняя для pgBackRest (новый базовый бэкап при смене инструмента), высокая для хранилища (S3 API).
REJECTED ALTERNATIVES:
  - WAL-G 3.0.9: Жизнеспособная замена (Apache-2.0, один бинарь), если ситуация с сопровождением pgBackRest снова ухудшится; сейчас 329 открытых issues против 30.
  - Barman 3.20.1: GPL-3.0 и архитектура с отдельным backup-сервером — избыточно для одного узла.
  - Только pg_dump + restic раз в сутки: RPO 24 часа и нет PITR; допустимо лишь как временный вариант до настройки pgBackRest (уточнить у владельца требуемый RPO).
  - Hetzner Object Storage: Фиксированная плата ~€6.49/мес (сторонний источник) при объёме в единицы ГБ; HEL1 деградирует с 2026-09-09; не off-site, если сервер тоже в Hetzner.
  - Cloudflare R2: Рабочая альтернатива (10 ГБ бесплатно, egress 0), но $0.015/ГБ и платные операции при частых WAL-пушах.
  - borg: Ветка 2.0 всё ещё beta (2.0.0b25).

### R9. NEED: Секреты и редакция ключей в логах/отчётах
PRIMARY: SOPS 3.13 + age 1.3 (шифрованные файлы в git) -> Compose secrets (/run/secrets); редакция: structlog-процессор в приложении + Alloy loki.secretfilter + scrubber в sentry-sdk + gitleaks в CI
RATIONALE: Ноль дополнительных сервисов и $0; секреты версионируются вместе с кодом, расшифровываются только на сервере и в CI; MPL-2.0/BSD-3. Редакция многослойная: основная — в процессе (маскирование по именам полей и по точным значениям
загруженных секретов), вторая линия — на пути логов; документация Alloy сама предупреждает не полагаться только на secretfilter.
ARCHITECTURE NOTES: Правило: секреты читаются только из файлов, не из переменных окружения (env виден в docker inspect и crash-дампах). Seed-фразы и приватные ключи пользователей платформа не принимает вовсе — валидатор ввода должен отклонять и не
логировать такие строки.
COST: $0.
DATA QUALITY VERIFICATION: Канареечный тест в CI и на staging: в окружение подкладываются фейковые ключи формата каждого провайдера (TronGrid/Tronscan/LLM), прогоняется расследование с принудительными ошибками, затем grep по stdout контейнеров,
VictoriaLogs, событиям GlitchTip, report.json и PDF — ни одного вхождения. Gitleaks-скан репозитория и образов; проверка, что HTTP-клиент не логирует URL с ключом в query и заголовки Authorization.
RISKS: Компрометация сервера раскрывает age-ключ и все секреты (смягчение: отдельные ключи провайдеров с минимальными правами и лимитами расходов, регламент ротации); нет аудита чтения секретов; ложные срабатывания/пропуски regex-правил;
ключи формата UUID стандартными правилами Gitleaks могут не ловиться — нужны свои правила.
REPLACEABILITY: Высокая: значения переносятся в Infisical/OpenBao; приложение читает секреты из файлов /run/secrets и не зависит от источника.
REJECTED ALTERNATIVES:
  - Infisical: Бесплатный план без версионирования, ротации и audit log; Pro $20–23 за identity в месяц; self-host добавляет критичный сервис (+Postgres/Redis) на тот же сервер. Кандидат при росте команды.
  - OpenBao / HashiCorp Vault: Избыточная операционная нагрузка (unseal, политики, бэкап) для ~20 секретов; Vault под BUSL 1.1. OpenBao — целевой вариант на масштабе.
  - Doppler / 1Password: Все API-ключи у третьей стороны; у Doppler расхождение лимитов на собственной странице и 3-дневный activity log; цены 1Password не получены.
  - Только .env-файлы на сервере: Нет шифрования at rest, истории и контроля изменений; легко утекают в логи/бэкапы.
  - Только фильтр на сборщике логов: Редакция после того, как секрет уже покинул процесс (stdout, docker json-log на диске, отчёт).

## LIVE PROBE FINDINGS
- gh api repos/* для ~75 репозиториев (license, pushed_at, archived, stars, open_issues, последний релиз, число workflows, последний коммит); метаданные получены двумя независимыми прогонами и совпали. Замечание: releases?per_page=1
возвращает последний опубликованный, а не «latest» релиз (Prometheus v3.13.4 патч при актуальном v3.15.0; borg 2.0.0b25 при стабильном 1.4.5; Vault 2.2.0-rc1 при 2.1.2).
- wkhtmltopdf/wkhtmltopdf: archived=true, последний push 2022-11-22, релиз 0.12.6 от 2020-06-10.
- Прочитаны LICENSE-файлы там, где GitHub API отдал NOASSERTION: pdfmake — MIT; opentimestamps-client и python-opentimestamps — LGPL-3.0+; rfc3161ng — MIT; Dokploy — Apache-2.0 + /proprietary; SigNoz и Infisical — MIT + ee/; Sentry
и self-hosted — FSL-1.1-Apache-2.0; pgBackRest — MIT; WAL-G — Apache-2.0; borg — BSD-3; Vault — BUSL 1.1 (лицензиар IBM); Bugsink — PolyForm Shield 1.0.0; structlog — MIT OR Apache-2.0.
- UCO: скачан ontology/uco/observable/observable.ttl (380 207 байт), grep по «crypto» — 0 совпадений; issue ucoProject/UCO#675 «Cryptocurrency Address and Transaction Representation» открыт 2026-03-26, 5 комментариев.
- GitHub Security Advisories: coollabsio/coolify — 70 записей на первой странице (в т.ч. CVE-2026-57498 critical от 2026-06-28, CVE-2026-41896, CVE-2026-42204 high); Dokploy/dokploy — 60 записей (пачка critical от 2026-07-21:
CVE-2026-72864, -72737, -72877 и др.); basecamp/kamal — 0.
- OpenTimestamps: GET https://alice.btc.calendar.opentimestamps.org/, https://bob.btc.calendar.opentimestamps.org/, https://finney.calendar.eternitywall.com/ — HTTP 200, «OpenTimestamps Calendar Server (v0.7.1)», best-block height
971303, pending commitments 450/451/1 624, среднее время между транзакциями 1.68 ч (bob) и 5.79 ч (finney).
- PyPI JSON API: weasyprint 70.0 (2026-09-08, Python >=3.10, классификаторы до 3.14), playwright 1.63.0, reportlab 5.0.1 (2026-08-20), docxtpl 0.20.2 (2025-11-13, LGPL-2.1-only), typst 0.15.0 (wheel cp38-abi3-win_amd64), pyhanko
0.37.0, rfc3161-client 1.0.9, rfc3161ng 2.1.3 (2020-10-30), opentimestamps 0.4.5 (2023-01-25), pydantic 2.14.1, jsonschema 4.26.0, stix2 3.0.2, structlog 26.1.0, pypdf 6.20.1, rfc8785 0.1.4, case-utils 0.18.0.
- npm registry: pagedjs 0.4.3 (2023-07-06), pagedjs-cli 0.4.3 (2023-07-20), @react-pdf/renderer 4.9.0 (2026-08-27), pdfmake 0.3.11 (2026-06-12).
- Docker Hub API: gotenberg/gotenberg:8 обновлён 2026-09-11, размер amd64 ~703 МБ, arm64 ~696 МБ.
- Исходный код: gotenberg pkg/modules/chromium/routes.go — маршруты /forms/chromium/convert/{url,html,markdown}, поля header.html, footer.html, preferCssPageSize, generateTaggedPdf, generateDocumentOutline, waitDelay; модули api,
chromium, exiftool, libreoffice, pdfcpu, pdfengines, pdftk, prometheus, qpdf, webhook.
- Исходный код: getsops/sops cmd/sops/main.go содержит подкоманды exec-env и exec-file; age/keysource.go — SOPS_AGE_KEY, SOPS_AGE_KEY_FILE, SOPS_AGE_KEY_CMD.
- Исходный код docs Playwright (docs/src/api/class-page.md): опции Page.pdf, tagged и outline с v1.42; в header/footer-шаблонах скрипты не исполняются и стили страницы не видны.
- WeasyPrint: каталог weasyprint/pdf содержит pdfa.py, pdfua.py, pdfx.py, tags.py, sRGB2014.icc; issue #578 (open с 2018-02-22), #1104 (closed; комментарий мейнтейнера 2024-08-03 о разнице <20% между таблицами и div), PR #2808
(2026-06).
- GitLab API: glitchtip/glitchtip-backend — лицензия MIT, тег v6.2.6 от 2026-08-07, last_activity 2026-10-13, 359 stars.
- pgbackrest.org/news.html: 2026-04-27 «No longer maintained», 2026-05-18 «pgBackRest Will Continue!» (коалиция спонсоров), 2026-10-04 «Weak Encryption Subkeys and Salts» и релиз 2.59.3.
- status.hetzner.com (2026-10-14): открыты «Limited availability of cloud instances» с 2026-06-26, «Object Storage in location HEL1 partially degraded» с 2026-09-09, «Cloud IPv6 routing problems» с 2026-10-13.
- docs.hetzner.com price-adjustment (изменена 2026-07-08): с 2026-06-15 CX33 €6.49->€8.49, CPX32 €13.99->€35.49, CAX21 €7.99->€10.49, CCX13 €15.99->€42.99 (DE/FI, без НДС и IPv4).
- Поиск GitHub по трём запросам о шаблонах писем/запросов о заморозке криптоактивов — 0 репозиториев.
- typst/typst-assets/files/fonts: DejaVu Sans Mono, Libertinus Serif, New Computer Modern (+Math), Foxit-шрифты.

## CANDIDATES (full audit cards)

### [RECOMMENDED] WeasyPrint 70.0
NEED: PDF-рендеринг evidence-отчёта и писем
KIND: open-source
URL: https://github.com/Kozea/WeasyPrint
LICENSE: BSD-3-Clause
COMMERCIAL USE: Да, без условий кроме сохранения copyright notice; SaaS-использование не ограничено.
PROJECT STATE: v70.0 от 2026-09-08 (security-релиз), последний коммит 2026-10-13, 9 676 stars, 151 open issue, 13 CI workflows, каталог tests есть, не archived. PyPI: requires_python >=3.10, классификаторы 3.11–3.14 (3.13 поддержан).
CLAIMED VS ACTUAL: Документация сама признаёт: «Tables are slow, especially across multiple pages»; issue #578 «Performance issue on long documents» открыт с 2018. По PR #2808 (2026-06) таблица 1200 строк рендерится ~0.9–1.9 с (цифры автора PR, не
мои замеры). Валидность PDF/A «не гарантируется» (docs). Официального Docker-образа нет. На Windows нужен MSYS2 + Pango — на dev-машине Windows 11 проще рендерить в Linux-контейнере.
CAPABILITIES: HTML+CSS Paged Media (@page, counter(page)/counter(pages), running headers), длинные таблицы с переносом, ссылки (TXID -> explorer), PNG/SVG, PDF/A-1..4 (с v67.0, 2025-12-02) и PDF/UA, вложения в PDF (weasyprint.Attachment,
--attachment) — можно вложить JSON-отчёт и manifest в PDF/A-3. Кириллица через Pango при наличии шрифтов в образе.
INFRA: Python >=3.10, Pango >=1.44, шрифты с кириллицей (DejaVu/Noto/PT) в образе; ~200–500 МБ RAM на большой документ (оценка, не измерено).
PRICING/LIMITS: Бесплатно. Лимитов нет; CPU-bound, однопоточный рендер.
RISKS: Нет JS (граф нужно вставлять готовым PNG/SVG); собственный SVG-рендерер ограничен; производительность на 5–10 тыс. строк надо измерить; частые security-релизы (68.0, 69.0, 70.0) — обновлять обязательно.
REPLACEABILITY: Высокая: вход — HTML+CSS, тот же шаблон можно отдать Gotenberg/Chromium.
HOW VERIFIED: gh api repos/Kozea/WeasyPrint (метаданные, workflows, дерево), чтение docs (first_steps, changelog, common_use_cases), чтение issues #578, #1104, #2808 через gh api, PyPI JSON API. Код не запускался.
CONFIDENCE: high
EVIDENCE: https://github.com/Kozea/WeasyPrint | https://doc.courtbouillon.org/weasyprint/stable/first_steps.html | https://doc.courtbouillon.org/weasyprint/stable/changelog.html | https://doc.courtbouillon.org/weasyprint/stable/common_use_cases.html | https://github.com/Kozea/WeasyPrint/issues/578 | https://github.com/Kozea/WeasyPrint/pull/2808

### [ALTERNATIVE] Gotenberg 8.37.0 (Chromium + LibreOffice как HTTP-сервис)
NEED: PDF-рендеринг evidence-отчёта и писем
KIND: open-source
URL: https://github.com/gotenberg/gotenberg
LICENSE: MIT
COMMERCIAL USE: Да, без ограничений.
PROJECT STATE: v8.37.0 от 2026-09-11, коммит 2026-10-13, 13 274 stars, 32 open issues, 5 workflows, каталог test, не archived. Docker-образ gotenberg/gotenberg:8 обновлён 2026-09-11, ~703 МБ (amd64, сжатый).
CLAIMED VS ACTUAL: README: «Trusted in production by thousands of companies» — не проверяемо. Требований по RAM/конкурентности в документации не нашёл; PDF/A делается пост-конвертацией через LibreOffice/qpdf, а не Chromium.
CAPABILITIES: Маршруты /forms/chromium/convert/html|url|markdown, screenshot; поля header.html/footer.html, preferCssPageSize, generateTaggedPdf, generateDocumentOutline, waitDelay; модули libreoffice (DOCX->PDF), pdfcpu/qpdf/pdftk/exiftool
(merge, metadata, PDF/A, PDF/UA, encrypt), prometheus, webhook. Полный Chromium => JS-граф можно рендерить прямо в отчёте.
INFRA: Отдельный контейнер ~700 МБ образ, 1–2 ГБ RAM запаса.
PRICING/LIMITS: Бесплатно; ресурсы сервера (Chromium ~0.5–1 ГБ RAM на рендер — оценка).
RISKS: Тяжелее WeasyPrint; header/footer Chromium не видят стили страницы; SSRF-поверхность, если в HTML попадают внешние URL (нужен запрет сети).
REPLACEABILITY: Высокая — stateless HTTP API, тот же HTML.
HOW VERIFIED: gh api (метаданные, дерево pkg/modules), чтение pkg/modules/chromium/routes.go (grep полей), README, Docker Hub API, сайт gotenberg.dev.
CONFIDENCE: high
EVIDENCE: https://github.com/gotenberg/gotenberg | https://raw.githubusercontent.com/gotenberg/gotenberg/main/pkg/modules/chromium/routes.go | https://gotenberg.dev/docs/getting-started/introduction | https://hub.docker.com/r/gotenberg/gotenberg

### [ALTERNATIVE] Playwright 1.64 / Chromium print-to-PDF (page.pdf)
NEED: PDF-рендеринг evidence-отчёта и писем
KIND: open-source
URL: https://github.com/microsoft/playwright
LICENSE: Apache-2.0
COMMERCIAL USE: Да.
PROJECT STATE: playwright v1.64.0 (2026-10-07), playwright-python v1.63.0 (2026-09-15), 97 640 stars, активные коммиты 2026-10-13; PyPI wheels win_amd64/manylinux, Python 3.11–3.14.
CLAIMED VS ACTUAL: Ограничения из исходника docs: в header/footer-шаблонах «Script tags … are not evaluated» и «Page styles are not visible»; PDF/A и вложений нет — нужен пост-процессинг (pypdf/pyHanko). none found сверх этого.
CAPABILITIES: page.pdf: format, margin, displayHeaderFooter, headerTemplate/footerTemplate (классы pageNumber, totalPages, date, title, url), preferCSSPageSize, tagged и outline (с v1.42). Рендерит ту же web-версию отчёта, включая JS-граф.
INFRA: Chromium в образе (~300+ МБ), ~0.5–1 ГБ RAM на рендер.
PRICING/LIMITS: Бесплатно.
RISKS: Тяжёлая зависимость в основном приложении; обновления Chromium; для сервиса проще взять Gotenberg, который оборачивает тот же движок.
REPLACEABILITY: Высокая (тот же HTML).
HOW VERIFIED: gh api, чтение docs/src/api/class-page.md из репозитория (раздел Page.pdf), PyPI JSON.
CONFIDENCE: high
EVIDENCE: https://github.com/microsoft/playwright | https://raw.githubusercontent.com/microsoft/playwright/main/docs/src/api/class-page.md | https://pypi.org/project/playwright/

### [NEEDS-TRIAL] Typst 0.15.1 (+ typst-py 0.15.0)
NEED: PDF-рендеринг evidence-отчёта и писем
KIND: open-source
URL: https://github.com/typst/typst
LICENSE: Apache-2.0
COMMERCIAL USE: Да (компилятор Apache-2.0; web-приложение typst.app — отдельный коммерческий сервис, не нужен).
PROJECT STATE: v0.15.1 (2026-07-17), коммиты 2026-10, 56 601 stars, 1 308 open issues, 5 workflows. Python-биндинг messense/typst-py v0.15.0 (2026-06-16), Apache-2.0, wheels abi3 win_amd64 и manylinux.
CLAIMED VS ACTUAL: Версия всё ещё 0.x — между минорными версиями бывают ломающие изменения синтаксиса; PDF/UA-2 не поддержан. Покрытие кириллицы встроенными шрифтами не проверял рендером.
CAPABILITIES: Очень быстрая компиляция; table.header/table.footer с repeat=true, colspan/rowspan; --pdf-standard a-1b…a-4e, ua-1; pdf.attach (нужен PDF/A-3 или A-4f); встроенные шрифты Libertinus Serif, New Computer Modern, DejaVu Sans Mono (в
typst-assets).
INFRA: Один бинарь/wheel, без системных зависимостей.
PRICING/LIMITS: Бесплатно.
RISKS: Отдельный язык разметки: web-отчёт (HTML) и PDF придётся верстать дважды; экранирование пользовательских данных в .typ; pre-1.0.
REPLACEABILITY: Средняя: шаблоны не переносимы в HTML-движки.
HOW VERIFIED: gh api (typst/typst, messense/typst-py, typst/typst-assets/files/fonts), docs typst.app (reference/pdf, reference/model/table), PyPI JSON.
CONFIDENCE: medium
EVIDENCE: https://github.com/typst/typst | https://typst.app/docs/reference/pdf/ | https://typst.app/docs/reference/model/table/ | https://github.com/messense/typst-py | https://github.com/typst/typst-assets

### [REJECTED] ReportLab 5.0.1 (open-source PDF Toolkit)
NEED: PDF-рендеринг evidence-отчёта и писем
KIND: open-source
URL: https://pypi.org/project/reportlab/
LICENSE: BSD (open-source toolkit); ReportLab PLUS (RML, PageCatcher) — коммерческая лицензия
COMMERCIAL USE: Toolkit — да. RML/PageCatcher — только в платном ReportLab PLUS (цена на сайте не показана).
PROJECT STATE: PyPI 5.0.1 от 2026-08-20, requires_python >=3.9,<4, классификаторы до 3.14. Основной репозиторий не на GitHub — CI/тесты не проверял.
CLAIMED VS ACTUAL: Удобный шаблонный язык RML есть только в коммерческой версии; pyRXP (парсер RML) под GPL.
CAPABILITIES: Императивная генерация (Platypus: LongTable, PageTemplate, номера страниц), TTF-шрифты с кириллицей через registerFont.
PRICING/LIMITS: Toolkit бесплатен.
RISKS: Вёрстка кодом, а не шаблоном: дублирует web-версию отчёта, дороже в поддержке письма на нескольких языках.
REPLACEABILITY: Низкая (вёрстка в коде).
HOW VERIFIED: PyPI JSON API, docs.reportlab.com (docs only).
CONFIDENCE: medium
EVIDENCE: https://pypi.org/project/reportlab/ | https://docs.reportlab.com/

### [REJECTED] wkhtmltopdf 0.12.6
NEED: PDF-рендеринг evidence-отчёта и писем
KIND: open-source
URL: https://github.com/wkhtmltopdf/wkhtmltopdf
LICENSE: LGPL-3.0
COMMERCIAL USE: Формально да, но проект мёртв.
PROJECT STATE: Репозиторий archived=true, последний push 2022-11-22, последний релиз 0.12.6 от 2020-06-10, 1 352 open issues. Обёртка python-pdfkit: последний коммит 2023-09-14.
CLAIMED VS ACTUAL: Страница статуса проекта сама предупреждает: «Do not use wkhtmltopdf with any untrusted HTML» и рекомендует WeasyPrint/Prince/Puppeteer; движок — QtWebKit образца 2012 года.
PRICING/LIMITS: Бесплатно.
RISKS: Нет патчей безопасности, устаревший CSS, не подходит для отчётов с данными из внешних источников.
HOW VERIFIED: gh api repos/wkhtmltopdf/wkhtmltopdf, https://wkhtmltopdf.org/status.html, PyPI pdfkit.
CONFIDENCE: high
EVIDENCE: https://github.com/wkhtmltopdf/wkhtmltopdf | https://wkhtmltopdf.org/status.html

### [REJECTED] react-pdf (@react-pdf/renderer 4.9.0)
NEED: PDF-рендеринг evidence-отчёта и писем
KIND: open-source
URL: https://github.com/diegomura/react-pdf
LICENSE: MIT
COMMERCIAL USE: Да.
PROJECT STATE: npm 4.9.0 от 2026-08-27, последний коммит 2026-09-22, 16 833 stars, 341 open issues, 5 workflows.
CLAIMED VS ACTUAL: none found (глубоко не проверял: кириллица требует регистрации своего шрифта — по памяти, не перепроверено).
PRICING/LIMITS: Бесплатно.
RISKS: Только Node/React, собственная модель вёрстки (не HTML/CSS) — отдельный шаблон от web-отчёта и ещё один рантайм в Python-бэкенде; нет PDF/A и вложений.
HOW VERIFIED: gh api, npm registry API.
CONFIDENCE: medium
EVIDENCE: https://github.com/diegomura/react-pdf | https://registry.npmjs.org/@react-pdf%2frenderer

### [REJECTED] pdfmake 0.3.11
NEED: PDF-рендеринг evidence-отчёта и писем
KIND: open-source
URL: https://github.com/bpampuch/pdfmake
LICENSE: MIT (текст LICENSE прочитан; GitHub API показывает NOASSERTION)
COMMERCIAL USE: Да.
PROJECT STATE: 0.3.11 от 2026-06-12 (после него коммитов нет ~4 мес.), 12 351 stars, 239 open issues.
CLAIMED VS ACTUAL: none found
PRICING/LIMITS: Бесплатно.
RISKS: JSON-описание документа в JS, не HTML; нет PDF/A; второй рантайм; дублирование шаблонов.
HOW VERIFIED: gh api + чтение LICENSE, npm registry.
CONFIDENCE: medium
EVIDENCE: https://github.com/bpampuch/pdfmake | https://registry.npmjs.org/pdfmake

### [REJECTED] Paged.js 0.4.3
NEED: PDF-рендеринг evidence-отчёта и писем
KIND: open-source
URL: https://github.com/pagedjs/pagedjs
LICENSE: MIT
COMMERCIAL USE: Да.
PROJECT STATE: npm latest 0.4.3 от 2023-07-06 (pagedjs-cli 0.4.3 от 2023-07-20) — релизов нет более 3 лет, хотя в репозитории есть коммиты (последний 2026-10-06); 1 531 stars, 236 open issues, 1 workflow.
CLAIMED VS ACTUAL: Позиционируется как polyfill CSS Paged Media, но всё равно требует headless Chromium для получения PDF; релизный цикл фактически остановлен.
PRICING/LIMITS: Бесплатно.
RISKS: Polyfill-пагинация в браузере медленная на длинных таблицах (не измерял); не решает ничего, чего не дают WeasyPrint или Chromium @page.
HOW VERIFIED: gh api (commits, tags), npm registry.
CONFIDENCE: medium
EVIDENCE: https://github.com/pagedjs/pagedjs | https://registry.npmjs.org/pagedjs

### [REJECTED] LaTeX (TeX Live / Tectonic)
NEED: PDF-рендеринг evidence-отчёта и писем
KIND: open-source
URL: https://github.com/tectonic-typesetting/tectonic
LICENSE: LaTeX — LPPL и др.; Tectonic — LICENSE в репозитории, GitHub API отдаёт «Other» (текст не читал)
COMMERCIAL USE: Да (по общеизвестным условиям; текст лицензии Tectonic не перечитывал).
PROJECT STATE: Tectonic: 5 167 stars, последний коммит 2026-07-31, релиз «continuous» 2026-07-31, 172 open issues, 7 workflows.
CLAIMED VS ACTUAL: none found
PRICING/LIMITS: Бесплатно; TeX Live full — гигабайты.
RISKS: Отдельный язык шаблонов, сложное экранирование пользовательских данных, кириллица/шрифты требуют настройки, медленная компиляция, высокая планка для маленькой команды.
HOW VERIFIED: gh api (метаданные). Возможности LaTeX — из общих знаний, не перепроверялись.
CONFIDENCE: low
EVIDENCE: https://github.com/tectonic-typesetting/tectonic

### [ALTERNATIVE] docxtpl 0.20.2 (python-docx-template) + LibreOffice-конвертация
NEED: Шаблоны писем биржам / Tether / правоохранительным органам (редактируемые документы)
KIND: open-source
URL: https://github.com/elapouya/python-docx-template
LICENSE: LGPL-2.1-only (docxtpl); LibreOffice — MPL-2.0
COMMERCIAL USE: Да: использование как библиотеки в SaaS без распространения не накладывает copyleft-обязательств на свой код.
PROJECT STATE: PyPI 0.20.2 от 2025-11-13 (релизу ~11 мес.), последний коммит в репозитории 2026-07-07, 2 722 stars, 176 open issues, 4 workflows, tests есть. GitHub Releases не ведутся.
CLAIMED VS ACTUAL: none found
CAPABILITIES: Jinja2-теги внутри .docx — юрист правит шаблон в Word; PDF получается через LibreOffice (например маршрут Gotenberg libreoffice).
INFRA: LibreOffice headless (в составе Gotenberg) для DOCX->PDF.
PRICING/LIMITS: Бесплатно.
RISKS: Вёрстка длинных таблиц TXID в DOCX хрупкая; редкие релизы; итоговый PDF зависит от шрифтов LibreOffice.
REPLACEABILITY: Высокая для писем (шаблон = файл .docx).
HOW VERIFIED: gh api, PyPI JSON.
CONFIDENCE: medium
EVIDENCE: https://github.com/elapouya/python-docx-template | https://pypi.org/project/docxtpl/

### [RECOMMENDED] Pydantic 2.14.1
NEED: JSON-отчёт: схема и версионирование
KIND: open-source
URL: https://github.com/pydantic/pydantic
LICENSE: MIT
COMMERCIAL USE: Да.
PROJECT STATE: v2.14.1 от 2026-10-11, коммиты 2026-10-13, 29 014 stars, requires_python >=3.10, классификаторы до 3.15.
CLAIMED VS ACTUAL: none found
CAPABILITIES: Типизированные модели отчёта (Fact с обязательным txid, Label с source/checked_at/confidence), строгая валидация, генерация JSON Schema, дискриминируемые union для версий схемы.
PRICING/LIMITS: Бесплатно.
RISKS: Схема привязана к Python-моделям; для внешних потребителей нужно публиковать сгенерированный JSON Schema как артефакт релиза.
REPLACEABILITY: Высокая: наружу отдаётся стандартный JSON Schema.
HOW VERIFIED: gh api, PyPI JSON.
CONFIDENCE: high
EVIDENCE: https://github.com/pydantic/pydantic | https://pypi.org/project/pydantic/

### [RECOMMENDED] JSON Schema 2020-12 + python-jsonschema 4.26.0
NEED: JSON-отчёт: схема и версионирование
KIND: standard
URL: https://json-schema.org/specification
LICENSE: jsonschema (библиотека) — MIT
COMMERCIAL USE: Да.
PROJECT STATE: Спецификация: текущая версия 2020-12 (сайт: «The current version is 2020-12»), преемник не опубликован. Библиотека 4.26.0 от 2026-01-07, коммиты 2026-10-12, 4 989 stars, 55 open issues.
CLAIMED VS ACTUAL: none found
CAPABILITIES: Независимая от языка проверка отчёта потребителем (биржа, юрист, другой инструмент); CI-валидация golden-отчётов.
PRICING/LIMITS: Бесплатно.
RISKS: Не описывает семантику расследования — только структуру; версионирование (SemVer поля schema_version) — на своей стороне.
REPLACEABILITY: Высокая.
HOW VERIFIED: json-schema.org (docs), gh api, PyPI JSON.
CONFIDENCE: high
EVIDENCE: https://json-schema.org/specification | https://github.com/python-jsonschema/jsonschema

### [ALTERNATIVE] STIX 2.1 (OASIS) + stix2 3.0.2
NEED: JSON-отчёт: стандарты обмена доказательствами
KIND: standard
URL: https://docs.oasis-open.org/cti/stix/v2.1/os/stix-v2.1-os.html
LICENSE: Спецификация — OASIS IPR Non-Assertion Mode; библиотека stix2 — BSD-3-Clause
COMMERCIAL USE: Да.
PROJECT STATE: STIX 2.1 — OASIS Standard от 2021-06-10. cti-python-stix2 v3.0.2 от 2026-02-12 (последний коммит тогда же), 439 stars, 68 open issues, Python 3.10–3.14.
CLAIMED VS ACTUAL: В списке SCO (раздел 6) нет объектов для криптовалютных адресов и блокчейн-транзакций — их придётся описывать собственным Extension Definition, то есть совместимость с получателями будет только номинальной.
CAPABILITIES: Граф объектов и связей, identity/report/note/observed-data, расширения через Extension Definition.
PRICING/LIMITS: Бесплатно.
RISKS: Ни биржи, ни Tether не принимают STIX в LE-каналах (подтверждений обратного не нашёл); лишняя сложность для MVP.
REPLACEABILITY: Экспорт-адаптер поверх своей схемы — легко добавить позже.
HOW VERIFIED: Чтение спецификации на docs.oasis-open.org (первые 100k символов, оглавление SCO), gh api, PyPI JSON, веб-поиск расширений (не найдено опубликованного крипто-SCO).
CONFIDENCE: medium
EVIDENCE: https://docs.oasis-open.org/cti/stix/v2.1/os/stix-v2.1-os.html | https://github.com/oasis-open/cti-python-stix2 | https://pypi.org/project/stix2/

### [REJECTED] CASE 1.5.0 / UCO 1.5.0 (Cyber-investigation Analysis Standard Expression)
NEED: JSON-отчёт: стандарты обмена доказательствами
KIND: standard
URL: https://github.com/casework/CASE
LICENSE: Apache-2.0
COMMERCIAL USE: Да.
PROJECT STATE: CASE 1.5.0 (2026-07-24), UCO 1.5.0 (2026-07-24); репозитории активны (CASE push 2026-09-23, UCO 2026-07-27), 80 и 123 stars; case-utils 0.18.0 (2026-09-02).
CLAIMED VS ACTUAL: В ontology/uco/observable/observable.ttl (380 КБ) нет ни одного вхождения «crypto»; issue UCO #675 «Cryptocurrency Address and Transaction Representation» открыт с 2026-03-26 и прямо говорит: «CASE/UCO has no dedicated classes to
represent this data». То есть крипто-расследование стандартно выразить пока нельзя.
CAPABILITIES: JSON-LD/RDF онтология цифровой криминалистики: provenance, действия инструментов, chain of custody — концептуально ближе всего к evidence-отчёту.
PRICING/LIMITS: Бесплатно.
RISKS: RDF/SHACL-стек тяжёл для маленькой команды; малая экосистема; модель адресов/транзакций ещё не принята.
REPLACEABILITY: Экспорт-адаптер позже, когда #675 будет принят.
HOW VERIFIED: gh api, скачан и прочитан grep-ом observable.ttl, прочитан issue #675, список репозиториев организации casework.
CONFIDENCE: high
EVIDENCE: https://github.com/casework/CASE | https://github.com/ucoProject/UCO | https://github.com/ucoProject/UCO/issues/675 | https://raw.githubusercontent.com/ucoProject/UCO/master/ontology/uco/observable/observable.ttl

### [REJECTED] IVMS101 (interVASP Messaging Standard, версия IVMS 101.2023)
NEED: JSON-отчёт: стандарты обмена доказательствами
KIND: standard
URL: https://www.intervasp.org/
LICENSE: Лицензия/условия использования на сайте не указаны
COMMERCIAL USE: Не подтверждено (условий на сайте нет).
PROJECT STATE: Текущая версия IVMS 101.2023; обновление выпущено 2024-06-04; исходный релиз 2020.
CLAIMED VS ACTUAL: Стандарт описывает только данные отправителя/получателя между VASP (Travel Rule); про запросы правоохранительных органов и обмен доказательствами на сайте ничего нет — к задаче не относится.
PRICING/LIMITS: PDF бесплатно.
RISKS: Нерелевантен: платформа не VASP и не передаёт KYC-данные.
HOW VERIFIED: Чтение intervasp.org (docs only).
CONFIDENCE: medium
EVIDENCE: https://www.intervasp.org/

### [RECOMMENDED] Hash-manifest (SHA-256) + каноничный JSON RFC 8785 (rfc8785 0.1.4) + подпись Ed25519
NEED: Целостность доказательств (integrity seal)
KIND: standard
URL: https://github.com/trailofbits/rfc8785.py
LICENSE: rfc8785.py — Apache-2.0; hashlib — stdlib
COMMERCIAL USE: Да.
PROJECT STATE: rfc8785 0.1.4 от 2024-09-27 (релиз старый, но репозиторий жив: коммит 2026-09-28, 8 workflows), 13 stars — маленькая библиотека Trail of Bits. Альтернатива подписи файлов: minisign (ISC, коммит 2026-10-11).
CLAIMED VS ACTUAL: none found
CAPABILITIES: manifest.json: sha256 каждого артефакта (report.json, report.pdf, graph.png, сырые ответы API), версии моделей/параметры; хеш каноничной формы manifest печатается в колонтитуле PDF и на странице печати.
PRICING/LIMITS: Бесплатно.
RISKS: Хеш без внешней метки времени доказывает только неизменность, но не момент создания — поэтому дополняется RFC 3161/OpenTimestamps. Нужно управление подписывающим ключом (SOPS/age).
REPLACEABILITY: Высокая; JCS реализуем в ~100 строк при необходимости.
HOW VERIFIED: gh api, PyPI JSON. Стандарт RFC 8785 не перечитывался.
CONFIDENCE: medium
EVIDENCE: https://github.com/trailofbits/rfc8785.py | https://pypi.org/project/rfc8785/ | https://github.com/jedisct1/minisign

### [RECOMMENDED] RFC 3161 timestamp: rfc3161-client 1.0.9 + TSA (FreeTSA / Sectigo / квалифицированный TSA)
NEED: Целостность доказательств (integrity seal)
KIND: standard
URL: https://github.com/trailofbits/rfc3161-client
LICENSE: rfc3161-client — Apache-2.0
COMMERCIAL USE: Библиотека — да. FreeTSA: явных условий использования нет, для компаний предлагают связаться с оператором. Sectigo: публичный endpoint, просят >=15 с между запросами (search snippet). Квалифицированные eIDAS-метки — платные.
PROJECT STATE: rfc3161-client v1.0.9 от 2026-09-14, коммит 2026-10-12, 7 workflows, wheels manylinux/musllinux/macOS; мало звёзд (7), но автор — Trail of Bits. Старый rfc3161ng 2.1.3 — релиз 2020-10-30, заброшен.
CLAIMED VS ACTUAL: README: библиотека «does not perform any network activity» — транспорт на нашей стороне. FreeTSA ведёт частное лицо, SLA и ToS нет, старый сертификат истёк в 03.2026 — для юридически значимых отчётов это слабое звено.
CAPABILITIES: Построение TimeStampReq, разбор и верификация TimeStampResp (VerifierBuilder); сетевой вызов делается своим HTTP-клиентом. FreeTSA: endpoint https://freetsa.org/tsr, SHA-256/384/512, сертификат обновлён 2026-03-16 (действует до
02.2040, ECC P-384).
PRICING/LIMITS: FreeTSA — 0. Квалифицированные метки: Lleida.net «from €0,03», SK ID ~0.006–0.036 за метку (search snippet, валюты/условия не подтверждены). 1 метка на отчёт => <=€0.04 на расследование.
RISKS: Доверие к метке = доверие к TSA; нужен fallback-список TSA и хранение цепочки сертификатов вместе с токеном; rate-limit у бесплатных TSA.
REPLACEABILITY: Высокая: протокол стандартный, TSA меняется конфигом.
HOW VERIFIED: gh api, чтение README rfc3161-client, PyPI JSON, чтение freetsa.org; Sectigo и цены QTSP — только поисковые сниппеты. Запросы к TSA не отправлялись (POST запрещён правилами аудита).
CONFIDENCE: medium
EVIDENCE: https://github.com/trailofbits/rfc3161-client | https://pypi.org/project/rfc3161-client/ | https://freetsa.org/index_en.php | https://sectigo.com/resource-library/time-stamping-server | https://www.lleida.net/en/esignature-and-econtracting/timestamp

### [ALTERNATIVE] OpenTimestamps (opentimestamps-client 0.7.2)
NEED: Целостность доказательств (integrity seal)
KIND: open-source
URL: https://github.com/opentimestamps/opentimestamps-client
LICENSE: LGPL-3.0-or-later (текст LICENSE прочитан)
COMMERCIAL USE: Да при использовании как библиотеки/CLI без модификации; публичные календари — бесплатный сервис на донатах без SLA.
PROJECT STATE: Клиент 0.7.2 от 2024-12-31, последний коммит 2026-02-07 (правки примеров), 425 stars, 49 open issues; python-opentimestamps на PyPI 0.4.5 от 2023-01-25. Развитие медленное, но календари живы.
CLAIMED VS ACTUAL: Подтверждение не мгновенное: по живым страницам календарей среднее время между транзакциями 1.68 ч (bob) и 5.79 ч (finney) — итоговый proof появляется через часы, отчёт надо «апгрейдить» позже. Кошельки календарей держат 46–601
тыс. сат — сервис существует на донатах.
CAPABILITIES: Привязка хеша manifest к блокчейну Bitcoin без доверенной третьей стороны; proof (.ots) кладётся рядом с отчётом.
PRICING/LIMITS: 0.
RISKS: Нет SLA; не является «квалифицированной» меткой в юридическом смысле; малоизвестен юристам/следователям.
REPLACEABILITY: Дополняющий слой, отключается без потерь.
HOW VERIFIED: gh api, чтение LICENSE, PyPI JSON, живые GET к alice.btc/bob.btc.calendar.opentimestamps.org и finney.calendar.eternitywall.com (HTTP 200, Calendar Server v0.7.1, best-block height 971303).
CONFIDENCE: high
EVIDENCE: https://github.com/opentimestamps/opentimestamps-client | https://alice.btc.calendar.opentimestamps.org/ | https://bob.btc.calendar.opentimestamps.org/ | https://finney.calendar.eternitywall.com/

### [NEEDS-TRIAL] pyHanko 0.37.0 (подпись PDF, PAdES, document timestamp)
NEED: Целостность доказательств (integrity seal)
KIND: open-source
URL: https://github.com/MatthiasValvekens/pyHanko
LICENSE: MIT
COMMERCIAL USE: Да.
PROJECT STATE: pyhanko 0.37.0 от 2026-08-31, коммит 2026-10-11, 784 stars, 5 open issues, 7 workflows, Python >=3.10.
CLAIMED VS ACTUAL: README автора: «This project is currently in beta, and not yet production-ready» — при том что библиотека широко используется. Для подписи нужен X.509-сертификат организации (отдельная покупка/процедура).
CAPABILITIES: PAdES B-B/B-T/B-LT/B-LTA, RFC 3161 timestamp внутри PDF, валидация подписи, QR-штампы.
PRICING/LIMITS: Бесплатно; сертификат подписи — отдельно.
RISKS: Фактически один мейнтейнер; без сертификата даёт только document timestamp.
REPLACEABILITY: Высокая (стандарт PAdES).
HOW VERIFIED: gh api, чтение README, PyPI JSON.
CONFIDENCE: high
EVIDENCE: https://github.com/MatthiasValvekens/pyHanko | https://pypi.org/project/pyhanko/

### [NEEDS-TRIAL] Каналы и форматы запросов: Binance LERS/Kodex, OKX LE Guide, Tether / T3 FCU
NEED: Шаблоны писем биржам / Tether / правоохранительным органам
KIND: standard
URL: https://www.kodexglobal.com/
LICENSE: n/a (проприетарные порталы и регламенты)
COMMERCIAL USE: Порталы предназначены для верифицированных государственных органов; частная платформа может только готовить пакет документов для жертвы/юриста/следователя.
PROJECT STATE: Kodex: «trusted by 15K+ government agencies», клиенты по сайту — Coinbase, Bitfinex, Bitget; Binance использует собственную LERS с проверкой через Kodex (поисковые сниппеты: одобрение доступа ~3 рабочих дня, запрос без официальных
документов не обрабатывается). OKX: запросы на enforcement@okx.com от уполномоченных сотрудников (сниппет). Tether: официальной публичной процедуры не найдено; по вторичным источникам действует по запросам LE; T3 FCU
(TRON+Tether+TRM Labs) — тоже LE-канал.
CLAIMED VS ACTUAL: Единого машинного стандарта запроса (схемы/API) для бирж не существует; ни один канал не принимает обращения от частных лиц как основание для заморозки. Обещать пользователю «запрос на заморозку» напрямую в Tether нельзя — только
проект письма для передачи через полицию.
PRICING/LIMITS: n/a
RISKS: Регламенты меняются без уведомления; первичные страницы Binance и OKX не удалось открыть (ECONNRESET), у Tether страница /legal вернула 404 — содержание полей запроса подтверждено только сниппетами.
REPLACEABILITY: Шаблоны — свои Jinja2-файлы с реестром получателей (канал, требуемые поля, дата проверки).
HOW VERIFIED: Чтение kodexglobal.com; Binance/OKX/Tether/T3 — только поисковые сниппеты и вторичные источники; поиск по GitHub готовых шаблонов писем (0 результатов по трём запросам).
CONFIDENCE: low
EVIDENCE: https://www.kodexglobal.com/ | https://www.binance.com/en/support/law-enforcement | https://www.okx.com/help/okx-law-enforcement-request-guide | https://www.trmlabs.com/resources/blog/t3-financial-crime-unit-a-model-for-public-private-disruption-in-the-age-of-stablecoins | https://blocksec.com/blog/1-26-billion-frozen-usdt-blacklisting-on-ethereum-and-tron-in-2025

### [RECOMMENDED] Docker Compose v5.6.0 на одном VPS + Caddy 2.11.7 + GitHub Actions
NEED: Деплой и CI/CD
KIND: open-source
URL: https://github.com/docker/compose
LICENSE: Apache-2.0 (Compose, Caddy)
COMMERCIAL USE: Да. GitHub Actions: 2 000 мин/мес бесплатно для приватных репозиториев на плане Free, публичные — бесплатно на стандартных runner.
PROJECT STATE: Compose v5.6.0 от 2026-10-02, 38 381 stars, 107 open issues, 15 workflows. Caddy v2.11.7 от 2026-10-03, 77 917 stars.
CLAIMED VS ACTUAL: Docs: Compose secrets работают только для Linux-контейнеров и не шифруются Compose-ом (это механизм доставки, шифрование at rest — задача SOPS). Нет zero-downtime из коробки (секунды простоя при пересоздании контейнера).
CAPABILITIES: Один compose.yaml для dev (Windows 11 + Docker) и prod; secrets как файлы в /run/secrets; healthcheck/restart; авто-TLS через Caddy; деплой: Actions собирает образы -> GHCR -> ssh на сервер -> docker compose pull && up -d --wait.
INFRA: Docker Engine на VPS, SSH-ключ деплоя.
PRICING/LIMITS: 0. Actions сверх лимита: Linux 2-core $0.006/мин; self-hosted runner бесплатен.
RISKS: Нет автоскейлинга и мульти-хоста; rollback вручную (тег предыдущего образа).
REPLACEABILITY: Высокая: те же образы запускаются Kamal или k3s.
HOW VERIFIED: gh api (compose, caddy), docs.docker.com (use-secrets), docs.github.com (billing: минуты и цены).
CONFIDENCE: high
EVIDENCE: https://github.com/docker/compose | https://docs.docker.com/compose/how-tos/use-secrets/ | https://docs.github.com/en/billing/concepts/product-billing/github-actions | https://docs.github.com/en/billing/reference/actions-runner-pricing | https://github.com/caddyserver/caddy

### [ALTERNATIVE] Kamal 2.12.0
NEED: Деплой и CI/CD
KIND: open-source
URL: https://github.com/basecamp/kamal
LICENSE: MIT
COMMERCIAL USE: Да.
PROJECT STATE: v2.12.0 от 2026-06-18, коммит 2026-10-13, 14 645 stars, 159 open issues, 6 workflows; опубликованных security advisories — 0.
CLAIMED VS ACTUAL: Нужен Ruby (или запуск в Docker «с ограничениями»); про Windows в установке ничего нет, issue #1350 «Fix secrets adapters failing fetch on Windows» открыт с 2025-01-10 — с Windows 11 реально работать только через WSL/CI. Адаптера
SOPS среди встроенных нет.
CAPABILITIES: Zero-downtime деплой через kamal-proxy (80/443), установка Docker на сервер, accessories (БД и пр.), адаптеры секретов: 1Password, LastPass, Bitwarden, Bitwarden SM, AWS Secrets Manager, Doppler, GCP, Passbolt.
PRICING/LIMITS: 0; нужен container registry.
RISKS: Ещё один инструмент и Ruby-зависимость ради одного сервера; accessories (Postgres) управляются отдельно от приложения.
REPLACEABILITY: Высокая (обычные Docker-образы).
HOW VERIFIED: gh api (метаданные, security-advisories, поиск issues), kamal-deploy.org docs (installation, secrets).
CONFIDENCE: high
EVIDENCE: https://github.com/basecamp/kamal | https://kamal-deploy.org/docs/installation/ | https://kamal-deploy.org/docs/commands/secrets/ | https://github.com/basecamp/kamal/issues/1350

### [REJECTED] Coolify 4.4.6
NEED: Деплой и CI/CD
KIND: open-source
URL: https://github.com/coollabsio/coolify
LICENSE: Apache-2.0
COMMERCIAL USE: Да (self-hosted бесплатно; Coolify Cloud $5/мес за 2 сервера, +$3 за каждый следующий).
PROJECT STATE: v4.4.6 от 2026-10-09, 62 948 stars, 718 open issues, 23 workflows, очень активен.
CLAIMED VS ACTUAL: Маркетинг — «self-hosted Heroku», но в GitHub Security Advisories >=70 записей; только за 2026-06-25…07-02 опубликованы critical/high: cross-team IDOR (CVE-2026-57498, critical), неаутентифицированный запуск деплоя через webhook
(CVE-2026-41896), несколько RCE до root на управляемых серверах (CVE-2026-42204, -42143, -34594, -34599).
PRICING/LIMITS: Self-hosted 0.
RISKS: Панель с root-доступом к серверу, где лежат API-ключи и материалы расследований, — непропорциональная поверхность атаки для одного сервера; PHP-стек + своя БД съедают RAM.
REPLACEABILITY: Средняя (конфигурация живёт в БД панели).
HOW VERIFIED: gh api repos/coollabsio/coolify и /security-advisories (первая страница, 70 записей), coolify.io/pricing, новостной поиск.
CONFIDENCE: high
EVIDENCE: https://github.com/coollabsio/coolify | https://github.com/coollabsio/coolify/security/advisories | https://coolify.io/pricing | https://thehackernews.com/2026/01/coolify-discloses-11-critical-flaws.html

### [REJECTED] Dokploy 0.30.8
NEED: Деплой и CI/CD
KIND: open-source
URL: https://github.com/Dokploy/dokploy
LICENSE: Apache-2.0 для основного кода + отдельная LICENSE_PROPRIETARY для каталогов /proprietary (GitHub API: NOASSERTION); в корне также TERMS_AND_CONDITIONS.md (не читал)
COMMERCIAL USE: Да для Apache-части; условия proprietary-части и TERMS_AND_CONDITIONS не проверены.
PROJECT STATE: v0.30.8 от 2026-09-29, 37 779 stars, 775 open issues, 16 workflows, ветка по умолчанию canary.
CLAIMED VS ACTUAL: В Security Advisories 60 записей на первой странице; 2026-07-21 опубликована пачка critical: member -> root через docker-terminal WebSocket (CVE-2026-72864), cross-organization IDOR с утечкой S3-учёток бэкапов (CVE-2026-72737),
command injection в деплое (CVE-2026-72877, -72867) и др.
PRICING/LIMITS: Self-hosted 0.
RISKS: Те же, что у Coolify: панель с root на проде; молодая кодовая база (создан 2024-04), смешанная лицензия.
REPLACEABILITY: Средняя.
HOW VERIFIED: gh api (метаданные, LICENSE.MD прочитан целиком, список корня, /security-advisories).
CONFIDENCE: high
EVIDENCE: https://github.com/Dokploy/dokploy | https://github.com/Dokploy/dokploy/blob/canary/LICENSE.MD | https://github.com/Dokploy/dokploy/security/advisories

### [REJECTED] k3s v1.37.1+k3s1
NEED: Деплой и CI/CD
KIND: open-source
URL: https://github.com/k3s-io/k3s
LICENSE: Apache-2.0
COMMERCIAL USE: Да.
PROJECT STATE: v1.37.1+k3s1 от 2026-09-30, 34 188 stars, 98 open issues, 26 workflows.
CLAIMED VS ACTUAL: none found (требования к ресурсам не перепроверял).
PRICING/LIMITS: 0.
RISKS: Kubernetes-операционка (манифесты/Helm, ingress, storage, обновления) для команды из нескольких человек и одного сервера — чистые накладные расходы; control plane отъедает RAM у приложения.
REPLACEABILITY: Целевой вариант при росте до нескольких узлов.
HOW VERIFIED: gh api (метаданные).
CONFIDENCE: medium
EVIDENCE: https://github.com/k3s-io/k3s

### [REJECTED] PaaS: Fly.io / Railway / Render
NEED: Деплой и CI/CD
KIND: commercial SaaS
URL: https://docs.fly.io/about/pricing
LICENSE: Проприетарные сервисы
COMMERCIAL USE: Да (платные планы).
PROJECT STATE: Действующие сервисы. Fly.io: бесплатного тира для новых организаций нет (trial 2 ч машинного времени или 7 дней). Railway: Hobby $5, Pro $20 в месяц + usage.
CLAIMED VS ACTUAL: «Дешёвый старт» не выдерживает постоянно работающего стека: Railway $10/ГБ RAM и $20/vCPU в месяц => 4 vCPU/8 ГБ ~ $160/мес; Fly shared-cpu-2x 4 ГБ ~ $25.39/мес за одну машину, Managed Postgres от $38/мес + $0.28/ГБ. Это в 5–20
раз дороже VPS той же мощности.
PRICING/LIMITS: Fly: shared-cpu-1x 1 ГБ $6.70, volumes $0.15/ГБ, IPv4 $2/мес, egress $0.02/ГБ (NA/EU). Railway: volume $0.15/ГБ, egress $0.05/ГБ. Render: цены со страницы не извлеклись.
RISKS: Стоимость, vendor lock-in на платформенные примитивы, данные расследований у третьей стороны, сложнее зафиксировать эталонное железо для замеров.
REPLACEABILITY: Средняя.
HOW VERIFIED: docs.fly.io/about/pricing и docs.railway.com/reference/pricing/plans прочитаны; render.com/pricing — контент не отдался (не проверено).
CONFIDENCE: medium
EVIDENCE: https://docs.fly.io/about/pricing | https://docs.railway.com/reference/pricing/plans | https://render.com/pricing

### [RECOMMENDED] OVHcloud VPS-2 (4 vCore / 8 GB / 75 GB NVMe)
NEED: VPS-провайдер и эталонная конфигурация
KIND: commercial SaaS
URL: https://www.ovhcloud.com/en-ie/vps/
LICENSE: n/a
COMMERCIAL USE: Да.
PROJECT STATE: Актуальная линейка VPS-1…VPS-4 на сайте 2026-10-14.
CLAIMED VS ACTUAL: Цена «From €7.21 ex. VAT/month» ($8.50 на ovhcloud.com/en) показана без указания срока; ссылки конфигуратора содержат pricing=upfront12 — вероятно, это цена при оплате за 12 месяцев вперёд; цена без обязательств на странице не
показана. Сторонние источники сообщают о повышениях цен OVH в 2026 — сверять на checkout.
CAPABILITIES: VPS-2: 4 vCore, 8 ГБ RAM, 75 ГБ NVMe, 1 Гбит/с, безлимитный трафик, ежедневный бэкап (последние 24 ч) включён.
PRICING/LIMITS: VPS-1 2/4/40 €3.81; VPS-2 4/8/75 €7.21; VPS-3 6/12/100 €10.40; VPS-4 8/24/200 €19.96 (ex VAT, «from»).
RISKS: Shared vCPU (модель CPU и steal не раскрыты); вероятный 12-месячный commitment; встроенный бэкап — у того же провайдера, off-site всё равно нужен.
REPLACEABILITY: Высокая: обычный Linux-VPS + Docker.
HOW VERIFIED: Чтение двух региональных страниц ovhcloud.com (en и en-ie) 2026-10-14; заказ не оформлялся.
CONFIDENCE: medium
EVIDENCE: https://www.ovhcloud.com/en-ie/vps/ | https://www.ovhcloud.com/en/vps/

### [ALTERNATIVE] Hetzner Cloud (CX33 / CPX32 / CCX13)
NEED: VPS-провайдер и эталонная конфигурация
KIND: commercial SaaS
URL: https://www.hetzner.com/cloud/
LICENSE: n/a
COMMERCIAL USE: Да.
PROJECT STATE: Два повышения цен в 2026: 1 апреля и 15 июня (официальная страница price-adjustment, изменена 2026-07-08). На status.hetzner.com открыто уведомление «Limited availability of cloud instances» с 2026-06-26; все тарифы Cost-Optimized
(CX/CAX) в отданном HTML помечены «currently unavailable».
CLAIMED VS ACTUAL: Репутация «самого дешёвого» устарела: CX33 (4 vCPU/8 ГБ/80 ГБ) €6.49 -> €8.49, но недоступен к заказу; доступный аналог CPX32 (4/8/160) подорожал с €13.99 до €35.49 (+154%); CCX13 (2 dedicated vCPU/8 ГБ) €15.99 -> €42.99.
Ограничения затрагивают новых клиентов (по сторонним пересказам статус-уведомления).
CAPABILITIES: Почасовая тарификация с месячным cap, снапшоты, firewall, API/Terraform, Object Storage в той же зоне.
PRICING/LIMITS: DE/FI, без НДС и IPv4: CX23 €5.49, CX33 €8.49, CAX21 €10.49, CPX22 €19.49, CPX32 €35.49, CCX13 €42.99 (€0.0689/ч). IPv4 ~€0.50/мес (сторонний источник). Трафик 20 ТБ в EU.
RISKS: Нет гарантии, что новый аккаунт сможет заказать нужный тариф; ценовая волатильность.
REPLACEABILITY: Высокая.
HOW VERIFIED: docs.hetzner.com price-adjustment (официальные таблицы), status.hetzner.com, страницы тарифов (цены в HTML не отрисовались, статусы доступности — да), два независимых блога.
CONFIDENCE: high
EVIDENCE: https://docs.hetzner.com/general/infrastructure-and-availability/price-adjustment/ | https://status.hetzner.com/ | https://www.hetzner.com/cloud/cost-optimized/ | https://www.hetzner.com/cloud/regular-performance/ | https://www.vincentschmalbach.com/hetzner-cheap-cloud-unavailable-price-increases/ | https://findstack.com/resources/hetzner-price-increase-2026

### [ALTERNATIVE] netcup VPS 1000 G12.5 (4 vCore / 8 GB / 128 GB)
NEED: VPS-провайдер и эталонная конфигурация
KIND: commercial SaaS
URL: https://www.netcup.com/en/server/vps
LICENSE: n/a
COMMERCIAL USE: Да.
PROJECT STATE: Актуальное поколение G12.5; G12 больше не заказывается (по странице).
CLAIMED VS ACTUAL: На странице по два числа на тариф (VPS 1000: €14.50 и €16.68 «incl. 19% VAT») без явной подписи первого; цены даны для 12-месячного контракта (−13%), 24 мес — −26%, цена помесячного контракта не показана.
CAPABILITIES: VPS 500: 2/4/64; VPS 1000: 4/8/128; VPS 2000: 8/16/256; локации Вена, Нюрнберг, Амстердам, Манассас, Сингапур; трафик включён.
PRICING/LIMITS: VPS 500 €8.26/€9.50; VPS 1000 €14.50/€16.68; VPS 2000 €26.92/€30.96 (12 мес).
RISKS: Контрактные сроки; локацию нельзя сменить после создания; точная net-цена требует проверки в корзине.
REPLACEABILITY: Высокая.
HOW VERIFIED: Чтение страницы netcup.com 2026-10-14 (docs only).
CONFIDENCE: medium
EVIDENCE: https://www.netcup.com/en/server/vps

### [REJECTED] Contabo Cloud VPS 4 / DigitalOcean Basic 8 GB
NEED: VPS-провайдер и эталонная конфигурация
KIND: commercial SaaS
URL: https://contabo.com/en/vps/
LICENSE: n/a
COMMERCIAL USE: Да.
PROJECT STATE: Действующие тарифы на 2026-10-14.
CLAIMED VS ACTUAL: Contabo: €4.40/мес — это цена при 24-месячном сроке (база €5.50) за 4 vCPU/8 ГБ/100 ГБ SSD; сторонние бенчмарки сообщают о высокой вариативности CPU (19% против 4% у Hetzner — сниппет, не проверено). DigitalOcean: стабильнее, но 4
vCPU/8 ГиБ/160 ГиБ стоит $48/мес, бэкапы +20–30%.
PRICING/LIMITS: Contabo Cloud VPS 4 €5.50 (€4.40 при 24 мес), VPS 6 6/12 €7.50. DigitalOcean: 2 ГиБ $12–18, 4 ГиБ $24, 8 ГиБ $48, 16 ГиБ $96; посекундная тарификация с 2026-01-01.
RISKS: Contabo — непредсказуемая производительность плохо подходит для эталонных замеров; DigitalOcean — цена в 5–6 раз выше OVH/netcup при тех же спецификациях.
HOW VERIFIED: Чтение contabo.com/en/vps и digitalocean.com/pricing/droplets; вариативность CPU — только сниппет.
CONFIDENCE: medium
EVIDENCE: https://contabo.com/en/vps/ | https://www.digitalocean.com/pricing/droplets

### [RECOMMENDED] VictoriaMetrics 1.154.0 + VictoriaLogs 1.53.0 + Grafana 13.2 + Grafana Alloy 1.20.1
NEED: Мониторинг и централизованные логи
KIND: open-source
URL: https://github.com/VictoriaMetrics/VictoriaLogs
LICENSE: VictoriaMetrics, VictoriaLogs, Alloy — Apache-2.0; Grafana — AGPL-3.0 (используется без модификаций как внутренний инструмент)
COMMERCIAL USE: Да. AGPL Grafana не затрагивает код платформы, пока Grafana не модифицируется и не встраивается в продукт.
PROJECT STATE: VictoriaMetrics v1.154.0 (2026-10-12), 17 851 stars; VictoriaLogs v1.53.0 (2026-10-01), отдельный репозиторий с 2025-07-06, 2 368 stars, 301 open issue; Grafana v13.2.4 (2026-10-13); Alloy v1.20.1 (2026-09-28), 3 612 stars, 1 273
open issues.
CLAIMED VS ACTUAL: «up to 30x less RAM and up to 15x less disk space than … Elasticsearch and Grafana Loki» — заявление вендора, не проверено. Ограничение из docs: Grafana Alerting UI не показывает datasource-managed правила через плагин
VictoriaLogs (алерты — файлами vmalert). У Alloy 1 273 открытых issue.
CAPABILITIES: Single-binary хранилища метрик и логов, приём Loki push/OTLP/syslog/journald, retention флагом (-retentionPeriod, по умолчанию 7 дней; лимит по диску), Grafana-плагин, алерты через vmalert; Alloy собирает логи Docker и метрики,
содержит loki.secretfilter.
INFRA: 4–5 контейнеров на том же VPS.
PRICING/LIMITS: 0; оценка потребления ~0.8–1.2 ГБ RAM на весь стек (не измерено).
RISKS: Мониторинг на том же сервере не сообщит о падении самого сервера — нужен внешний heartbeat; LogsQL — отдельный язык запросов.
REPLACEABILITY: Высокая: Alloy пишет в Loki/OTLP/remote-write совместимые приёмники (Grafana Cloud, Loki, Prometheus).
HOW VERIFIED: gh api (все четыре репозитория), docs.victoriametrics.com/victorialogs (первые 100k символов), grafana.com docs по Alloy.
CONFIDENCE: medium
EVIDENCE: https://github.com/VictoriaMetrics/VictoriaMetrics | https://github.com/VictoriaMetrics/VictoriaLogs | https://docs.victoriametrics.com/victorialogs/ | https://github.com/grafana/alloy | https://github.com/grafana/grafana

### [ALTERNATIVE] Prometheus 3.x + Loki 3.7 + Grafana + Alloy (классический стек)
NEED: Мониторинг и централизованные логи
KIND: open-source
URL: https://github.com/grafana/loki
LICENSE: Prometheus — Apache-2.0; Loki и Grafana — AGPL-3.0; Alloy — Apache-2.0
COMMERCIAL USE: Да при внутреннем использовании без модификаций.
PROJECT STATE: Prometheus v3.15.0 (2026-09-25; также свежий патч v3.13.4 от 2026-10-02), 66 529 stars; Loki v3.7.8 (2026-09-17), 29 010 stars, 1 058 open issues. Promtail — EOL с 2026-03-02, преемник Alloy.
CLAIMED VS ACTUAL: Документация Loki относит Docker/Compose-установку к «evaluation, testing, development» и для production рекомендует Helm/Tanka — то есть single-node Compose официально не production-путь. Старые гайды с Promtail устарели.
PRICING/LIMITS: 0.
RISKS: Больше движущихся частей и конфигурации (Loki storage/compactor/retention) при том же результате; AGPL у двух компонентов.
REPLACEABILITY: Высокая.
HOW VERIFIED: gh api, grafana.com/docs (loki install docker, promtail EOL).
CONFIDENCE: high
EVIDENCE: https://github.com/prometheus/prometheus | https://github.com/grafana/loki | https://grafana.com/docs/loki/latest/setup/install/docker/ | https://grafana.com/docs/loki/latest/send-data/promtail/

### [ALTERNATIVE] Grafana Cloud Free
NEED: Мониторинг и централизованные логи
KIND: commercial SaaS
URL: https://grafana.com/pricing/
LICENSE: Проприетарный сервис
COMMERCIAL USE: На странице цен ограничений на коммерческое использование free-тира нет («personal projects, exploring new ideas, and early-stage startups»); ToS не читал.
PROJECT STATE: Действующий сервис; лимиты на 2026-10-14.
CLAIMED VS ACTUAL: Retention 14 дней — недостаточно для журнала действий агентов (его нужно хранить в Postgres, а не в логах). Pro: $19/мес + $6.50 за 1k series и ~$0.50/ГБ логов (метки цен на странице обрезаны).
CAPABILITIES: 10k active series, 50 ГБ логов, 50 ГБ трейсов, retention 14 дней, 3 пользователя, 100k synthetic API-проверок в месяц, IRM на 3 пользователей. На сервере нужен только Alloy.
PRICING/LIMITS: Free: см. выше. Pro: от $19/мес.
RISKS: Логи расследований уходят третьей стороне (нужна строгая редакция и согласие владельца); зависимость от условий free-тира.
REPLACEABILITY: Высокая (те же протоколы).
HOW VERIFIED: Чтение grafana.com/pricing (docs only).
CONFIDENCE: medium
EVIDENCE: https://grafana.com/pricing/

### [REJECTED] SigNoz 0.145 / OpenObserve 1.1.0-rc2 / OpenTelemetry Collector 0.162
NEED: Мониторинг и централизованные логи
KIND: open-source
URL: https://github.com/SigNoz/signoz
LICENSE: SigNoz — MIT + каталоги ee/ под отдельной лицензией; OpenObserve — AGPL-3.0; OTel Collector — Apache-2.0
COMMERCIAL USE: Да (SigNoz — кроме ee/; OpenObserve — AGPL, внутреннее использование без модификаций).
PROJECT STATE: SigNoz v0.145.0 (2026-10-05), 32 349 stars, 1 537 open issues. OpenObserve v1.1.0-rc2 (2026-10-08), 22 345 stars. OTel Collector v0.162.0 (2026-09-28).
CLAIMED VS ACTUAL: SigNoz: минимум 4 ГБ RAM только под себя (ClickHouse + Keeper + Postgres 16 + collector), старые compose-файлы deprecated с v0.130.0 («Foundry is the supported path»), на Windows требуется WSL2 — половина эталонного сервера на
мониторинг. OpenObserve: последний тег — release candidate. OTel Collector — транспорт, а не хранилище.
PRICING/LIMITS: 0.
RISKS: Непропорциональные ресурсы (SigNoz); AGPL и RC-релизы (OpenObserve).
HOW VERIFIED: gh api (метаданные, LICENSE), signoz.io/docs/install/docker.
CONFIDENCE: medium
EVIDENCE: https://github.com/SigNoz/signoz | https://signoz.io/docs/install/docker/ | https://github.com/openobserve/openobserve | https://github.com/open-telemetry/opentelemetry-collector

### [RECOMMENDED] GlitchTip 6.2.6 (self-hosted, Sentry-SDK-совместимый)
NEED: Трекинг ошибок и uptime
KIND: open-source
URL: https://gitlab.com/glitchtip/glitchtip-backend
LICENSE: MIT (GitLab API)
COMMERCIAL USE: Да. Hosted: Free 1 000 событий/мес, $15/мес за 100k.
PROJECT STATE: Тег v6.2.6 от 2026-08-07, last_activity 2026-10-13, 359 stars (GitLab).
CLAIMED VS ACTUAL: Совместимость с Sentry — только по части ошибок/базовой производительности, без replay/profiling (по памяти; не перепроверял).
CAPABILITIES: Приём ошибок от sentry-sdk (sentry-python 2.72.0, MIT), uptime-проверки; требования: рекомендовано 512 МБ RAM, PostgreSQL 14+, Valkey/Redis опционален; retention по умолчанию 90 дней.
INFRA: 1–2 контейнера + существующий PostgreSQL.
PRICING/LIMITS: Self-hosted 0.
RISKS: Небольшая команда разработчиков (Burke Software); события ошибок могут содержать секреты — обязателен scrubber в SDK.
REPLACEABILITY: Высокая: смена DSN на Sentry/Bugsink.
HOW VERIFIED: GitLab API (project, license, tags), glitchtip.com (install, pricing), gh api getsentry/sentry-python.
CONFIDENCE: high
EVIDENCE: https://gitlab.com/glitchtip/glitchtip-backend | https://glitchtip.com/documentation/install | https://glitchtip.com/pricing

### [ALTERNATIVE] Sentry (SaaS Developer/Team и self-hosted 26.9.0)
NEED: Трекинг ошибок и uptime
KIND: commercial SaaS
URL: https://sentry.io/pricing/
LICENSE: FSL-1.1-Apache-2.0 (не OSI; через 2 года -> Apache-2.0)
COMMERCIAL USE: SaaS — да. Self-hosted — да для внутреннего использования; запрещено Competing Use (продавать Sentry как сервис).
PROJECT STATE: self-hosted 26.9.0 (2026-09-16), getsentry/sentry 45 552 stars.
CLAIMED VS ACTUAL: Self-hosted «для low-volume и PoC» требует минимум 4 ядра, 16 ГБ RAM + 16 ГБ swap (рекомендовано 32 ГБ) — вдвое больше всего эталонного сервера. Бесплатный Developer-план: 1 пользователь, 5k ошибок.
PRICING/LIMITS: Developer $0 (1 user, 5k errors, 5 ГБ логов, 30 дней); Team $26/мес (годовая оплата, 50k errors); Business $80/мес.
RISKS: SaaS: данные об ошибках (потенциально с адресами/данными пользователей) у третьей стороны; self-hosted — неподъёмен по ресурсам.
REPLACEABILITY: Высокая (тот же SDK).
HOW VERIFIED: sentry.io/pricing, develop.sentry.dev/self-hosted, gh api + чтение LICENSE.md.
CONFIDENCE: high
EVIDENCE: https://sentry.io/pricing/ | https://develop.sentry.dev/self-hosted/ | https://github.com/getsentry/self-hosted

### [ALTERNATIVE] Bugsink 2.6.1
NEED: Трекинг ошибок и uptime
KIND: open-source
URL: https://github.com/bugsink/bugsink
LICENSE: PolyForm Shield 1.0.0 (source-available, не OSI) + ee/ под отдельной лицензией
COMMERCIAL USE: Внутреннее использование разрешено; запрещено использовать для конкурирующего с Bugsink продукта.
PROJECT STATE: 2.6.1 от 2026-09-25, коммит 2026-10-13, 2 122 stars, 133 open issues, 10 workflows.
CLAIMED VS ACTUAL: Часто называют «open source», но лицензия — PolyForm Shield (прочитано в LICENSE).
PRICING/LIMITS: Self-hosted 0.
RISKS: Не-OSI лицензия, молодой проект (2024-08).
HOW VERIFIED: gh api + чтение LICENSE, bugsink.com/docs.
CONFIDENCE: medium
EVIDENCE: https://github.com/bugsink/bugsink | https://www.bugsink.com/docs/

### [RECOMMENDED] Uptime Kuma 2.5.6 + внешний heartbeat (healthchecks.io)
NEED: Трекинг ошибок и uptime
KIND: open-source
URL: https://github.com/louislam/uptime-kuma
LICENSE: Uptime Kuma — MIT; healthchecks.io — SaaS
COMMERCIAL USE: Uptime Kuma — да. healthchecks.io Hobbyist: 20 проверок бесплатно, условие про коммерческое использование на странице не указано; Business $20/мес (100 проверок).
PROJECT STATE: Uptime Kuma 2.5.6 от 2026-10-09, 92 412 stars, 836 open issues, 30 workflows.
CLAIMED VS ACTUAL: Uptime Kuma на том же сервере не обнаружит падение сервера — поэтому нужен внешний сервис. Бесплатные тиры конкурентов оговорены: Better Stack — «Free for personal projects» (10 мониторов, логи 3 ГБ/3 дня), UptimeRobot Free —
«hobby and non-profit projects» (50 мониторов, 5 мин) — для коммерческого продукта сомнительны.
CAPABILITIES: HTTP/TCP/keyword/JSON-query/Docker-мониторы, интервал от 20 с, 90+ каналов уведомлений (Telegram, e-mail), status pages. healthchecks.io — dead-man-switch для cron бэкапов и самого сервера.
PRICING/LIMITS: 0 (в пределах free-тиров).
RISKS: NFS не поддерживается для данных Kuma (README).
REPLACEABILITY: Высокая.
HOW VERIFIED: gh api + README, healthchecks.io/pricing, betterstack.com/pricing, uptimerobot.com/pricing.
CONFIDENCE: high
EVIDENCE: https://github.com/louislam/uptime-kuma | https://healthchecks.io/pricing/ | https://betterstack.com/pricing | https://uptimerobot.com/pricing/

### [RECOMMENDED] pgBackRest 2.59.3
NEED: Бэкапы PostgreSQL и файлов
KIND: open-source
URL: https://github.com/pgbackrest/pgbackrest
LICENSE: MIT (текст LICENSE прочитан)
COMMERCIAL USE: Да.
PROJECT STATE: v2.59.3 от 2026-10-04, коммит 2026-10-13, 4 437 stars, 30 open issues, 17 workflows.
CLAIMED VS ACTUAL: Два существенных факта 2026 года: (1) 2026-04-27 автор объявил, что проект больше не поддерживается; 2026-05-18 — «pgBackRest Will Continue!» благодаря коалиции спонсоров (AWS, Supabase, pgEdge, Tiger Data, Percona, Eon.io) — bus-
factor остаётся. (2) 2026-10-04 раскрыта уязвимость «Weak Encryption Subkeys and Salts»: версии до 2.59.3 могли создавать слабые ключи шифрования репозитория — использовать только >=2.59.3.
CAPABILITIES: Full/diff/incr (в т.ч. блочные), параллельное сжатие lz4/zstd, WAL-архив и PITR, репозитории S3/Azure/GCS, шифрование, verify, несколько репозиториев.
INFRA: Устанавливается рядом с PostgreSQL (в том же образе/контейнере), доступ к S3-совместимому бакету.
PRICING/LIMITS: 0.
RISKS: Зависимость от одного основного автора; конфигурация archive_command требует аккуратности.
REPLACEABILITY: Средняя: формат репозитория свой, замена — WAL-G/Barman с новым базовым бэкапом.
HOW VERIFIED: gh api, README и pgbackrest.org/news.html прочитаны.
CONFIDENCE: high
EVIDENCE: https://github.com/pgbackrest/pgbackrest | https://pgbackrest.org/news.html

### [ALTERNATIVE] WAL-G 3.0.9
NEED: Бэкапы PostgreSQL и файлов
KIND: open-source
URL: https://github.com/wal-g/wal-g
LICENSE: Apache-2.0 (LICENSE.md прочитан; API: NOASSERTION)
COMMERCIAL USE: Да.
PROJECT STATE: v3.0.9 от 2026-08-20, коммит 2026-10-12, 4 303 stars, 329 open issues, 19 workflows.
CLAIMED VS ACTUAL: none found (документацию глубоко не читал); заметно больше открытых issues, чем у pgBackRest (329 против 30).
CAPABILITIES: Один Go-бинарь, WAL-архив и PITR в S3-совместимое хранилище, поддержка нескольких СУБД.
PRICING/LIMITS: 0.
RISKS: Нет встроенной команды verify уровня pgBackRest (по памяти, не перепроверено); документация слабее.
REPLACEABILITY: Средняя.
HOW VERIFIED: gh api + чтение LICENSE.md.
CONFIDENCE: medium
EVIDENCE: https://github.com/wal-g/wal-g

### [REJECTED] Barman 3.20.1
NEED: Бэкапы PostgreSQL и файлов
KIND: open-source
URL: https://github.com/EnterpriseDB/barman
LICENSE: GPL-3.0
COMMERCIAL USE: Да при внутреннем использовании (GPL без распространения обязательств не создаёт).
PROJECT STATE: 3.20.1 от 2026-09-29, 3 259 stars, 41 open issues, 5 workflows; поддерживается EDB.
CLAIMED VS ACTUAL: none found
PRICING/LIMITS: 0.
RISKS: Архитектурно рассчитан на отдельный backup-сервер; для single-server MVP избыточен; Python-стек на хосте.
HOW VERIFIED: gh api.
CONFIDENCE: medium
EVIDENCE: https://github.com/EnterpriseDB/barman

### [RECOMMENDED] restic 0.19.1 (файлы, тома, pg_dump-копии)
NEED: Бэкапы PostgreSQL и файлов
KIND: open-source
URL: https://github.com/restic/restic
LICENSE: BSD-2-Clause
COMMERCIAL USE: Да.
PROJECT STATE: v0.19.1 от 2026-07-05, коммит 2026-10-11, 36 547 stars, 621 open issues, 7 workflows.
CLAIMED VS ACTUAL: none found. borg (альтернатива): стабильная ветка 1.4.5 (2026-07-18), 2.0 всё ещё beta (2.0.0b25, 2026-09-27) — поэтому не выбран.
CAPABILITIES: Дедуплицированные шифрованные снапшоты в S3-совместимые хранилища, B2, SFTP, REST server, rclone; пароль через RESTIC_PASSWORD_FILE/COMMAND. Документация рекомендует B2 через S3-совместимый API.
PRICING/LIMITS: 0.
RISKS: Потеря пароля = потеря бэкапов; сам по себе не даёт консистентного снимка работающей БД (для БД — pgBackRest).
REPLACEABILITY: Высокая.
HOW VERIFIED: gh api (restic, borg), restic.readthedocs.io.
CONFIDENCE: high
EVIDENCE: https://github.com/restic/restic | https://restic.readthedocs.io/en/stable/030_preparing_a_new_repo.html | https://github.com/borgbackup/borg

### [RECOMMENDED] Backblaze B2 (S3-совместимое хранилище бэкапов)
NEED: Хранилище для бэкапов (off-site)
KIND: commercial SaaS
URL: https://www.backblaze.com/cloud-storage/pricing
LICENSE: n/a
COMMERCIAL USE: Да.
PROJECT STATE: Действующий сервис, цены на 2026-10-14.
CLAIMED VS ACTUAL: none found
CAPABILITIES: S3-совместимый API; Object Lock (governance/compliance, legal hold) без доплаты — защита бэкапов от удаления при компрометации сервера.
PRICING/LIMITS: $6.95/ТБ/мес (pay-as-you-go), первые 10 ГБ бесплатно, egress бесплатно до 3x от среднего объёма, далее $0.01/ГБ; вызовы API классов A–C бесплатны; минимального срока хранения нет.
RISKS: Регион выбирается при создании аккаунта (EU/US) — проверить при регистрации.
REPLACEABILITY: Высокая (S3 API).
HOW VERIFIED: Чтение страницы цен и docs Object Lock.
CONFIDENCE: high
EVIDENCE: https://www.backblaze.com/cloud-storage/pricing | https://www.backblaze.com/docs/cloud-storage-object-lock

### [ALTERNATIVE] Cloudflare R2
NEED: Хранилище для бэкапов (off-site)
KIND: commercial SaaS
URL: https://developers.cloudflare.com/r2/pricing/
LICENSE: n/a
COMMERCIAL USE: Да.
PROJECT STATE: Действующий сервис.
CLAIMED VS ACTUAL: none found (поддержку object lock/retention в R2 не проверял).
PRICING/LIMITS: Standard $0.015/ГБ-мес; Class A $4.50/млн, Class B $0.36/млн; egress бесплатно; free tier 10 ГБ, 1 млн Class A, 10 млн Class B в месяц; IA $0.01/ГБ с минимумом 30 дней.
RISKS: В ~2 раза дороже B2 за ГБ; оплата операций при частых WAL-пушах.
REPLACEABILITY: Высокая (S3 API).
HOW VERIFIED: Чтение developers.cloudflare.com/r2/pricing.
CONFIDENCE: high
EVIDENCE: https://developers.cloudflare.com/r2/pricing/

### [ALTERNATIVE] Hetzner Object Storage
NEED: Хранилище для бэкапов (off-site)
KIND: commercial SaaS
URL: https://www.hetzner.com/storage/object-storage/
LICENSE: n/a
COMMERCIAL USE: Да.
PROJECT STATE: Локации FSN1/NBG1/HEL1; на status.hetzner.com открыт инцидент «Object Storage in location HEL1 partially degraded» с 2026-09-09 (статус Monitoring).
CLAIMED VS ACTUAL: Сумма базовой цены на официальной странице не отрисовалась; по сторонним источникам €4.99 -> €6.49/мес с 2026-04-01, сверх квоты ~€8.70/ТБ-мес. Docs: «not ideal for all S3 workloads». Плата фиксированная, даже если хранится 5 ГБ.
CAPABILITIES: S3-совместимо, object locking, versioning, expiry; в базовую цену входят 1 ТБ хранения и ~1 ТБ egress; лимиты 100 бакетов, 750 req/s на бакет.
PRICING/LIMITS: ~€6.49/мес базово (search snippet), объекты <64 КБ тарифицируются как 64 КБ.
RISKS: Если сервер тоже в Hetzner — бэкап у того же провайдера (не off-site); затяжная деградация HEL1.
REPLACEABILITY: Высокая.
HOW VERIFIED: hetzner.com и docs.hetzner.com (структура тарифа, лимиты), status.hetzner.com; сумма — только сторонние источники.
CONFIDENCE: medium
EVIDENCE: https://www.hetzner.com/storage/object-storage/ | https://docs.hetzner.com/storage/object-storage/overview/ | https://status.hetzner.com/ | https://sliplane.io/blog/cheap-object-storage-providers-europe

### [RECOMMENDED] SOPS 3.13.3 + age 1.3.2 (+ Compose secrets как файлы)
NEED: Хранение секретов
KIND: open-source
URL: https://github.com/getsops/sops
LICENSE: SOPS — MPL-2.0; age — BSD-3-Clause
COMMERCIAL USE: Да.
PROJECT STATE: SOPS v3.13.3 (2026-07-23), коммит 2026-10-13, 23 377 stars, 456 open issues (проект CNCF). age v1.3.2 (2026-08-29), 23 904 stars, 21 open issue.
CLAIMED VS ACTUAL: none found
CAPABILITIES: Шифрованные YAML/JSON/ENV/INI/binary в git; ключи age (в т.ч. гибридные post-quantum), PGP, KMS, Vault/OpenBao; подкоманды exec-env и exec-file (в cmd/sops/main.go); переменные SOPS_AGE_KEY / SOPS_AGE_KEY_FILE / SOPS_AGE_KEY_CMD
(в age/keysource.go). На сервере: расшифровка в tmpfs -> Compose secrets -> /run/secrets.
INFRA: Приватный age-ключ на сервере (0600, вне репозитория) и офлайн-копия у владельца.
PRICING/LIMITS: 0.
RISKS: Нет аудита доступа, динамических секретов и автоматической ротации; компрометация сервера = компрометация ключа расшифровки; ротация API-ключей — ручной регламент.
REPLACEABILITY: Высокая: значения переносятся в Infisical/OpenBao.
HOW VERIFIED: gh api (оба репозитория), чтение исходников SOPS (grep exec-env, SOPS_AGE_KEY*), README age, getsops.io/docs.
CONFIDENCE: high
EVIDENCE: https://github.com/getsops/sops | https://raw.githubusercontent.com/getsops/sops/main/cmd/sops/main.go | https://raw.githubusercontent.com/getsops/sops/main/age/keysource.go | https://github.com/FiloSottile/age | https://getsops.io/docs/

### [ALTERNATIVE] Infisical 0.166.5
NEED: Хранение секретов
KIND: open-source
URL: https://github.com/Infisical/infisical
LICENSE: MIT для ядра + каталоги ee/ под отдельной лицензией (LICENSE прочитан)
COMMERCIAL USE: Да для MIT-части; cloud Free — 5 identities, 3 окружения.
PROJECT STATE: v0.166.5 от 2026-10-12, 29 737 stars, 812 open issues, 40 workflows.
CLAIMED VS ACTUAL: В бесплатном плане нет версионирования секретов, point-in-time recovery, ротации, динамических секретов и хранения audit log — именно то, ради чего берут менеджер секретов; Pro $20–23 за identity в месяц (машинные identity тоже
считаются).
INFRA: Self-host: отдельный сервис + PostgreSQL + Redis (по памяти, не перепроверено).
PRICING/LIMITS: Free $0 (5 identities); Pro $20/identity/мес (годовая) или $23.
RISKS: Self-host добавляет критичный сервис на тот же сервер; cloud — секреты у третьей стороны.
REPLACEABILITY: Средняя.
HOW VERIFIED: gh api + LICENSE, infisical.com/pricing.
CONFIDENCE: medium
EVIDENCE: https://github.com/Infisical/infisical | https://infisical.com/pricing

### [REJECTED] OpenBao 2.7.1 / HashiCorp Vault 2.1.x
NEED: Хранение секретов
KIND: open-source
URL: https://github.com/openbao/openbao
LICENSE: OpenBao — MPL-2.0; Vault — Business Source License 1.1 (лицензиар IBM)
COMMERCIAL USE: OpenBao — да. Vault — production-использование разрешено, кроме «competitive offering» (hosted/embedded предложение, конкурирующее с платным Vault).
PROJECT STATE: OpenBao v2.7.1 (2026-10-01), 8 423 stars, 337 open issues, 23 workflows, под OpenSSF/Linux Foundation. Vault v2.1.2 (2026-10-07), 36 388 stars.
CLAIMED VS ACTUAL: Vault по-прежнему часто называют open source — фактически BUSL 1.1 (LICENSE прочитан). none found для OpenBao.
PRICING/LIMITS: 0 (self-hosted).
RISKS: Unseal, политики, бэкап и HA самого хранилища — избыточная операционная нагрузка для одного сервера и ~10–20 секретов.
REPLACEABILITY: OpenBao — целевой вариант при росте (динамические учётки БД, аудит).
HOW VERIFIED: gh api + чтение LICENSE Vault, README OpenBao.
CONFIDENCE: high
EVIDENCE: https://github.com/openbao/openbao | https://github.com/hashicorp/vault/blob/main/LICENSE

### [ALTERNATIVE] Doppler / 1Password
NEED: Хранение секретов
KIND: commercial SaaS
URL: https://www.doppler.com/pricing
LICENSE: Проприетарные сервисы
COMMERCIAL USE: Doppler Developer: про коммерческое использование не сказано (план описан как для «solo projects»). 1Password — цены и условия не извлеклись.
PROJECT STATE: Действующие сервисы.
CLAIMED VS ACTUAL: Doppler: карточка плана говорит «3 free users», сравнительная таблица — лимит 25 (расхождение на самой странице); activity log на бесплатном плане хранится 3 дня.
PRICING/LIMITS: Doppler Developer: 3 пользователя бесплатно, далее $8/мес за пользователя, 10 проектов, 4 окружения, 50 service tokens; Team $21/пользователь/мес.
RISKS: Все API-ключи платформы у третьей стороны; сетевой запрос при старте сервиса.
REPLACEABILITY: Высокая (значения переносимы; у Kamal есть адаптеры doppler и 1password).
HOW VERIFIED: doppler.com/pricing прочитан; 1password.com — нужная страница не получена.
CONFIDENCE: low
EVIDENCE: https://www.doppler.com/pricing | https://1password.com/pricing/password-manager

### [RECOMMENDED] structlog 26.1.0 — redaction-процессор в приложении
NEED: Редакция API-ключей в логах и отчётах
KIND: open-source
URL: https://github.com/hynek/structlog
LICENSE: MIT OR Apache-2.0
COMMERCIAL USE: Да.
PROJECT STATE: 26.1.0 от 2026-06-06, коммит 2026-10-05, 4 972 stars, 39 open issues, 8 workflows, Python >=3.10 (до 3.15).
CLAIMED VS ACTUAL: Готового встроенного «secret scrubber» в библиотеке нет — процессор пишется самостоятельно (~30 строк); это glue-код.
CAPABILITIES: Структурные JSON-логи с цепочкой процессоров: свой процессор маскирует значения по именам полей (api_key, authorization, token…) и по точным значениям загруженных секретов (самый надёжный способ — заменять известные строки
секретов).
PRICING/LIMITS: 0.
RISKS: Не покрывает логи сторонних библиотек (httpx/urllib3 URL с ключом в query) без маршрутизации stdlib logging через structlog.
REPLACEABILITY: Высокая.
HOW VERIFIED: gh api, PyPI JSON; отсутствие встроенного скраббера — по знанию библиотеки, документацию сегодня не перечитывал.
CONFIDENCE: medium
EVIDENCE: https://github.com/hynek/structlog | https://pypi.org/project/structlog/

### [RECOMMENDED] Grafana Alloy loki.secretfilter (правила Gitleaks)
NEED: Редакция API-ключей в логах и отчётах
KIND: open-source
URL: https://grafana.com/docs/alloy/latest/reference/components/loki/loki.secretfilter/
LICENSE: Apache-2.0 (Alloy)
COMMERCIAL USE: Да.
PROJECT STATE: Компонент Alloy v1.20.1 (2026-09-28).
CLAIMED VS ACTUAL: Документация прямо предупреждает: «Don't rely solely on this component to redact sensitive information»; возможны ложные срабатывания и пропуски; заметно повышает CPU; не сканирует labels; набор правил по умолчанию меняется между
версиями Alloy. Ключи TronGrid/Tronscan формата UUID стандартными правилами могут не ловиться — нужны свои правила.
CAPABILITIES: Вторая линия защиты на пути логов: regex-правила Gitleaks, redact_with/redact_percent (по умолчанию 80), свой gitleaks_config, метрики срабатываний.
PRICING/LIMITS: 0.
RISKS: См. выше; только логи, не Sentry-события и не отчёты.
REPLACEABILITY: Высокая (аналог — Vector VRL redact, MPL-2.0).
HOW VERIFIED: Чтение страницы компонента в docs Alloy; gh api grafana/alloy, vectordotdev/vector.
CONFIDENCE: high
EVIDENCE: https://grafana.com/docs/alloy/latest/reference/components/loki/loki.secretfilter/ | https://github.com/grafana/alloy | https://github.com/vectordotdev/vector

### [REJECTED] Только фильтры на стороне сборщика/ SaaS (Vector VRL, server-side scrubbing Sentry)
NEED: Редакция API-ключей в логах и отчётах
KIND: open-source
URL: https://github.com/vectordotdev/vector
LICENSE: Vector — MPL-2.0
COMMERCIAL USE: Да.
PROJECT STATE: Vector: 22 697 stars, коммит 2026-10-13, 2 494 open issues.
CLAIMED VS ACTUAL: none found (детали VRL redact и серверного скраббинга Sentry сегодня не перепроверял).
PRICING/LIMITS: 0.
RISKS: Редакция «после факта»: секрет уже покинул процесс и может попасть в stdout контейнера, docker json-log на диске, core dump, отчёт. Как единственная мера не удовлетворяет требованию «ключи никогда не попадают в логи и отчёты».
HOW VERIFIED: gh api (метаданные).
CONFIDENCE: low
EVIDENCE: https://github.com/vectordotdev/vector

## OPEN QUESTIONS FOR OWNER (researcher)
- Какие юрисдикции и языки приоритетны для писем (RU/EN/другие) и требуется ли для отчёта юридически значимая метка времени или подпись (квалифицированный eIDAS TSA, PAdES с сертификатом организации) — или на MVP достаточно хеш-
манифеста + бесплатного RFC 3161 + OpenTimestamps?
- Допустимо ли отправлять логи/ошибки/метрики во внешние SaaS (Grafana Cloud, Sentry) или все данные расследований должны оставаться на собственном сервере? От этого зависит выбор между self-hosted стеком и Grafana Cloud Free.
- Какие RPO/RTO приемлемы: PITR с потерей минут (pgBackRest) или достаточно ночного дампа (RPO 24 ч) на первом этапе? Сколько часов простоя допустимо при потере сервера?
- Бюджет и условия на сервер: готов ли владелец к 12-месячному обязательству (OVH/netcup, ~€7–17/мес) или нужна почасовая оплата без обязательств (Hetzner CPX32, ~€36/мес)? Есть ли уже аккаунт Hetzner со старыми тарифами CX?
- Достаточно ли 8 ГБ RAM для эталонной конфигурации с учётом выбора графового хранилища в других областях аудита, или эталон сразу фиксировать как 8 vCPU / 16–24 ГБ?
- Нужны ли письма в редактируемом DOCX (для юристов/следователей) или достаточно PDF? Кто юридически вычитывает шаблоны и формулировки (платформа не должна обещать заморозку/возврат)?
- Срок хранения отчётов и материалов расследований и политика удаления по запросу пользователя (GDPR) — это определяет retention бэкапов и допустимость Object Lock.
- Репозиторий приватный на GitHub Free (2 000 мин Actions/мес) или другой план/хостинг кода? Допустим ли GHCR как registry образов?
- Должен ли PDF-отчёт соответствовать PDF/A (архивный формат) и содержать вложенные JSON/manifest, или PDF — только человекочитаемая копия рядом с JSON?
- Кто владеет подписывающим ключом платформы и офлайн-копией age-ключа (процедура восстановления при уходе сотрудника)?

## NOT VERIFIED (researcher)
- Производительность WeasyPrint на таблицах 5–10 тыс. строк и расход памяти не измерялись (запуск стороннего кода запрещён правилами аудита); цифры 0.9–1.9 с на 1 200 строк — из PR #2808 автора PR.
- Корректность рендера кириллицы и покрытие шрифтов в WeasyPrint/Typst/Chromium не проверялись рендером; для Typst проверен только список встроенных шрифтов.
- Валидность PDF/A-3 из WeasyPrint (veraPDF) не проверялась; veraPDF как инструмент не аудировался.
- Первичные страницы Binance (law-enforcement, guidelines) и OKX (law enforcement request guide) не открылись (ECONNRESET); tether.io/legal вернул 404. Требования к запросам LE подтверждены только поисковыми сниппетами и вторичными
источниками.
- Условия использования FreeTSA для коммерческого сервиса (явных ToS нет), лимиты Sectigo (15 с между запросами — сниппет) и цены квалифицированных TSA (Lleida €0.03, SK ID, Certigna — сниппеты, валюта и минимальные пакеты не
подтверждены). Запросы к TSA не отправлялись.
- Базовая цена Hetzner Object Storage (€6.49/мес) и IPv4 (€0.50/мес) — только из сторонних источников: на официальных страницах суммы не отрисовались. Статус «currently unavailable» для CPX-тарифов может быть артефактом JS-
рендеринга; для CX/CAX подтверждён двумя независимыми блогами и статус-страницей.
- Срок обязательств, на который действует цена OVHcloud VPS-2 €7.21 (предположительно 12 мес upfront по параметру ссылки), цена без обязательств, модель CPU и датацентры.
- Точная net-цена netcup VPS 1000 G12.5 (на странице два числа — €14.50 и €16.68 incl. VAT — без однозначной подписи) и цена помесячного контракта.
- Цены Render и бизнес-планов 1Password (страницы не отдали содержимое).
- Условия коммерческого использования бесплатных тиров Grafana Cloud, healthchecks.io и Doppler по их ToS (читались только страницы цен).
- Фактическое потребление RAM/CPU стеком VictoriaMetrics + VictoriaLogs + Grafana + Alloy + GlitchTip и итоговая оценка ~6 ГБ на эталонном сервере — расчётные оценки, не замеры. Заявление VictoriaLogs «up to 30x less RAM» —
вендорское.
- Требования Infisical self-hosted (PostgreSQL + Redis), отсутствие встроенного скраббера в structlog, возможности Vector VRL redact и серверного data scrubbing Sentry/GlitchTip — по прежним знаниям, сегодня не перепроверялись.
- Работа Kamal на Windows 11 без WSL (есть только косвенное свидетельство — открытый issue #1350).
- Тексты лицензий Tectonic, bagit-python (GitHub API не определил лицензию), LICENSE_PROPRIETARY и TERMS_AND_CONDITIONS Dokploy, ee/LICENSE Infisical и SigNoz не читались.
- Поддержка Object Lock/retention в Cloudflare R2 и в связке pgBackRest/restic + B2 Object Lock на практике (совместимость с expire/prune) не проверялась.
- Стоимость домена и e-mail-рассылки уведомлений, а также тарифы на исходящий трафик сверх включённого у VPS-провайдеров.
- Актуальные версии ОС для эталона (Ubuntu 24.04 LTS / 26.04 LTS, Debian 13) и поддерживаемая версия PostgreSQL не перепроверялись — относятся к смежной области.
- BagIt (RFC 8493) и Sigstore Rekor как альтернативные механизмы целостности проверены только на уровне метаданных репозиториев (bagit-python v1.9.0 от 2025-06-13; rekor v1.5.4 от 2026-08-20), подробно не аудировались.