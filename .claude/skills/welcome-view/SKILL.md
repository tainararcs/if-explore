---
name: welcome-view
description: Implement or change the IF Explore welcome view (route `/`, WelcomeView.vue) — the entry screen that introduces the project and starts the "Descobrir minhas leituras" flow or sends returning visitors to their recommendations. Also covers the one-time frontend foundations (design tokens, fonts, i18n, shared preferences storage) when they do not exist yet.
---

# Welcome view

Read `frontend/AGENTS.md`, `frontend/docs/project-guidelines.md`, and
`frontend/docs/design-guidelines.md` first. This skill only adds what is specific
to the welcome view; never contradict those documents.

## 1. Foundations (do once, check before creating)

The welcome view is the first view implemented. If any of these is missing,
create it before the view, following `design-guidelines.md`:

1. Tokens, `@font-face`, base element styles, `.container`, `.button*`, and
   `:focus-visible` rules in `src/index.css` (light + dark).
2. Self-hosted fonts in `public/fonts/` (Libre Caslon Text 400/400i/700, Inter
   variable). Download the `.woff2` files only with the user's permission and
   state each file's source; keep their licenses (OFL) next to them.
3. `vue-i18n` configured in `src/lib/i18n.ts` with `src/locales/pt-BR.ts`,
   registered in `main.ts`; `lang="pt-BR"` and title "IF Explore" in `index.html`.
4. Shared models, mock catalog, `preferences-storage.ts`, and
   `useReadingPreferences.ts` (design guidelines §10).
5. Routes from design guidelines §11, replacing the current `/` → `/home`
   redirect, with a per-route document title.
6. `BrandMark.vue` and `AppHeader.vue` in `src/components/`.

## 2. Goal

In under ten seconds the visitor should understand what IF Explore is and want
to start. One primary action, nothing else competing for attention.

## 3. Content (pt-BR, in i18n resources under `welcome.*`)

- Eyebrow: "BIBLIOTECA ROBERVAL CARDOSO · IF SUDESTE MG – BARBACENA".
- Title (display serif, with one italic word for emphasis), for example:
  "Sua próxima leitura já está *na estante* do campus."
- Lead (1–2 sentences): the app suggests books from the campus library based on
  your study area and taste; it takes about a minute and needs no login.
- "Como funciona" — three short numbered items:
  1. Escolha suas áreas de estudo.
  2. Marque três títulos que chamam sua atenção.
  3. Receba recomendações do acervo.
- Privacy note (small, muted): preferences stay only in this browser.
- Footer: link "Acessar o site oficial da biblioteca" (official URL from the
  design guidelines, `target="_blank"`, `rel="noopener noreferrer"`, with an
  external-link indication for screen readers).

## 4. Actions and states

Use `useReadingPreferences()` to decide the state; do not read `localStorage`
directly in the view.

| State | Primary | Secondary |
|---|---|---|
| No saved preferences | "Descobrir minhas leituras" → `/onboarding` | — |
| Saved preferences | "Ver minhas recomendações" → `/home` | "Refazer minhas escolhas" → `/onboarding` (answers pre-filled) |

Render actions as `RouterLink` with `.button` classes. The primary button has a
trailing arrow icon.

## 5. Layout

Mobile (base):

```
[BrandMark] IF Explore              (static header, no actions)
EYEBROW
Display title (2–4 lines)
Lead paragraph
[ Primary button — full width ]
[ Secondary button — full width ]   (only with saved preferences)
Privacy note
Hero: fan of 3–5 generated BookCovers, slightly rotated and overlapping
Como funciona (3 items, stacked)
Footer link to the official library
```

`md`+ (≥ 900px): two-column hero inside `.container`; text column (max ~560px)
on the left, cover fan on the right, vertically centered, hero filling roughly
`min(100dvh - header, 720px)`. "Como funciona" becomes three columns below.
Buttons become auto-width and inline.

Visual details:

- Paper background (`--color-bg`) with a subtle large serif ornament or thin
  horizontal rule under the eyebrow (as in the moodboard), no stock photos.
- Cover fan uses real mock books (pick by fixed ids for a stable composition),
  decorative (`aria-hidden`), with a soft `--shadow-md`; on hover/reduced-motion
  rules from the guidelines, the fan may spread a few degrees.
- Staggered fade-in of title → lead → actions (≤ 400ms total), only under
  `prefers-reduced-motion: no-preference`.

## 6. Structure

```
src/features/welcome/
├── views/WelcomeView.vue
└── components/
    ├── WelcomeCoverFan.vue     (only if the fan markup is non-trivial)
    └── WelcomeHowItWorks.vue   (only if it improves readability)
```

## 7. Done when

- Both states render correctly (test by clearing and seeding the storage key).
- Works at 360px without horizontal scroll, and at 1440px.
- Light and dark themes pass contrast; keyboard order is title → actions →
  footer link; focus is visible.
- No hardcoded interface text; `npm run lint`, `npm run typecheck`, and
  `npm run build` pass.
