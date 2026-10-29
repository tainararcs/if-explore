# Design Guidelines

Visual identity, layout, and interaction rules shared by every view of
**IF Explore**. `docs/project-guidelines.md` governs code organization; this file
governs how the interface looks and behaves. View-specific decisions live in the
skills under `.claude/skills/` at the repository root.

## 1. Product and principles

IF Explore modernizes the discovery of books from the Biblioteca Roberval Cardoso
(IF Sudeste MG – Campus Barbacena) and recommends readings from a short taste
onboarding. It does **not** reimplement the library system: loans, reservations,
and full records stay on the official site. At this stage all data is mocked;
the app must make no request to the real catalog.

There is no authentication. Preferences are stored only in the visitor's browser.

Principles:

1. **Classic interface, modern experience.** Paper, serif typography, and
   institutional greens; fluid, fast, touch-friendly interactions.
2. **Mobile first.** Design and write CSS for ~360px first, then enhance with
   `min-width` media queries.
3. **Few steps, clear choices.** Every screen has one primary action.
4. **Content first.** Book covers and titles carry the interface; chrome stays
   quiet.
5. **Accessible by default.** WCAG 2.2 AA contrast, keyboard navigation, visible
   focus, and reduced-motion support.

## 2. Brand

| Item | Value |
|---|---|
| Product name | IF Explore |
| Recommendation flow name | Descobrir minhas leituras |
| Institutional subtitle | Biblioteca Roberval Cardoso · IF Sudeste MG – Campus Barbacena |
| Official library site | `https://biblioteca.barbacena.ifsudestemg.edu.br/cgi-bin/wxis.exe?IsisScript=phl82.xis&cipar=phl82.cip&lang=por` |

The brand mark is a grid of rounded squares in the institutional green with one
red circle at the top-left, a reference to the Instituto Federal mark (see the
wireframes). Implement it as an inline SVG component (`BrandMark.vue`) with an
accessible name only when it is not accompanied by the text "IF Explore".
The red (`--color-brand-accent`) appears only in the brand mark.

Voice (pt-BR): warm, direct, and inviting; address the reader as "você"; avoid
jargon such as "onboarding" or "algoritmo" in the interface. Prefer gender-neutral
phrasing ("Boas-vindas", not "Bem-vindo").

## 3. Color

All colors are CSS custom properties defined in `src/index.css`: the palette on
`:root` and the semantic tokens in the Tailwind `@theme static` block, which also
exposes them as utilities (`bg-surface`, `text-primary`, `border-border`).
Components use **semantic tokens only**; raw palette values appear only in the
token definitions.

### 3.1 Palette (from the moodboard)

| Token | Hex | Name |
|---|---|---|
| `--palette-green-900` | `#174D3B` | Verde institucional |
| `--palette-green-700` | `#356B56` | Verde musgo |
| `--palette-green-300` | `#91A99B` | Verde sálvia |
| `--palette-paper` | `#F6F2E9` | Creme papel |
| `--palette-sand` | `#DED4C3` | Areia |
| `--palette-charcoal` | `#242722` | Carvão |
| `--palette-red` | `#C8191E` | Brand mark only |

### 3.2 Semantic tokens

| Semantic token | Light | Dark | Use |
|---|---|---|---|
| `--color-bg` | `#F6F2E9` | `#1A1D19` | Page background |
| `--color-surface` | `#FBF8F2` | `#242722` | Cards, sheets, header |
| `--color-surface-muted` | `#EEE8DC` | `#2D312B` | Inputs, skeletons, unselected chips |
| `--color-border` | `#DED4C3` | `#4D544A` | Dividers, outlines |
| `--color-border-strong` | `#DED4C3` | `#737B6D` | Form field outlines (3:1 on surface in dark) |
| `--color-chip-border` | transparent | `#4D544A` | Unselected chip outline |
| `--color-text` | `#242722` | `#F0EBE0` | Primary text |
| `--color-text-muted` | `#5B6158` | `#B4B9AE` | Secondary text, metadata |
| `--color-primary` | `#174D3B` | `#6CC196` | Primary buttons, selected states, links |
| `--color-primary-hover` | `#356B56` | `#7FCCA3` | Hover/active of primary |
| `--color-on-primary` | `#FBF8F2` | `#0F1D16` | Text/icons over primary |
| `--color-primary-soft` | `#DCE6DF` | `#2B4A3B` | Selected chip background, highlights |
| `--color-on-primary-soft` | `#174D3B` | `#9CDCBA` | Text/icons over primary-soft |
| `--color-focus` | `#356B56` | `#6CC196` | Focus ring |
| `--color-success` | `#2F6B47` | `#8FCBA5` | "Disponível" |
| `--color-warning` | `#8A4B1F` | `#E0A878` | "Emprestado" |
| `--color-danger` | `#A3262A` | `#F08C8C` | Errors |
| `--color-brand-accent` | `#C8191E` | `#E0484C` | Brand mark circle only |

Each semantic token is declared once with `light-dark(<light>, <dark>)`. By
default the theme follows `prefers-color-scheme`; the header toggle
(`ThemeToggle.vue`, `useColorTheme()`) stores the visitor's choice in
`localStorage` (`if-explore:theme`) and sets `data-theme="light|dark"` on
`<html>`, which forces `color-scheme`. An inline script in `index.html` applies
the stored choice before rendering to avoid a flash. Check every new
token pair for at least 4.5:1 contrast (3:1 for large text and UI outlines).

### 3.3 Cover colors

Generated covers (section 7.4) use a fixed set of deep tones so the shelf feels
like a classic library. They are decorative, so the same values serve both
themes:

`#174D3B` green · `#356B56` moss · `#2E5A6B` petrol · `#6E2F3A` wine ·
`#8A4B1F` terracotta · `#3E3A5C` indigo · `#5C5A2E` olive · `#242722` charcoal.

Text on covers is `#F6F2E9`. Pick the tone deterministically from the book id
(stable hash), so a book always has the same cover.

Never communicate state with color alone: pair it with text, an icon, or a
change in shape (for example a check mark on selected items).

## 4. Typography

Fonts are self-hosted as `.woff2` files in `public/fonts/` and declared with
`@font-face` (`font-display: swap`) in `src/index.css`. Do not load fonts from
external CDNs. Preload only the body font's regular weight in `index.html`.

| Role | Family | Fallback stack | Weights |
|---|---|---|---|
| Display / headings | Libre Caslon Text | `Georgia, 'Times New Roman', serif` | 400, 400 italic, 700 |
| UI / body | Inter (variable) | `system-ui, -apple-system, 'Segoe UI', sans-serif` | 400–700 |

Tokens: `--font-display`, `--font-body`.

Type scale (fluid, mobile → desktop):

| Token | Size | Line height | Family / use |
|---|---|---|---|
| `--text-display` | `clamp(2.25rem, 1.6rem + 3vw, 3.75rem)` | 1.05 | Display; welcome title |
| `--text-h1` | `clamp(1.75rem, 1.4rem + 1.6vw, 2.5rem)` | 1.15 | Display; view titles |
| `--text-h2` | `clamp(1.375rem, 1.2rem + 0.8vw, 1.75rem)` | 1.2 | Display; section/shelf titles |
| `--text-h3` | `1.125rem` | 1.3 | Body 600; card titles |
| `--text-body` | `1rem` | 1.55 | Body 400 |
| `--text-small` | `0.875rem` | 1.45 | Body; metadata |
| `--text-caption` | `0.75rem` | 1.4 | Body 600, `letter-spacing: 0.08em`, uppercase; eyebrows and labels |

Rules:

- Serif for titles, quotes, and book titles on covers; sans-serif for everything
  interactive (buttons, chips, inputs, metadata).
- Use the uppercase caption style for eyebrows above titles ("BIBLIOTECA ROBERVAL
  CARDOSO"), echoing the moodboard.
- Italic serif is reserved for quotes and small emphasis inside display titles.
- Keep paragraph width at or below `65ch`.
- Never go below `0.75rem`.

## 5. Spacing, layout, and breakpoints

### 5.1 Spacing

4px base scale: `--space-1` 4px, `--space-2` 8px, `--space-3` 12px,
`--space-4` 16px, `--space-5` 24px, `--space-6` 32px, `--space-7` 48px,
`--space-8` 64px, `--space-9` 96px. Use only these values for margins, paddings,
and gaps. Tailwind spacing utilities use the same 4px base, so the step names
differ: `--space-1` to `--space-4` are `1` to `4`, `--space-5` is `6`,
`--space-6` is `8`, `--space-7` is `12`, `--space-8` is `16`, and `--space-9` is
`24` (for example, `gap-6` equals `var(--space-5)`).

### 5.2 Breakpoints (mobile first, `min-width`)

| Name | Width | Typical change |
|---|---|---|
| base | 0 | Single column, 16px gutter, sticky bottom action bars |
| `sm` | 600px | Two-column grids, 24px gutter |
| `md` | 900px | Side-by-side hero, actions move inline, shelf arrow buttons |
| `lg` | 1200px | Max content width reached, 32px gutter |

CSS custom properties cannot be used inside media queries; write the literal
widths above and keep this table as the single source. The Tailwind `sm:`,
`md:`, and `lg:` variants use these same widths (`--breakpoint-*` in
`src/index.css`).

### 5.3 Containers

- `.container`: `width: min(100% - 2 * var(--gutter), 1200px); margin-inline: auto;`
  with `--gutter` 16px → 24px (`sm`) → 32px (`lg`).
- Narrow reading/focus content (welcome text, onboarding steps): max 720px.
- Horizontal page scroll is never allowed. Shelves scroll inside themselves.
- Use `min-height: 100dvh` for full-screen views and respect safe areas
  (`env(safe-area-inset-bottom)`) on sticky bottom bars.

## 6. Shape, elevation, and motion

| Token | Value | Use |
|---|---|---|
| `--radius-sm` | 6px | Inputs, small badges |
| `--radius-md` | 12px | Cards, panels |
| `--radius-lg` | 20px | Sheets, hero panels |
| `--radius-pill` | 999px | Buttons, chips, search bar |
| `--radius-cover` | 3px 6px 6px 3px | Book covers (spine side tighter) |
| `--shadow-sm` | `0 1px 2px rgb(36 39 34 / 0.08)` | Cards at rest |
| `--shadow-md` | `0 6px 20px rgb(36 39 34 / 0.12)` | Covers, hover, sticky bars |
| `--duration-fast` | 150ms | Hover, press, chip toggle |
| `--duration-base` | 250ms | Step transitions, reveal |
| `--ease-standard` | `cubic-bezier(0.2, 0, 0, 1)` | All transitions |

In dark mode shadows lose meaning; rely on `--color-border` and surface contrast.

Motion is functional and short: fades/slides of 8–16px between onboarding steps,
a slight lift on hover (`translateY(-2px)`) for covers, a scale press (`0.97`)
on buttons. Wrap all non-essential motion in
`@media (prefers-reduced-motion: no-preference)`.

## 7. Components

Shared components live in `src/components/`; feature-only components stay in
their feature. Build only what a view needs; this list defines how each element
must look when it is built.

### 7.1 Buttons

Global classes in `src/index.css`, applicable to `<button>`, `<a>`, and
`<RouterLink>` (do not wrap them in a component without a concrete benefit):

- `.button` base: pill, min-height 48px (44px for `.button--small`), padding
  `0 var(--space-5)`, body font 600, inline icon gap `var(--space-2)`.
- `.button--primary`: `--color-primary` fill, `--color-on-primary` text. One per
  screen region. A trailing arrow icon in a circle echoes the wireframe's CTA.
- `.button--secondary`: transparent, 1.5px `--color-primary` border.
- `.button--ghost`: text only, for tertiary actions ("Pular", "Voltar").
- Disabled: 45% opacity, `cursor: not-allowed`, and keep it focusable only if an
  explanation is shown next to it; prefer explaining why the action is not yet
  available ("Escolha pelo menos 1 área").
  In dark mode, disabled buttons drop the opacity and use `--color-surface-muted`
  with `--color-text-muted` and a `--color-border` outline (6.6:1), because
  45% opacity over the dark surface was unreadable (2.8:1).

### 7.2 Chips (`SelectableChip.vue`)

Toggle chips for areas, courses, genres, and filters. Pill shape, min-height
40px, `--color-surface-muted` background at rest; selected state uses
`--color-primary-soft` background, `--color-primary` border, `--color-on-primary-soft` text, **and** a
leading check icon. Render as `<button type="button" aria-pressed>`. Group chips
in a `<fieldset>` with a `<legend>` and wrap them with `flex-wrap` and
`gap: var(--space-2)`.

### 7.3 Inputs and search

The search field is a pill with a leading magnifier icon, a clear button when it
has text, `type="search"`, a visible `<label>` (visually hidden is acceptable when
the placeholder and icon make the purpose obvious), and min-height 48px.

### 7.4 Book cover (`BookCover.vue`)

There are no cover images. Generate a typographic cover:

- Aspect ratio 2:3, `--radius-cover`, `--shadow-md`.
- Background from the cover colors (section 3.3) chosen by the book id.
- A darker 6% spine band on the left edge and a thin inner border inset by 6px
  (classic edition look).
- Small uppercase author at the top, serif title centered (line-clamped to 4
  lines, size relative to the cover width using container query units), and a
  small ornament or rule.
- Decorative: `aria-hidden="true"` when the title is also rendered as text next to
  it; otherwise give it `role="img"` and an `aria-label` with the title and
  author.

### 7.5 Book card

Cover on top, then title (`--text-h3`, two-line clamp), author (`--text-small`,
muted, one line), and an availability badge (`AvailabilityBadge.vue`). The
shared `BookCard.vue` is a link to the book page (`/books/:id`): the whole card is
the link, its accessible name is the title, hover lifts the cover slightly and
underlines the title (hover-capable devices only). In selection contexts (onboarding)
the whole card becomes a toggle button with `aria-pressed`, a selected outline
(3px `--color-primary`), and a check badge on the cover.

### 7.6 Badges

Small pill with a dot plus text, `--text-caption` without uppercase:
"Disponível" (`--color-success`) and "Emprestado" (`--color-warning`).

### 7.7 Header (`AppHeader.vue`)

Single header, no bottom navigation bar. Left: brand mark + "IF Explore",
always a link to the welcome view (`/`). From `sm` (600px), center: the main navigation (`<nav>`, three-column grid so it stays centered
on wide screens): "Recomendações" (`/home`, marked with
`aria-current="page"`, primary color and underline when active) and "Sobre",
rendered as a disabled link (`aria-disabled`, not focusable, "Em breve") until
the about view exists. Below 600px the links move into a menu opened by a
hamburger button at the far right (`aria-expanded`/`aria-controls`). The menu
fills the screen below the header (fixed, above page content, page scroll
locked), shows the links in larger type and a simple footer (library name,
campus, link to the official site), and closes on navigation, Escape (focus
returns to the button), or a tap outside the header. The header always sits
above page content (`z-20`). Right: icon-only contextual actions passed through a slot (for
example the ✦ "Ajustar preferências" icon button on the home), followed by the
theme toggle, present on every view. The
toggle shows the moon in light mode and the sun in dark mode, swapping them
with a short rotate/scale/fade transition. Height 64px, `--color-surface` with a bottom border,
sticky on the home, static elsewhere.

### 7.7.1 Footer (`AppFooter.vue`)

Shared footer on the welcome, home, and book pages (not on the onboarding,
which stays a focus flow). Surface background, top border, small muted text,
links without underline until hover. Columns: about the project (brand, short
description, note that the official catalog is still where loans happen),
library (name, hours, email, catalog link), campus (`<address>`, phone, email,
"Fale conosco" and campus site), IF Sudeste MG social networks, and "Desenvolvido
por". Bottom bar: copyright and a notice that catalog data is illustrative while
mocked. Contact data lives in `src/lib/campus-info.ts` (source: the campus
"Fale conosco" page). External links use `ExternalLink.vue` (new tab, icon,
screen-reader hint). Layout: 1 column at base, 2 at `sm`, 3 at `md` with the
about block on its own row, 4 at `lg`.

### 7.8 Icons

Line icons, 24px grid, 1.5px stroke, round caps and joins, `currentColor`, in the
style of the moodboard iconography (open book, bookmark, shelf, sparkle, search,
arrow, check, close, sliders). Implement as small SVG components in
`src/components/icons/` only when used. No icon library. Decorative icons get
`aria-hidden="true"`; icon-only buttons need an `aria-label` and a 44×44px hit
area.

### 7.9 Feedback states

- **Loading:** skeletons with the final shape (cover rectangles, text bars) and a
  subtle shimmer under `prefers-reduced-motion: no-preference`; never a lone
  spinner for content areas.
- **Empty:** an icon, a short serif sentence, a helpful explanation, and an action.
- **Error:** text in `--color-danger` plus an icon and a retry action; announce
  with `role="alert"`.
- Mock services resolve after a short artificial delay (200–400ms) so loading
  states are exercised.

## 8. Accessibility

- One `<h1>` per view; logical heading order; landmarks (`header`, `main`,
  `nav`, `footer`).
- Visible focus ring on every interactive element:
  `outline: 2px solid var(--color-focus); outline-offset: 2px` via
  `:focus-visible`.
- Touch targets ≥ 44×44px.
- Moving between onboarding steps moves focus to the new step's heading.
- Live counters (for example "2 de 3 escolhidos") use `aria-live="polite"`.
- Horizontal shelves are keyboard reachable (`tabindex="0"` on the scroll region
  with an accessible name, or focusable items inside) and have arrow buttons at
  `md`+.
- Respect `prefers-reduced-motion` and `prefers-color-scheme`.
- `lang="pt-BR"` on `<html>` and a meaningful `<title>` per route.

## 9. Content and internationalization

- All interface text lives in `vue-i18n` resources (`src/locales/pt-BR.ts`), with
  keys grouped by feature (`welcome.*`, `onboarding.*`, `home.*`, `common.*`).
  Only pt-BR is supported.
- Mock catalog content (titles, authors, synopses) is data, not interface text,
  and stays in the mock data files.
- Format numbers and dates with `Intl` through vue-i18n.

## 10. Shared domain and data

These contracts are used by more than one feature and therefore live in shared
directories (see `docs/project-guidelines.md`):

| Concern | Location |
|---|---|
| `Book`, `KnowledgeArea`, `Course`, `LiteraryGenre` types | `src/models/` |
| Mock catalog data | `src/services/mocks/` |
| Catalog access (async, mocked) | `src/services/catalog-service.ts` |
| `ReadingPreferences` type | `src/models/reading-preferences.ts` |
| Preferences persistence | `src/services/preferences-storage.ts` |
| Reactive preferences access | `src/composables/useReadingPreferences.ts` |

### 10.1 Taxonomy

- **Knowledge areas (mandatory choice):** Ciências Exatas e da Terra, Ciências
  Biológicas, Ciências Agrárias, Ciências da Saúde, Ciências Humanas, Ciências
  Sociais Aplicadas, Tecnologia e Computação, Linguagens, Letras e Artes.
- **Campus courses (optional refinement):** each course belongs to one area and
  one level (`integrated`, `technical`, `undergraduate`, `graduate`). The list
  mirrors ifsudestemg.edu.br/barbacena/cursos (checked October 2026) and keeps
  courses with suspended intakes, since they still have enrolled students:
  - Técnico integrado: Agroindústria, Agropecuária, Alimentos, Hospedagem, Química.
  - Técnico concomitante/subsequente: Enfermagem, Eventos, Informática, Meio
    Ambiente, Segurança do Trabalho, Agropecuária (EaD).
  - Graduação: Bacharelados em Administração, Agronomia, Educação Física, Gestão
    Ambiental, Nutrição, Sistemas de Informação; Licenciaturas em Ciências
    Biológicas, Educação Física, Química; Tecnologias em Alimentos, Gestão de
    Turismo (presencial e EaD), Sistemas para Internet.
  - Pós-graduação: Especialização em Planejamento e Gestão de Áreas Naturais
    Protegidas.
- **Literary genres (refine step):** Romance, Aventura, Suspense e mistério,
  Fantasia, Ficção científica, Terror, Poesia, Clássicos brasileiros, Biografias e
  memórias, Quadrinhos, Humor, Crônicas e contos.

### 10.2 Book model (mock)

```ts
interface Book {
  id: string
  title: string
  authors: string[]
  year: number
  areaId: string
  courseIds: string[]
  genreIds: string[]
  subjects: string[]
  synopsis: string
  quote?: string
  availability: 'available' | 'borrowed'
  callNumber: string // classificação/localização no acervo
}
```

Mock at least 8 books per knowledge area and 3 per literary genre, using real,
plausible academic and literary titles.

### 10.3 Preferences persistence

- `localStorage` key `if-explore:preferences`, JSON with a `version: 1` field.
- Shape: `{ version, areaIds, courseIds, seedBookIds, genreIds, updatedAt }`.
- Data read from storage is untrusted: parse as `unknown`, validate the shape,
  and treat invalid data as "no preferences". Consumers ignore ids that no
  longer exist in the catalog.
- Wrap every storage access in `try/catch` (private mode, blocked storage);
  the app must work in-memory if storage fails.
- "Has preferences" means at least one area and three seed books.
- Tell the visitor, in the interface, that preferences stay only in this browser.

## 11. Routes and flow

| Path | View | Notes |
|---|---|---|
| `/` | `features/welcome/views/WelcomeView.vue` | Entry point |
| `/onboarding` | `features/onboarding/views/TasteOnboardingView.vue` | `?step=areas\|books\|genres` |
| `/home` | `features/home/views/HomeView.vue` | Guard: redirect to `/` without preferences |
| `/books/:id` | `features/book-detail/views/BookDetailView.vue` | No guard; unknown ids show a not-found state |

Flow: welcome → onboarding (areas → books → [optional genres]) → home. Returning
visitors with saved preferences can go straight from the welcome to the home or
restart the flow, with previous answers pre-filled. From any book card, the
visitor opens the book page, whose related shelf leads to other books.
