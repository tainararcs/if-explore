---
name: home-view
description: Implement or change the IF Explore homepage (route `/home`, HomeView.vue) — search bar plus personalized recommendation shelves built from saved reading preferences, switching to a results grid while searching. Search and shelves come from the project API (`backend/`).
---

# Home view

Read `frontend/AGENTS.md`, `frontend/docs/project-guidelines.md`, and
`frontend/docs/design-guidelines.md` first. Foundations (tokens, i18n, models,
catalog service, preferences storage) are described in the `welcome-view` skill;
reuse them, never duplicate them.

## 1. Goal

Simple, intuitive discovery: search the library collection and browse personalized
shelves, Play Books/Netflix style. Book cards open the book page (`/books/:id`).

## 2. Access

Route guard: without valid preferences, redirect to `/`. Replace the current
placeholder `HomeView.vue`.

## 3. Layout

```
AppHeader (sticky): [BrandMark] IF Explore            [✦ Ajustar preferências]
Greeting eyebrow + serif h1: "Suas recomendações"
Short line: "Com base em <área 1>, <área 2> e nos títulos que você escolheu."
Search bar (full width at base, max 640px at md+)
[✦ Peça uma sugestão à IA]   (link to /discover, carries ?q= when searching)
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
- "Escolhidos para você" on mobile only (below 900px): one featured book at a
  time, centered (`scroll-snap-align: center`, ~62vw wide), with the previous
  and next books peeking at the edges, plus one dot per book. Neighbors are always
  scaled to ~0.88 with faded covers only (text keeps its contrast), including
  with reduced motion. With motion allowed, the change transitions, and where
  supported a scroll-driven animation (`animation-timeline: view(inline)`)
  makes it follow the finger. Other shelves keep the free scroll on mobile.
- Each item is a book card linking to the book page: cover (catalog image, or the
  generated one when missing), title, authors (`formatAuthors`), and availability
  badge (label from `copies.status`; "Consulte na biblioteca" while `copies` is `null`).

## 5. Search

- Searches the whole collection through `searchBooks` (`GET /api/books?q=`):
  title, authors, subjects, and synopsis, case- and accent-insensitive, ranked by
  relevance with the visitor's areas first (`preferArea`). Debounced ~250ms; a
  new query cancels the previous request.
- The area filter applies to the search on the API (`area`) and to the shelves
  locally.
- Query synced to the URL (`?q=`) with `router.replace`, so reload keeps it.
- Results grid: 2 columns at base, 3 at `sm`, 5 at `md`, 6 at `lg`. 24 results at
  a time with a "Mostrar mais livros" button; the heading shows the total found.
- Empty result: empty state with a suggestion to check spelling or clear the
  filter, plus a "Limpar busca" action.

## 6. Data

- `src/features/home/services/recommendation-service.ts` posts the saved
  preferences to `POST /api/recommendations` and validates the shelves it gets
  back. Ranking happens in the API over the whole collection (course > area >
  genre > shared subjects with the seed books; seed books never come back), and
  only shelves with at least 3 books are returned.
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
└── components/            (BookShelf and BookCard are shared, in src/components/)
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
