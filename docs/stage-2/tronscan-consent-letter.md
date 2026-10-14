# Письмо в TRONSCAN: запрос согласия на коммерческое использование API

Черновик письма к решению 1.10 в [stage-2-decisions.md](../spec/stage-2-decisions.md). Сначала — заметка для владельца на русском, затем текст письма на английском. Поля в квадратных скобках заполняет владелец.

## Заметка для владельца

**Почему письмо нужно.** Мы прочитали условия TRONSCAN (Terms of Service, «Last updated: January 4, 2022», PDF https://static.tronscan.org/pdf/TRONSCAN_Terms_of_Service.pdf, скачан 2026-10-14, SHA-256 файла `77ba0f2fdf512b61b7c98570bff656d8c41437efe63c4bb23df57d44957fb2ae`). Нас касаются разделы:
- **§6 Acceptable Use** — запрещено разрабатывать сторонние приложения, которые взаимодействуют с сервисами TRONSCAN, без их предварительного письменного согласия; запрещён автоматизированный доступ и сбор данных средствами, «не предоставленными» TRONSCAN (официальный API, по нашему прочтению, — средство, предоставленное ими, но это стоит подтвердить).
- **§8 Copyrights** — данные и материалы сайта принадлежат компании; использование и копирование без письменного разрешения запрещены; выдержки и ссылки допускаются с полным и ясным указанием TRONSCAN.io и ссылкой на исходную страницу.
- **§9 Trademarks** — название TRONSCAN нельзя использовать без письменного разрешения; а в отчётах мы хотим указывать TRONSCAN как источник.
- **§1 Eligibility** — сервисом не могут пользоваться граждане, резиденты и организации материкового Китая, Тайваня, Гонконга, США и Сингапура. ООО WHOMEVER (Узбекистан) под это не подпадает, но наши клиенты могут быть из этих стран — об этом вопрос в письме.
- **§17** — право Сингапура.

Это те же разделы, что указаны в аудите Этапа 1 (§1, §6, §8). Действует ли эта редакция и есть ли отдельные условия для API, проверить не удалось: сайты tronscan.org, tronscan.io, docs.tronscan.org и support.tronscan.org отвечают автоматическим клиентам проверкой Cloudflare (HTTP 403). Документация API (по выдаче поиска) требует ключ для Mainnet и не публикует квоты ключа.

**До ответа TRONSCAN** действует решение G5: TronScan вне критического пути, его теги не хранятся.

**Куда отправлять.** Официальный контакт подтвердить не удалось (см. выше). Порядок:
1. Открыть https://tronscan.org в обычном браузере и найти в подвале страницы раздел контактов или поддержки; второй вариант — форма «Submit a request» в центре поддержки https://support.tronscan.org (адрес встречается в выдаче поиска; сама страница нам не открылась).
2. Брать адрес только с официального сайта. Не использовать адреса из сторонних каталогов: вокруг криптосервисов много поддельных контактов.
3. Отправить с корпоративного адреса компании, приложить выписку о регистрации компании, если попросят. Сохранить копию письма и ответ: письменное согласие — документ для нашего архива условий.

**Что заполнить:** реквизиты компании, ФИО и должность подписанта, контактный e-mail, адрес сайта, если он уже есть. Оценки объёмов в письме — наши расчётные, не замер; при необходимости поправить.

---

## Letter (English)

**Subject:** Request for written consent to use the TRONSCAN API in a commercial blockchain-investigation service (WHOMEVER LLC, Uzbekistan)

Dear TRONSCAN team,

We are WHOMEVER LLC (in Russian: ООО «WHOMEVER»), a limited liability company registered in the Republic of Uzbekistan [registration number: …; registered address: …]. We are building LEDGERHUNT, a service that helps victims of cryptocurrency theft trace stolen USDT-TRC20 on the TRON network and prepare reports for the victims themselves, for exchange compliance teams and for law enforcement.

We have read the TRONSCAN Terms of Service (last updated January 4, 2022). Section 6 requires your prior written consent before third-party applications interact with your Services, Section 8 requires express written permission for use of TRONSCAN materials beyond excerpts and links with credit, and Section 9 requires written permission to use the TRONSCAN name. We would like to use the TRONSCAN API commercially and in full compliance with these terms, so we are asking for your written consent for the use described below, or for the terms under which such use is possible.

**1. Intended use**

- Read-only calls to the public TRONSCAN API (apilist.tronscanapi.com) with our own API key sent in the `TRON-PRO-API-KEY` header. We do not send transactions and do not use any write or account functions.
- Endpoints we expect to use:
  - `/api/account/tag` — public address tags (for example, exchange or service labels);
  - `/api/accountv2` — basic public account information;
  - `/api/token_trc20/transfers` — TRC20 transfer history of an address, used only to cross-check data we obtain from other sources;
  - `/api/transaction-info` — details of a single transaction.
- Rate: at most 1 request per second from a single server, with exponential back-off on HTTP 429 and respect for `Retry-After`. All requests go through one rate-limited gateway that logs every call.
- Expected volume (our planning estimate, not a measurement): up to about 100 requests per investigation; about 5,000 requests per month in the first phase (tens of investigations per month); up to about 100,000 requests per month if we reach 1,000 investigations per month. We will ask you before exceeding the quota you assign.

**2. How the data would be used and stored**

- TRONSCAN tags would be one corroborating signal next to our own analysis of on-chain data. They would never be the only basis for a conclusion in a report.
- We would store the raw API responses we receive, with a timestamp and a SHA-256 hash, as evidence of what was shown at the time of the investigation.
- In investigation reports we would quote only the tags relevant to the addresses in the case, with attribution in this form (or any form you prefer): "Source: TRONSCAN (tronscan.org), address tag retrieved YYYY-MM-DD HH:MM UTC", with a link to the address page on tronscan.org.
- Reports go to the victim (our client) and, at the victim's request, to the security or compliance team of the exchange concerned and to law enforcement.

**3. What we will not do**

- We will not resell, sublicense or redistribute TRONSCAN data, and will not offer it as a database, API, data feed or bulk export.
- We will not mirror or bulk-download TRONSCAN data, will not scrape the website, and will not train machine-learning models on TRONSCAN data.
- We will not use the TRONSCAN logo or imply endorsement. We will use the name only for attribution, if you allow it.
- We will stop using the data and remove stored tags on your request.

**4. Questions**

1. Do you grant written consent under Sections 6 and 8 for the use described above? Are there conditions or fees?
2. Is the Terms of Service dated January 4, 2022 the current version, and does it apply to the API? Are there separate API terms we should accept?
3. What quotas apply with an API key (requests per second and per day)? Is there a paid or partner plan with higher limits?
4. How long may we store API responses and tags? May tags remain in reports that recipients (victims, exchanges, police) keep?
5. What attribution format do you require, and may we use the name TRONSCAN for attribution (Section 9)?
6. Section 1 excludes citizens, residents and organisations of the Chinese Mainland, Taiwan, Hong Kong, the United States and Singapore. Our company is in Uzbekistan, but some of our clients may be residents of these jurisdictions. May reports containing TRONSCAN tags be delivered to such clients?
7. How should we describe the accuracy and update frequency of tags in our reports? Is there a disclaimer you would like us to include?
8. Whom should we contact for compliance questions, quota changes or to report an incorrect tag?

We would be glad to provide more details or a short demonstration. Thank you for considering our request.

Kind regards,

[Full name]
[Position], WHOMEVER LLC
[Address]
[E-mail] | [Phone] | [Website, if available]

---

## Источники (дата обращения — 2026-10-14)

- https://static.tronscan.org/pdf/TRONSCAN_Terms_of_Service.pdf — Terms of Service TRONSCAN («Last updated: January 4, 2022»), прочитан полностью
- https://docs.tronscan.org/llms.txt — указатель документации; страница `common-network-auth` (ключ, лимиты) вернула 403, её содержание известно только по выдаче поиска
- docs/stage-1-stack-proposal.md, G5 и раздел 1 — прежнее прочтение условий и пробы TronScan (Этап 1)
