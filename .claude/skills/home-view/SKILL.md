---
name: home-view
description: Implement or change the IF Explore homepage (route `/home`, HomeView.vue) — personalized recommendation shelves built from saved reading preferences, with an AI shelf at the top that the visitor requests with one button (books plus the reason for each). Shelves and AI suggestions come from the project API (`backend/`). Search lives in the catalog (`catalog-view` skill).
---

# Home view

Read `frontend/AGENTS.md`, `frontend/docs/project-guidelines.md`, and
`frontend/docs/design-guidelines.md` first. Foundations (tokens, i18n, models,
catalog service, preferences storage) are described in the `welcome-view` skill;
reuse them, never duplicate them.

## 1. Goal

Simple, intuitive discovery: browse personalized shelves, Play Books/Netflix
style, and ask the AI for a few more picks with the reason for each. Book cards open the book page (`/books/:id`).

## 2. Access

Route guard: without valid preferences, redirect to `/`. Replace the current
placeholder `HomeView.vue`.

## 3. Layout

```
AppHeader (sticky): [BrandMark] IF Explore   [Para você] [Catálogo completo]   [☰ menu]
Greeting eyebrow + serif h1: "Suas recomendações"
Short line: "Com base em <área 1>, <área 2> e nos títulos que você escolheu."
Area filter chips (horizontal scroll at base): Todas · <selected areas>
AI shelf: "Sugestões da IA"                  (button first; then books with reasons)
Shelf: "Escolhidos para você"
Shelf: "Parecidos com os que você escolheu"  (the seed books' similar titles, interleaved)
Shelf: "Dos seus gêneros"                    (chosen genres interleaved, only with 2+ genres)
Shelf: "Mais de <área>"                      (one per selected area)
Shelf: "<gênero>"                            (one per chosen genre)
[Ver outras sugestões]                       (new shuffle seed, back to the top)
```

- "Catálogo completo" is a header tab to `/catalog` (see the `catalog-view`
  skill), where the search and the filters live.
- Preferences are adjusted from the header menu ("Ajustar preferências",
  `/onboarding?step=areas`, pre-filled) or from the welcome view; the home has
  no link of its own.
- Area filter chips narrow every shelf, the AI shelf included; "Todas" is the default.
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

## 5. AI shelf ("Sugestões da IA")

- Featured panel at the top, before the shelves. Before any request it shows a
  short invitation, the primary button "Pedir sugestões à IA", and a note on
  what is sent (the anonymous profile only).
- The button posts the saved preferences to `POST /api/recommendations/ai`
  (`ai-suggestions-service.ts`) with `excludeIds`: the books already suggested in
  the session and the ones in "Escolhidos para você" (at most 60). The answer is
  exactly 3 books, each with the AI's reason (a book the API added to complete
  the 3 comes without one), shown as `AiSuggestionCard` (cover, area and year,
  title link, availability, reason, call number with copy). Cards scroll
  horizontally below 900px and form a 3-column grid from there.
- Then the button becomes "Outras sugestões". `source: "rules"` (AI down) does
  not add a shelf, because it would repeat the rule-based shelves: show a short
  notice instead. Empty answer and 429 also become short notices.
- The shelf is kept in `sessionStorage` (`ai-suggestions-storage.ts`, ids and
  reasons, keyed by the profile): coming back to the home reloads the books (1
  request) without a new Gemini call. Changing preferences discards it.
- The area filter chips also narrow the AI shelf.

## 6. Data

- `src/features/home/services/recommendation-service.ts` posts the saved
  preferences to `POST /api/recommendations` and validates the shelves it gets
  back. Ranking happens in the API over the whole collection (course > area >
  genre > shared subjects with the seed books; seed books never come back), each
  book appears in one shelf only (the first that shows it), and only shelves with
  at least 3 books are returned.
- The request carries a `shuffleSeed` kept in `sessionStorage`
  (`shuffle-seed-storage.ts`): each shelf draws from its best ~40 candidates,
  weighted by score. The same seed gives the same shelves, so coming back from a
  book page keeps them; a new visit or "Ver outras sugestões" draws a new seed.
- Feature composables expose the state: `useHomeRecommendations.ts` (shelves)
  and `useAiSuggestions.ts` (AI shelf).
- States: skeleton shelves while loading, error with retry (`role="alert"`).

## 7. Structure

```
src/features/home/
├── views/HomeView.vue
├── services/recommendation-service.ts
├── models/ai-suggestions.ts
├── services/ai-suggestions-service.ts · ai-suggestions-storage.ts · shuffle-seed-storage.ts
├── composables/useHomeRecommendations.ts · useAiSuggestions.ts
└── components/            (BookShelf and BookCard are shared, in src/components/)
    ├── AiSuggestionShelf.vue
    └── AiSuggestionCard.vue
```

## 8. Done when

- Shelves reflect the saved areas, courses, seed books, and genres.
- Filter and empty/loading/error states work; the AI shelf survives a reload
  without a new Gemini call.
- Shelves are keyboard reachable; no horizontal page scroll at 360px; correct at
  1440px; light and dark themes pass contrast.
- No hardcoded interface text; `npm run lint`, `npm run typecheck`, and
  `npm run build` pass.
