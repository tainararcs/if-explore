---
name: catalog-view
description: Implement or change the IF Explore full catalog (route `/catalog`, CatalogView.vue) — search and robust filters (type, availability, area, course, genre, language, publication year) over the whole collection, with counts per option, sort, and "Mostrar mais livros", all kept in the URL. Data comes from `GET /api/books` and `GET /api/books/facets` (`backend/`).
---

# Catalog view

Read `frontend/AGENTS.md`, `frontend/docs/project-guidelines.md`, and
`frontend/docs/design-guidelines.md` first. Reuse the shared foundations
(tokens, i18n, `catalog-service.ts`, `BookCard`, `SelectableChip`).

## 1. Goal

The second header tab, "Catálogo completo": every title of the collection,
without the rules of the recommendations. The visitor searches and narrows the
list with filters; book cards open the book page.

## 2. Layout

```
AppHeader (sticky): [BrandMark] IF Explore   [Para você] [Catálogo completo]   [☰ menu]
Eyebrow + serif h1 "Catálogo completo" + short lead
Search bar (max 640px)
Toolbar: [Filtros (n)] (below 900px) · "<n> livros" · Ordenar por [select]
Active filters: removable pills + "Limpar filtros"
md+: filters column (260px, sticky, scrolls on its own) | results grid
base: results grid; filters open in a full-height side <dialog>
```

- Grid: 2 columns at base, 3 at `sm`, 4 at `lg`; 24 books at a time with
  "Mostrar mais livros" (no infinite scroll: the footer stays reachable and
  coming back from a book keeps the place).
- Filters dialog (below 900px): native `<dialog>` with `showModal()`, title and
  close button on top, "Limpar filtros" and "Ver <n> resultados" at the bottom;
  a tap on the backdrop closes it.

## 3. Filters

| Filter | Query | Notes |
|---|---|---|
| Text | `q` | Debounced ~250ms |
| Type | `type` | Opens with book, e-book, audiobook, and thesis; periodicals are an option; `type=any` means all types. Equipment (keys, headphones, computer) never appears (API) |
| Availability | `available=1` | Only titles with a copy available for loan |
| Area, course, genre | `area`, `course`, `genre` | Multi-select (OR within a filter, AND between filters); courses grouped by level |
| Language | `language` | Options come from the counts (names as the catalog writes them) |
| Publication year | `yearFrom`, `yearTo` | Two number fields, applied on change; a reversed range is swapped |
| Sort | `sort` | Relevance (only with text), most copies (default without text), recently added, publication year, title |

- `GET /api/books/facets` returns how many books each option would bring,
  counted without the filter itself. Options show "Nome (n)"; options with zero
  books disappear unless selected. Counts load after the list (~450 ms), and the
  filters work without them.
- The URL is the source of truth (`catalog-filters.ts`: read, write, defaults):
  reload, back/forward, and coming back from a book keep everything.
  `router.replace` keeps the scroll position.
- The visitor's areas, when there are preferences, come first (`preferArea`).

## 4. Structure

```
src/features/catalog/
├── views/CatalogView.vue
├── models/catalog-filters.ts      (URL state, defaults, counts types)
├── services/facets-service.ts
├── composables/useCatalogBrowse.ts
└── components/
    ├── SearchBar.vue
    ├── CatalogFilters.vue
    ├── ActiveFilters.vue
    └── CatalogResults.vue
```

## 5. Done when

- Every filter, the sort, and "Mostrar mais livros" work, and the URL restores
  them; counts update with the other filters.
- Loading (skeleton grid), empty (with "Limpar busca e filtros"), and error
  (with retry) states work.
- No horizontal page scroll at 360px; the dialog works with keyboard (Escape
  closes it) and the filters column scrolls on its own at 1440px.
- No hardcoded interface text; `npm run lint`, `npm run typecheck`, and
  `npm run build` pass.
