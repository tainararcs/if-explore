---
name: taste-onboarding-view
description: Implement or change the IF Explore taste onboarding (route `/onboarding`, TasteOnboardingView.vue) — the one-screen "Descobrir minhas leituras" flow where the visitor taps three titles on a wall of covers filterable by literary genre, optionally adds a campus course or study areas, and saves preferences before going to the home.
---

# Taste onboarding view

Read `frontend/AGENTS.md`, `frontend/docs/project-guidelines.md`, and
`frontend/docs/design-guidelines.md` first. Foundations (tokens, i18n, models,
catalog service, preferences storage) are described in the `welcome-view` skill;
reuse them, never duplicate them.

## 1. Goal

Pick books, not categories: one screen with a wall of covers, like the
Netflix/Pinterest taste pickers. Literary genres lead, as filters of the wall;
the academic profile (course and areas) stays available but optional and out
of the way. A visitor should finish in under a minute, with about 5 taps.

Modern, simple UX, but the UI stays within the project's visual standard: no
decorative icons or emojis, no slogans, plain copy.

## 2. The screen

- Title (serif, h1): "Escolha 3 livros que você leria". Helper: "Filtre por
  gênero para ver mais de cada estilo."
- Filter chips (`CandidateFilters.vue`): "Todos", each literary genre, then the
  areas the visitor chose. One active at a time. They scroll horizontally on
  mobile and wrap at `md`+.
  - "Todos" mixes every genre plus the chosen areas and courses.
  - A genre or an area shows only its titles.
  - All come from `getOnboardingCandidates` (`GET /api/recommendations/candidates`
    with `genre`, `area`, `course`). The API interleaves the groups, genres
    first, so every group appears near the top.
  - Each filter is fetched once and kept; changing areas or courses drops the
    stored "Todos" mix. A new request cancels the previous one.
- "Estuda no IF?" row below the filters: shows the chosen courses (or areas)
  or "Opcional: adicione seu curso", and opens `StudyDialog.vue`, a side
  `<dialog>` like the catalog filters, with an accent-insensitive course search,
  courses grouped by level (técnico integrado, técnico concomitante/subsequente,
  graduação, pós-graduação), and the knowledge areas. Selecting a course also
  selects its area; deselecting an area removes its selected courses.
- Wall of covers (`BookWall.vue`): cover, title, and author; 3 columns at base,
  4 at `sm`, 6 at `md`+. Shows 24 titles and "Mostrar mais livros" for the rest
  of the filter (up to 60).
  - Picked titles that are not in the visible part (from another filter or
    further down) come first, so they stay in view; picked titles already
    visible stay in place.
  - When 3 are picked, the other cards become `aria-disabled` and dimmed;
    deselecting one re-enables them. Never replace a pick silently.
  - Loading without titles shows cover skeletons; errors have a retry.
  - If a filter has fewer than 3 titles, the API completes the list with other
    titles.
- Sticky action bar: three dots and "Faltam N títulos" / "3 títulos escolhidos"
  (`aria-live`), and "Me recomende". The button stays enabled; tapping it before
  3 picks turns the hint red instead of saving.

## 3. Layout

Focus mode: `AppHeader` with `focus` (brand and menu, no tabs), and the route
meta `focusMode` hides the floating "back to top" button.

```
AppHeader focus: [BrandMark] IF Explore                    [☰ menu]
[← Voltar]
Title (serif, h1) · helper
[Todos] [Romance] [Aventura] …           ← scrolls sideways on mobile
[Estuda no IF? · Opcional: adicione seu curso   →]
Wall of covers                           ← scrolls
───────────────────────────────────────
Sticky action bar: ●○○ Faltam 2 títulos · [Me recomende]
```

## 4. State and persistence

- `useTasteOnboarding.ts` owns the draft (`areaIds`, `courseIds`,
  `seedBookIds`), the active filter, the stored candidates, and the final
  payload.
- Pre-fill from saved preferences (returning visitor, or "Ajustar preferências"
  in the header menu, which links to `/onboarding`). Saved seed books are loaded
  with `getBooksByIds`; ids that left the collection are dropped.
- Save only on "Me recomende", through `useReadingPreferences()`; abandoning the
  flow must not overwrite existing preferences.
- `genreIds` are not picked directly: `inferGenreIds` derives them from the
  genres of the 3 chosen titles, most frequent first.
- Preferences are complete with exactly 3 seed books (`isCompletePreferences`);
  genres, areas, and courses are optional. Count rules are pure functions in
  `models/onboarding-draft.ts`.

## 5. Structure

```
src/features/onboarding/
├── views/TasteOnboardingView.vue
├── composables/useTasteOnboarding.ts
├── models/onboarding-draft.ts       (draft, filters, pure rules)
├── services/onboarding-service.ts   (candidates from the API)
└── components/
    ├── CandidateFilters.vue
    ├── BookWall.vue
    ├── StudyDialog.vue
    └── OnboardingActionBar.vue
```

Shared pieces (`SelectableChip`, `BookCover`, icons) come from `src/components/`.

## 6. Done when

- Full flow works with keyboard only, including the dialog (Esc closes it).
- Exactly 3 books are enforced; preferences saved with the shape in design
  guidelines §10.3, with genres inferred from the books.
- One candidates request on load; switching back to a filter does not refetch.
- Works at 360px (sticky bar does not cover the last grid row) and at 1440px, in
  light and dark themes.
- No hardcoded interface text; `npm run lint`, `npm run typecheck`, and
  `npm run build` pass.
