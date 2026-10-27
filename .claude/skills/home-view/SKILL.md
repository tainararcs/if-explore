---
name: home-view
description: Implement or change the IF Explore homepage (route `/home`, HomeView.vue) — search bar plus personalized recommendation shelves built from saved reading preferences, switching to a results grid while searching. Uses mocked catalog and recommendation services only.
---

# Home view

Read `frontend/AGENTS.md`, `frontend/docs/project-guidelines.md`, and
`frontend/docs/design-guidelines.md` first. Foundations (tokens, i18n, models,
mock catalog, preferences storage) are described in the `welcome-view` skill;
reuse them, never duplicate them.

## 1. Goal

Simple, intuitive discovery: search the (mock) catalog and browse personalized
shelves, Play Books/Netflix style. Book cards are **not clickable** at this stage.

## 2. Access

Route guard: without valid preferences, redirect to `/`. Replace the current
placeholder `HomeView.vue`.

## 3. Layout

```
AppHeader (sticky): [BrandMark] IF Explore            [✦ Ajustar preferências]
Greeting eyebrow + serif h1: "Suas recomendações"
Short line: "Com base em <área 1>, <área 2> e nos títulos que você escolheu."
Search bar (full width at base, max 640px at md+)
Area filter chips (horizontal scroll at base): Todas · <selected areas>
── default mode ──
Shelf: "Escolhidos para você"
Shelf: "Porque você escolheu <título>"   (one per seed book, max 3)
Shelf: "Mais de <área>"                  (one per selected area)
Shelf: "Para ler por prazer: <gênero>"   (only if genres were refined)
── search mode (query not empty) ──
"<n> resultados para “<query>”" + results grid
```

- The ✦ action is an icon button with `aria-label="Ajustar preferências"` linking
  to `/onboarding?step=areas` (pre-filled).
- Area filter chips narrow every shelf and the results; "Todas" is the default.
- Do not show shelves that end up empty after filtering.

## 4. Shelves

- Section with a serif `h2`. Horizontal list (`<ul>`) with `overflow-x: auto`,
  `scroll-snap-type: x mandatory`, and the scrollbar always hidden.
- Base: free touch scroll, item width ~132px, gap `--space-4`. The scroll region
  bleeds to the viewport edge (padding equals the gutter) so the next card
  peeks, signaling scroll.
- From 900px: paged carousel. Each page fills the visible width with N books
  (at least 2, cards ≥ 150px, gap `--space-5`); previous/next icon buttons move
  one page, and dot pagination below shows and selects the current page
  (`aria-current`, accessible "Página X de Y" labels). A shelf that fits in one
  page is centered and shows no arrows or dots.
- Each item is a non-interactive book card: cover, title, author, availability
  badge. The "Escolhidos para você" shelf may show the book's `quote` in italic
  serif under the card at `md`+ (wireframe idea), clamped to 3 lines.

## 5. Search

- Searches title, authors, and subjects of the whole mock catalog,
  case- and accent-insensitive (`normalize('NFD')`), debounced ~250ms.
- Query synced to the URL (`?q=`) with `router.replace`, so reload keeps it.
- Results grid: 2 columns at base, 3 at `sm`, 5 at `md`, 6 at `lg`; results
  matching the visitor's areas rank first.
- Empty result: empty state with a suggestion to check spelling or clear the
  filter, plus a "Limpar busca" action.

## 6. Data

- Recommendation logic is a mocked service in
  `src/features/home/services/recommendation-service.ts` (async, artificial
  delay), standing in for the future AI backend. Scoring is a pure function:
  course match > area match > genre match > shared subjects with seed books;
  never recommend the seed books themselves in "Escolhidos para você".
- A feature composable (`useHomeRecommendations.ts`) exposes shelves and
  loading/error state; search uses `catalog-service.ts`.
- States: skeleton shelves while loading, error with retry (`role="alert"`).

## 7. Structure

```
src/features/home/
├── views/HomeView.vue
├── services/recommendation-service.ts
├── composables/useHomeRecommendations.ts
├── composables/useCatalogSearch.ts
└── components/
    ├── BookShelf.vue
    ├── BookCard.vue          (move to src/components/ only if reused)
    ├── SearchBar.vue
    └── SearchResults.vue
```

## 8. Done when

- Shelves reflect the saved areas, courses, seed books, and genres.
- Search, filter, and empty/loading/error states work; `?q=` survives reload.
- Shelves are keyboard reachable; no horizontal page scroll at 360px; correct at
  1440px; light and dark themes pass contrast.
- No hardcoded interface text; `npm run lint`, `npm run typecheck`, and
  `npm run build` pass.
