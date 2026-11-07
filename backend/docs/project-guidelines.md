# Backend Project Guidelines

## 1. Purpose and current state

The backend serves the IF Explore frontend. The library catalog (PHL Elysio, a
campus CGI without an API) is read by `phl_client`, copied into SQLite by the
sync commands, classified into the IF Explore taxonomy, and exposed by a
read-only JSON API built with Django Ninja. The Django admin is where the
library curates the taxonomy.

`AGENTS.md` contains the operational instructions. This document is the source
for technical organization and responsibility conventions. Setup, commands,
environment variables, and the endpoint reference live in `README.md`.

## 2. Directory structure

```text
backend/
├── config/            # settings (from environment variables) and URLs (admin, /api/)
├── catalog/           # the collection: models, services, API, admin, commands
│   ├── services/      # business rules
│   ├── management/commands/
│   ├── migrations/
│   └── tests/
└── phl_client/        # PHL catalog client, standard library only
    └── tests/fixtures/  # real OPAC pages used by the tests
```

| Location | Responsibility |
|---|---|
| `phl_client/` | Talk to the PHL catalog and turn its pages into typed data. Knows nothing about Django. |
| `catalog/models.py` | Entities, constraints, and indexes. The ORM is the data access layer. |
| `catalog/services/` | Rules: sync, classification, copy status, search, recommendations, live availability, AI discovery. |
| `catalog/api.py` | Routes: validate parameters, call a service, convert to schemas. |
| `catalog/schemas.py` | The JSON contract with the frontend. |
| `catalog/admin.py` | Curation of the taxonomy; synced data is read-only. |
| `catalog/management/commands/` | Thin wrappers that call a service and report the result. |
| `config/` | Settings and URL wiring only. |

Create a new Django app only for a separate domain, not for a new feature of the
collection.

## 3. `phl_client`

- Standard library only, no Django imports: it must stay usable from a plain
  script.
- Modules depend only on earlier ones: `errors` → `fields` → `text`, `isbn`,
  `query` (pure) → `parsers` (pure, no network) → `transport` (HTTP, session,
  cache, pause) → `client` (`PhlClient`, low-level searches) → `models` (`Book`,
  `Copy`, `SearchResult`) → `library` (`Library`, the facade).
- The PHL only understands ISO-8859-1 and needs a session id; `transport`
  handles both. Do not build catalog URLs elsewhere.
- Record field names are English (`FIELDS` in `fields.py`). To read a new
  catalog field: map its tag in `FIELDS`, expose it in `Book.from_record`, and
  cover it with a fixture test.
- Parsers are tested with real OPAC pages saved in `tests/fixtures/`. Save new
  pages from the live catalog; anonymize any borrower data before committing.
- `phl_client/api.html` documents the public API of the package; update it when
  that API changes.

## 4. Models and data

- `Book.id` is the PHL title id (field 002), used in frontend URLs. Never
  renumber it.
- Synced fields mirror the catalog and are overwritten by every snapshot; the
  original record is kept in `Book.raw` so data can be reprocessed without
  downloading again.
- Titles that leave the catalog become `is_active=False` instead of being
  deleted, so saved preferences that point to them do not break. Queries for the
  frontend always filter active books.
- `Author` and `Subject` are unique by normalized name (no accents, lowercase),
  so spelling variants merge.
- The taxonomy (`KnowledgeArea`, `Course`, `LiteraryGenre`) is curated in the
  admin. Its derived relations (`Book.area`, `courses`, `genres`) are computed
  during the catalog sync by `catalog/services/classification.py`, so taxonomy
  changes apply on the next sync. Course codes inferred from the catalog stay
  `mapping_confirmed=False` until the library confirms them.
- The FTS5 search index (`catalog_book_fts`) has no model: it is created by a
  raw SQL migration and rebuilt by `catalog/services/search_index.py`.
- Initial taxonomy comes from a data migration; later changes go through the
  admin or new migrations, never edits to an applied one.

## 5. Sync with the PHL catalog

- `sync_catalog` runs every 6 hours. It downloads the whole collection and the
  copy status summary in a few large requests and applies them in one
  transaction: upsert books and their copy status, rebuild relations, deactivate
  missing titles, and rebuild the search index. The API keeps reading the
  previous version until it commits. If any download fails, nothing is applied.
- A snapshot much smaller than the active collection is refused
  (`CATALOG_SYNC_MIN_RATIO`): it is treated as a truncated response.
- The copy status comes from the OPAC `decorado` format
  (`PhlClient.copy_statuses`): per title, the total and which statuses are
  present, not how many copies are free. That format ignores pagination and the
  server cuts it on some broken records, so it is split by title id prefix
  (`STATUS_TITLE_PREFIXES`) and works around broken records at a bounded cost.
- In that format a borrowed or reserved copy still shows as available, so the
  title status (`CopyStatus`) is derived by `catalog/services/copy_status.py`:
  "available" only without loans or reservations, otherwise `uncertain` when it
  cannot tell. The frontend shows `copies.status` and never interprets raw
  statuses.
- The batch writes only `COPY_BATCH_FIELDS`. The exact free count and loans
  (`copies_available`, `loans_total`) come only from the live check and must
  never be overwritten by the sync; the API shows the free count only when the
  live check is the most recent reading.
- Popularity is the number of copies (`copies_total`), known for every title;
  loans are only known for titles someone opened.
- The book page refreshes its copies live from the PHL (1 request) when the last
  live check is older than `COPIES_LIVE_MAX_AGE_MINUTES`; a PHL failure keeps the
  stored data instead of failing the page.
- Every sync run is recorded in `SyncRun`, and two runs of the same kind never
  overlap.
- Count the PHL requests of any new sync step. Steps that grow with the size of
  the collection, one request per title, are not acceptable for scheduled runs.

## 6. Services

- Services hold the rules and are called by routes, commands, and the admin.
- Prefer plain functions. Keep database-free rules pure and typed with small
  dataclasses (`CourseRule`, `GenreRule`) so they are tested without the
  database.
- Ranking (search relevance, related books, recommendation shelves, onboarding
  candidates) happens in the services, never in the frontend.
- Only recommendable document types (books, e-books, audiobooks, theses) enter
  recommendations and related shelves.
- Raw SQL is acceptable where the ORM cannot express the query well (FTS5,
  affinity scoring); always pass values as parameters and take table names from
  `Model._meta.db_table`.
- AI (Gemini) lives in `catalog/services/gemini.py` (REST client, standard
  library only, raises only `GeminiError`) and `catalog/services/discovery.py`
  (rules). The model only ranks and explains candidates selected from the local
  collection; ids outside them are discarded, and any failure falls back to the
  rule-based selection, so AI errors never become 5xx. Send only catalog data and
  the visitor's request text, never preferences or identifiers; do not log
  prompts. State the Gemini calls a change adds, like PHL requests.
- Generated text that is expensive to repeat is cached in its own model
  (`BookExplanation`), keyed by a hash of the data sent, never in synced fields.

## 7. API contract

- Routes live in `catalog/api.py` on a Django Ninja `Router` mounted at `/api/`,
  with `by_alias=True`. Interactive docs are at `/api/docs`.
- Schemas extend `CamelSchema`: fields are declared in `snake_case` and sent in
  `camelCase`. Missing values are `null`, never empty strings.
- Lists are paginated as `{items, total, page, pageSize}`. Query-string lists
  use repeated keys (`?area=a&area=b`).
- Errors use `HttpError` with a Portuguese message: 404 for missing or inactive
  books, 422 for invalid parameters (Ninja validation).
- Reading endpoints are `GET`; `POST` is used only when the input needs a body
  and nothing the visitor sends is stored (`/api/recommendations`,
  `/api/discovery`). Routes that call Gemini are throttled per IP and answer
  429 above the limit.
- The frontend mirrors the contract in `frontend/src/models/book.ts` and
  validates responses in `frontend/src/services/catalog-parsers.ts`. Changing a
  schema means updating those files, the API tests, and the endpoint tables in
  `README.md` in the same change.

## 8. Testing

- `python manage.py test` runs both `phl_client` and `catalog` tests. Tests
  never access the network.
- `phl_client` tests use saved pages from `phl_client/tests/fixtures/`.
- `catalog` tests build the collection from those pages with `apply_snapshot`
  and replace the PHL with `FakeLibrary` (`catalog/tests/test_sync.py`). API
  tests patch `catalog.services.availability.live_library`; AI tests patch
  `catalog.services.gemini.client` with `FakeGemini` (`catalog/tests/test_discovery.py`).
- Test observable behavior: stored data, API responses, and the requests made
  to the fake library. Add a regression test for every bug fix.

## 9. Performance

- Measure before optimizing and report the numbers. Current reference on the
  real collection (~20k titles): search 10–190 ms, related books ~75 ms, home
  recommendations ~0.4 s, full catalog sync with copy status ~85 s.
- SQLite runs in WAL mode so the sync can write while the API reads; keep write
  transactions short outside the snapshot.
