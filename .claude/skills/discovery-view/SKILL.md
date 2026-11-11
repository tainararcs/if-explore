---
name: discovery-view
description: Implement or change the IF Explore AI discovery screen (route `/discover`, DiscoveryView.vue) — the visitor writes what they want to read and gets up to six titles from the campus collection chosen by Gemini, each with a short reason, with a rule-based fallback when the AI is unavailable. Also covers the entry point on the home. Data comes from `POST /api/discovery` (see the `ai-discovery-api` skill).
---

# Discovery view

Read `frontend/AGENTS.md`, `frontend/docs/project-guidelines.md`, and
`frontend/docs/design-guidelines.md` first. Foundations (tokens, Tailwind, i18n,
models, catalog parsers, preferences storage) are in the `welcome-view` skill;
cards and covers in `home-view` and `book-detail-view`. Reuse them, never
duplicate them.

## 1. Goal

"Interface de interação com a IA" from the schedule: a conversational-feeling
but single-turn request. The visitor types a need, sees suggestions with a
reason each, and opens a book page. It must be clear that suggestions come from
AI and only from the library collection.

## 2. Route and entry points

- Route `/discover`, lazy-loaded `features/discovery/views/DiscoveryView.vue`,
  `titleKey` "Peça uma sugestão". No preference guard: preferences are optional.
- Header (`AppHeader`, every view): the "Pergunte à IA" tab (✦ icon) next to
  "Para você" → `/discover`, marked as current there. On the home, the search
  text goes along (`/discover?q=`).
- No back link: `/discover` is a peer tab of the home, like it.

## 3. Layout

Full container width, like the home and the welcome view.

```
AppHeader (sticky, "Pergunte à IA" tab current)
Eyebrow "Descoberta com IA" + serif h1 "Peça uma sugestão" + lead
┌ aside (md+: 300–380px, sticky) ┐ ┌ results (rest of the width) ───────────────┐
│ form: textarea + counter,       │ │ idle (md+ only): dashed panel explaining    │
│   [x] preferences (if saved),   │ │   what appears there                        │
│   [ ✦ Sugerir leituras ]        │ │ loading: step messages + 4 skeleton cards   │
│ Pedidos recentes   [Limpar]     │ │ "Sugestões para “…”"        [Compartilhar]  │
│   ⟲ last requests (max 5)       │ │ AI message or rules notice                  │
│ Ideias para começar (chips)     │ │ result cards, one per row                   │
└─────────────────────────────────┘ │ [ ✦ Mostrar outras sugestões ]              │
                                    │ AI note                                     │
                                    └─────────────────────────────────────────────┘
```

- From `md`, the aside is sticky below the header and scrolls inside itself when
  taller than the screen. Below `md`, one column: aside, then results.
- Mobile: after a request the aside collapses into `DiscoveryQuerySummary`
  ("Seu pedido" + the text + "Editar"), so the results show right away; "Editar"
  reopens the form and focuses the textarea. From `md` the form never collapses.
- Recent requests repeat the request on click; idea chips fill the textarea
  (do not submit) and focus it.
- Enter submits, Shift+Enter breaks a line; the button is the primary action.

## 4. Result item — `DiscoveryResultItem.vue`

`<article>` card: `BookCover` (~88px) on the left; eyebrow with area name and
year; title (serif) as the `RouterLink` to `/books/:id`, stretched over the whole
card with `::after`; authors (`formatAuthors`); `AvailabilityBadge`; the reason
under "Por que esta leitura" (omitted without a reason); and, when the book has
a call number, "Na estante <callNumber>" with a "Copiar" button
(`useClipboardFeedback`) layered above the stretched link, so there is no control
inside a link.

## 5. States

- Idle: form, recent requests, and ideas; on `md+` the results column shows the
  dashed explanation panel.
- Loading (`DiscoveryLoading`): visual step messages every ~1.2s ("Lendo seu
  pedido…", "Procurando no acervo…", "Escolhendo as melhores leituras…",
  "Explicando cada escolha…", stopping at the last), one screen reader message,
  3 skeleton cards; results region `aria-busy`. A new submit cancels the previous
  request (`AbortController`).
- `source = "rules"` (of the latest batch): notice above the list
  (`role="status"`).
- Empty `items`: empty state with tips and a link to the home search.
- Error: message with retry (`role="alert"`); 429 gets its own text.
- "Mostrar outras sugestões" sends the same request with `excludeIds` (all books
  shown so far, up to 60) and appends the new batch; an empty batch shows "Não há
  outras sugestões no acervo para este pedido." and hides the button.
- "Compartilhar" (shared `ShareButton`, small) shares or copies the page link;
  `?q=` reproduces the request.
- After results arrive, move focus to the results heading.

## 6. Data

- `features/discovery/services/discovery-service.ts`: `discover(query, profile,
  excludeIds, signal?)` posts to `/discovery` and validates the body with the
  shared parsers; `source` is a literal union checked at runtime. A 429 becomes a
  typed `RateLimitedError`.
- `features/discovery/services/recent-requests-storage.ts`: last 5 requests in
  `localStorage` (`if-explore:discovery-recent`), deduplicated ignoring case,
  tolerant to blocked storage.
- `features/discovery/composables/useDiscovery.ts`: state as a discriminated
  union (`idle | loading | success | error`), `moreStatus` for extra batches,
  recent requests, cancellation, retry. The last result (with its extra batches)
  stays in memory, so coming back from a book shows it without a new request.
- Query synced to `?q=` with `router.replace`; a URL with `q` submits once on
  load, so shared links work. The profile comes from `useReadingPreferences`.
- Area names come from `getKnowledgeAreas` (cached); without them the card shows
  only the year.
- AI text is rendered with interpolation only (never `v-html`).

## 7. Structure

```
src/features/discovery/
├── views/DiscoveryView.vue
├── components/DiscoveryForm.vue          (textarea, counter, preference toggle; defineModel; exposes focus)
├── components/DiscoveryStarters.vue      (recent requests and idea chips)
├── components/DiscoveryQuerySummary.vue  (collapsed request on mobile)
├── components/DiscoveryLoading.vue       (step messages and skeletons)
├── components/DiscoveryResultItem.vue
├── composables/useDiscovery.ts
├── services/discovery-service.ts
├── services/recent-requests-storage.ts
└── models/discovery.ts
src/components/ShareButton.vue            (shared with the book page)
src/components/icons/IconHistory.vue
src/router/index.ts                       (/discover)
src/locales/pt-BR.ts                      (discovery.*, common.share.*)
```

## 8. Done when

- With the API key set, a request returns AI items with reasons; with it empty,
  the fallback notice and items appear; with the API down, the error state.
- Every item opens its book page; back returns to the discovery with the same
  results (`?q=`).
- Keyboard and screen reader flow: label → textarea → submit → recent requests →
  ideas → status → results → more; no horizontal scroll at 360px; at 1440px the
  aside and results fill the container; light and dark pass contrast.
- No hardcoded interface text; `npm run lint`, `npm run typecheck`, and
  `npm run build` pass.
