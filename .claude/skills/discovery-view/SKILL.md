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
- Home: a secondary link below the search bar, "Peça uma sugestão à IA" →
  `/discover`; when the search has a query, pass it along (`/discover?q=`).
- Back link "← Suas recomendações" (or "← Início" without preferences), same
  rule as the book page.

## 3. Layout

```
AppHeader
[← Suas recomendações]
Serif h1: "Peça uma sugestão"
Lead: "Conte o que você procura e a IA escolhe títulos do acervo do campus."
┌ form ──────────────────────────────────────────┐
│ <label> O que você quer ler?                    │
│ [textarea, 3 rows, max 300]          120/300    │
│ Ideias: (chips) Algo leve para as férias ·      │
│   Introdução à programação · Clássicos ...      │
│ [x] Considerar minhas preferências (if saved)   │
│ [ Sugerir leituras ]                            │
└─────────────────────────────────────────────────┘
── results (aria-live="polite") ──
Message from the AI (when present), muted paragraph
List of up to 6 result items
Note: "Sugestões geradas por IA a partir do acervo. Confira os dados na página do livro."
```

- Max width ~720px, centered; results use the full content width at `md+`.
- Idea chips fill the textarea (do not submit); keyboard reachable.
- Enter submits, Shift+Enter breaks a line; the button is the primary action.

## 4. Result item — `DiscoveryResultItem.vue`

Horizontal card that is a `RouterLink` to `/books/:id` (accessible name = title):
`BookCover` (~88px) on the left; title (serif), authors (`formatAuthors`),
`AvailabilityBadge`; below, the reason under a small label "Por que esta
leitura". Without a reason (fallback), omit the label and the paragraph. Stack
vertically below `sm` only if the cover would squeeze the text.

## 5. States

- Idle: form only, ideas visible.
- Loading: submit shows progress, 3 skeleton items, results region `aria-busy`.
  A new submit cancels the previous request (`AbortController`).
- `source = "rules"`: notice above the list (`role="status"`): "A IA está
  indisponível agora; mostramos títulos do acervo ligados ao seu pedido."
- Empty `items`: empty state with tips (use other words, be less specific) and
  a link to the home search.
- Error: message with retry (`role="alert"`); 429 gets its own text ("Muitos
  pedidos em pouco tempo. Tente de novo em um minuto.").
- After results arrive, move focus to the results heading.

## 6. Data

- `features/discovery/services/discovery-service.ts`: `discover(query, profile?,
  signal?)` posts to `/discovery` and validates the body with the shared parsers
  (`parseBook`, `parseNullableString`, `parseRecord`, `list`); `source` is a
  literal union checked at runtime. A 429 becomes a typed `RateLimitedError`.
- `features/discovery/models/discovery.ts`: `DiscoveryResult` (`source`,
  `message`, `items: { book: Book; reason: string | null }[]`).
- `features/discovery/composables/useDiscovery.ts`: state as a discriminated
  union (`idle | loading | success | error`), cancellation, retry.
- Query synced to `?q=` with `router.replace`; a URL with `q` submits once on
  load, so shared links work. The profile comes from `useReadingPreferences`.
- AI text is rendered with interpolation only (never `v-html`).

## 7. Structure

```
src/features/discovery/
├── views/DiscoveryView.vue
├── components/DiscoveryForm.vue        (textarea, counter, ideas, preference toggle; defineModel)
├── components/DiscoveryResultItem.vue
├── composables/useDiscovery.ts
├── services/discovery-service.ts
└── models/discovery.ts
src/router/index.ts                     (/discover)
src/locales/pt-BR.ts                    (discovery.*)
src/features/home/views/HomeView.vue    (entry link)
```

## 8. Done when

- With the API key set, a request returns AI items with reasons; with it empty,
  the fallback notice and items appear; with the API down, the error state.
- Every item opens its book page; back returns to the discovery with the same
  results (`?q=`).
- Keyboard and screen reader flow: label → textarea → ideas → submit → status →
  results; no horizontal scroll at 360px; correct at 1440px; light and dark pass
  contrast.
- No hardcoded interface text; `npm run lint`, `npm run typecheck`, and
  `npm run build` pass.
