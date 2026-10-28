---
name: book-detail-view
description: Implement or change the IF Explore book page (route `/books/:id`, BookDetailView.vue) — cover and full record of one book on a band tinted with its cover color, a link to the official library catalog, and a shelf of related books. Also covers making book cards link to this page. Uses the mocked catalog only.
---

# Book detail view

Read `frontend/AGENTS.md`, `frontend/docs/project-guidelines.md`, and
`frontend/docs/design-guidelines.md` first. Foundations (tokens, Tailwind, i18n,
models, mock catalog) are described in the `welcome-view` skill and the home
shelf in the `home-view` skill; reuse them, never duplicate them.

## 1. Goal

Show everything a visitor needs to decide whether to read a book and where to
find it on campus, then invite them to keep exploring through related books.
Classic look (serif, paper, generated cover), modern experience (tinted hero,
sticky cover on desktop, swipeable shelf).

## 2. Route and navigation

- Route `/books/:id`, lazy-loaded
  `features/book-detail/views/BookDetailView.vue`, `titleKey` with the book
  title once loaded (fallback "Livro"). No preference guard: a shared link must
  open for anyone.
- Book cards become links (`RouterLink` to `/books/:id`) wherever they appear:
  home shelves, search results, and the related shelf here. The whole card is
  the link; its accessible name is the book title. Keep a visible focus ring and
  a subtle hover lift on the cover (hover-capable devices only). Update
  design guidelines §7.5 and the `home-view` skill, which currently say cards are
  not interactive.
- Navigating between books (related shelf) scrolls to the top and moves focus to
  the `h1`.
- "Voltar": `router.back()` when the previous history entry belongs to the app
  (`router.options.history.state.back` is a string); otherwise push `/home`
  (or `/` without preferences).

## 3. Data model changes

Extend `Book` in `src/models/book.ts` and fill every mock book:

```ts
interface Book {
  // ...existing fields, minus `availability`
  isbn?: string            // ISBN-13 of a real Brazilian edition; omit when unsure
  publisher: string
  edition?: string         // "3ª edição"
  pages: number
  copies: { total: number; available: number }
}
```

- Replace `availability` with `copies`; derive the state with a pure helper in
  `src/models/book.ts` (`isAvailable(book)`) and update current consumers
  (`BookCard`, badges). Do not store both.
- Never invent ISBNs: use one only when it is certainly real; it is needed for
  the future Google Books integration, which will skip books without it.
- `getBookById(id)` in `src/services/catalog-service.ts` (mocked delay),
  returning `Book | null`.

## 4. Layout

Mobile (base):

```
AppHeader: [BrandMark] IF Explore                 [theme toggle]
[← Voltar]
┌ band tinted with the cover color (full bleed) ┐
│        Cover (~144px, centered, shadow)        │
│   EYEBROW: ÁREA · ANO                          │
│   Serif h1 title (centered)                    │
│   Authors                                      │
│   ● 2 de 3 exemplares disponíveis              │
└────────────────────────────────────────────────┘
[ Ver no acervo da biblioteca ↗ ]   (primary, full width)
Sinopse (paragraph)
Citação (italic serif blockquote, only when present)
Assuntos e gêneros (static chips/tags, not buttons)
Ficha técnica (definition list)
Leituras relacionadas (BookShelf)
```

`md`+ (≥ 900px): inside `.container`, a two-column grid
`[cover ~240px] [details, max ~65ch]`. The cover column is `position: sticky`
below the header. The tinted band sits behind the top of both columns (from the
top of the page to about the middle of the cover) instead of wrapping the
whole hero. Title left-aligned; breadcrumb-like back link above:
"← Suas recomendações". The related shelf spans the full container width below.

### Hero band

- Color: the same tone `BookCover` uses for the book. Move the color picker out of
  `BookCover.vue` into `src/lib/cover-color.ts` (pure, stable hash) and use it in
  both places.
- Mix the tone with the page so text keeps contrast in both themes:
  `color-mix(in srgb, <cover tone> 20%, var(--color-bg))` in light; in dark,
  give the tone a minimum lightness first (`oklch(from <tone> max(l, 0.5) c h)`)
  so dark covers (charcoal, indigo) still read against the page. Text on the band uses the normal text tokens; check
  4.5:1 contrast in light and dark.
- Subtle fade at the bottom edge into `--color-bg`; no photos or gradients
  beyond that.
- The band is drawn by the page wrapper (`<main>`), so it starts right below
  the header and sits behind the "Voltar" row; loading, error, and not-found
  states have no band.

### Record ("Ficha técnica")

Definition list (`<dl>`), two columns from `sm`:

| Label | Value |
|---|---|
| Localização | `callNumber`, with a copy button ("Copiar localização", toast-free: the button label changes to "Copiado" for 2s and announces via `aria-live`) |
| Exemplares | "2 de 3 disponíveis" |
| Editora | publisher, plus edition when present |
| Ano | year (classical works with negative years show "c. 375 a.C.") |
| Páginas | pages, formatted with `Intl.NumberFormat` |
| ISBN | only when present |
| Área | area name |
| Indicado para | course names linked to the book, when any |

### Actions

- Primary: "Ver no acervo da biblioteca" — external link (`target="_blank"`,
  `rel="noopener noreferrer"`, external icon + visually hidden "abre em nova
  aba"). Check whether the PHL catalog accepts a search URL by title; if it
  does, build it from the title with `encodeURIComponent` in a pure function;
  otherwise link to the catalog home already used on the welcome view.
- Secondary "Compartilhar" (`BookShareButton.vue`): native Web Share when
  available, otherwise copies the link, with the same temporary label feedback
  as "Copiar localização" (`useClipboardFeedback`).
- Mobile only: once the actions scroll out of view (`useScrolledPast`), a fixed
  bottom bar keeps "Ver no acervo da biblioteca" at hand; it slides in/out with
  motion allowed and the main area reserves space so it never covers content.
- Reserved secondary slot for "Prévia" (Google Books). Do **not** render it
  until that integration exists; the layout must not leave an empty gap.

### Related books

- Reuse the home `BookShelf`/`BookCard`. Because a second feature now needs
  them, move both to `src/components/` (shared) and update imports; keep them
  free of home-specific rules.
- Title "Leituras relacionadas"; when two or more related books share an author
  with the current one, show a first shelf "Mais de <autor>" and keep the rest in
  "Leituras relacionadas".
- Ranking is a pure function in
  `features/book-detail/models/related-books.ts`: same author (3) > shared
  subjects (2 each) > shared genre (1) > same area (1); exclude the current
  book; at most 12; hide the shelf below 3 books.

## 5. States

- Loading: skeleton with the hero shape (band, cover rectangle, title bars) and
  one skeleton shelf.
- Not found (`getBookById` returns `null`): stay on the route and show an empty
  state in the main area — serif "Livro não encontrado", short explanation, and
  a "Voltar para as recomendações" action. Set the document title accordingly.
- Error: message with retry (`role="alert"`).
- The view must react to `:id` changes without remounting issues: keep the
  current book visible (dimmed, `aria-busy`) while the next loads, then move
  focus to the new title; the router scrolls new pages to the top.

## 6. Structure

```
src/features/book-detail/
├── views/BookDetailView.vue
├── composables/useBookDetail.ts      (load by id, related books, status)
├── models/related-books.ts           (pure ranking)
└── components/
    ├── BookHero.vue                  (band, sticky cover, title, availability; slot for the rest)
    └── BookRecord.vue                (ficha técnica + copy location)
src/lib/cover-color.ts                (moved from BookCover)
src/lib/library-catalog.ts            (catalog home URL; PHL has no stable search URL)
src/components/BookShelf.vue, BookCard.vue, AvailabilityBadge.vue   (shared)
```

Interface text goes under `bookDetail.*` in `src/locales/pt-BR.ts`. Use
Tailwind utilities for layout, spacing, and typography; keep `<style scoped>`
for the band's pseudo-elements and the sticky cover if utilities express them
poorly.

## 7. Done when

- `/books/:id` renders any mock book; unknown ids show the not-found state.
- Cards on the home, search results, and related shelf open the book page; back
  returns to where the visitor came from.
- Band, cover, and text pass contrast in light and dark; no horizontal page
  scroll at 360px; correct at 1440px; keyboard and screen reader flow is
  title → actions → content → shelf.
- `availability` fully replaced by `copies`; no hardcoded interface text;
  `npm run lint`, `npm run typecheck`, and `npm run build` pass.
