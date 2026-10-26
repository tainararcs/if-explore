---
name: taste-onboarding-view
description: Implement or change the IF Explore taste onboarding (route `/onboarding`, TasteOnboardingView.vue) — the short "Descobrir minhas leituras" flow where the visitor picks study areas (optional campus courses), chooses three titles, optionally refines with literary genres, and saves preferences before going to the home.
---

# Taste onboarding view

Read `frontend/AGENTS.md`, `frontend/docs/project-guidelines.md`, and
`frontend/docs/design-guidelines.md` first. Foundations (tokens, i18n, models,
mock catalog, preferences storage) are described in the `welcome-view` skill;
reuse them, never duplicate them.

## 1. Goal

Netflix/Spotify-like taste picking: visual, fast, and inviting. Two mandatory
steps, one optional refinement. A visitor should finish in about a minute.

## 2. Steps

The current step lives in the route query (`?step=areas|books|genres`) so the
browser back button works. Invalid or unreachable steps (for example `books`
without an area) redirect to the first incomplete step with `router.replace`.

### Step 1 — `areas` (mandatory)

- Title (serif): "O que você estuda ou quer estudar?"
- Helper: "Escolha uma ou mais áreas."
- `fieldset` of `SelectableChip`s with the knowledge areas (multi-select, min 1).
  Each area chip can carry a small line icon.
- Below the areas, all campus courses are always listed as smaller chips,
  grouped by level (técnico integrado, técnico concomitante/subsequente,
  graduação, pós-graduação) under "Cursos do Campus Barbacena (opcional)".
  Selecting a course also selects its area; deselecting an area removes its
  selected courses.
- Continue enabled only with ≥ 1 area; otherwise show the reason next to the
  button.

### Step 2 — `books` (mandatory, exactly 3)

- Title: "Escolha três títulos que chamam sua atenção."
- Live counter: "1 de 3 escolhidos" (`aria-live="polite"`) with three dots/slots
  that fill as books are picked.
- Grid of selectable book cards (cover + title + author) from the selected areas,
  prioritizing books linked to selected courses. With more than one area, show
  area filter chips above the grid ("Todas" + each area).
- Grid: 3 columns at base, 4 at `sm`, 5–6 at `md`+.
- When 3 are selected, the remaining cards become `aria-disabled` and visually
  dimmed; deselecting one re-enables them. Do not silently replace a selection.
- If the selected area has fewer than 3 books, also show books from related
  areas so the step can always be completed.

### Finish (after step 2)

Two choices in the action bar:

- Primary: "Me recomende" → save and go to `/home`.
- Secondary: "Refinar com gêneros literários" → step 3.

### Step 3 — `genres` (optional refinement)

- Title: "E fora da sala de aula, o que você gosta de ler?"
- Multi-select chips with the literary genres; zero is allowed.
- Primary: "Me recomende" → save and go to `/home`. Ghost: "Voltar".

## 3. Layout

Focus mode: no app navigation, minimal header.

```
AppHeader: [BrandMark] IF Explore                 [theme toggle]
[← Voltar]  [progress bar]  "Passo 1 de 2"
Step title (serif, h1 — focus moves here on step change)
Helper text
Step content (chips / grid)            ← scrolls
───────────────────────────────────────
Sticky action bar: hint/counter · [Primary]   (safe-area aware)
```

- Progress: segmented bar with 2 segments (areas, books) plus a third dashed
  segment only when the refinement is open; also text "Passo 1 de 2" for
  screen readers and users who do not read the bar.
- Content column max 720px for chips; the book grid may use up to 1200px.
- At `md`+, the action bar can stay sticky at the bottom of the content column
  instead of the viewport, with the primary button auto-width aligned right.
- Step transitions: fade + 12px horizontal slide in the navigation direction,
  only with `prefers-reduced-motion: no-preference`.

## 4. State and persistence

- Keep draft selections in a feature composable (`useTasteOnboarding.ts`) that
  owns the step logic, validation (`canContinue`), and the final payload.
- Pre-fill the draft from saved preferences when they exist (returning visitor,
  or "Ajustar preferências" from the home, which links to `?step=areas`).
- Save only on "Me recomende", through `useReadingPreferences()`; abandoning the
  flow must not overwrite existing preferences.
- Validation of counts (≥ 1 area, exactly 3 books) is a pure function, testable
  without Vue.

## 5. Structure

```
src/features/onboarding/
├── views/TasteOnboardingView.vue
├── composables/useTasteOnboarding.ts
└── components/
    ├── OnboardingProgress.vue
    ├── AreaStep.vue
    ├── BookPickStep.vue
    ├── GenreStep.vue
    └── OnboardingActionBar.vue
```

Shared pieces (`SelectableChip`, `BookCover`, icons) come from `src/components/`.

## 6. Done when

- Full flow works with keyboard only, focus moving to each step heading.
- Back button and page reload keep a coherent step (draft may reset on reload,
  but the URL must never show an impossible step).
- Exactly 3 books are enforced; genres optional; preferences saved with the
  shape in design guidelines §10.3.
- Works at 360px (sticky bar does not cover the last grid row) and at 1440px, in
  light and dark themes.
- No hardcoded interface text; `npm run lint`, `npm run typecheck`, and
  `npm run build` pass.
