<!-- Página do livro: destaque com capa e dados, ficha técnica e leituras relacionadas. -->
<template>
  <div class="flex min-h-dvh flex-col max-md:pb-20">
    <AppHeader sticky />

    <main
      class="book-page flex-1 pb-16"
      :class="{ 'book-page--tinted': bandTone }"
      :style="bandTone ? { '--band-tone': bandTone } : undefined"
    >
      <div class="container pt-3 md:pt-4">
        <button
          type="button"
          class="button button--ghost button--small -ms-3 px-3"
          @click="goBack"
        >
          <IconArrowLeft class="size-5" />
          {{ t('bookDetail.back') }}
        </button>
      </div>

      <div
        v-if="status === 'loading'"
        class="container grid gap-6 pt-2 md:grid-cols-[240px_minmax(0,1fr)] md:gap-12 md:pt-6"
        role="status"
      >
        <span class="sr-only">{{ t('bookDetail.loading') }}</span>
        <span
          class="skeleton mx-auto aspect-[2/3] w-36 rounded-cover md:mx-0 md:w-full"
          aria-hidden="true"
        />
        <div
          class="flex flex-col items-center gap-3 md:items-start"
          aria-hidden="true"
        >
          <span class="skeleton h-3 w-40 rounded-sm" />
          <span class="skeleton h-10 w-4/5 rounded-sm" />
          <span class="skeleton h-4 w-48 rounded-sm" />
          <span class="skeleton mt-6 h-12 w-64 rounded-pill" />
          <span class="skeleton mt-6 h-24 w-full rounded-md" />
        </div>
      </div>

      <div
        v-else-if="status === 'error'"
        class="container pt-8"
        role="alert"
      >
        <p class="mb-4 text-danger">
          {{ t('bookDetail.error') }}
        </p>
        <button
          type="button"
          class="button button--secondary"
          @click="reload"
        >
          {{ t('bookDetail.retry') }}
        </button>
      </div>

      <div
        v-else-if="status === 'notFound' || !book"
        class="container flex max-w-[420px] flex-col items-center gap-3 py-12 text-center"
      >
        <span class="grid size-14 place-items-center rounded-[50%] bg-primary-soft text-primary">
          <IconLibrary />
        </span>
        <h1 class="text-h2">
          {{ t('bookDetail.notFound.title') }}
        </h1>
        <p class="mb-2 text-text-muted">
          {{ t('bookDetail.notFound.text') }}
        </p>
        <RouterLink
          class="button button--secondary"
          :to="fallbackPath"
        >
          {{ hasPreferences ? t('bookDetail.notFound.action') : t('bookDetail.notFound.actionStart') }}
        </RouterLink>
      </div>

      <div
        v-else
        class="motion-safe:transition-opacity motion-safe:duration-(--duration-base)"
        :class="{ 'opacity-60': isRefreshing }"
        :aria-busy="isRefreshing"
      >
        <BookHero
          ref="hero"
          :book="book"
          :eyebrow="eyebrow"
        >
          <div
            ref="actions"
            class="mt-6 flex flex-col gap-3 sm:flex-row sm:justify-center md:justify-start"
          >
            <a
              class="button button--primary"
              :href="LIBRARY_CATALOG_URL"
              target="_blank"
              rel="noopener noreferrer"
            >
              {{ t('bookDetail.openCatalog') }}
              <IconExternalLink class="size-5" />
              <span class="sr-only">{{ t('common.opensInNewTab') }}</span>
            </a>
            <BookShareButton :title="book.title" />
          </div>

          <section
            class="mt-10"
            aria-labelledby="book-synopsis-title"
          >
            <h2
              id="book-synopsis-title"
              class="mb-3 font-body text-h3 font-semibold"
            >
              {{ t('bookDetail.synopsis') }}
            </h2>
            <p class="max-w-[65ch] text-body">
              {{ book.synopsis }}
            </p>
            <blockquote
              v-if="book.quote"
              class="m-0 mt-6 max-w-[60ch] border-l-2 border-primary pl-4 font-display text-h3 leading-[1.4] text-text-muted italic"
            >
              “{{ book.quote }}”
            </blockquote>
            <ul
              v-if="tags.length > 0"
              class="m-0 mt-6 flex list-none flex-wrap gap-2 p-0"
              :aria-label="t('bookDetail.tags')"
            >
              <li
                v-for="tag in tags"
                :key="tag"
                class="rounded-pill border border-border bg-surface px-3 py-1 text-small"
              >
                {{ tag }}
              </li>
            </ul>
          </section>

          <BookRecord
            class="mt-10"
            :book="book"
            :area-name="areaName"
            :year-label="yearLabel"
            :course-names="courseNames"
          />
        </BookHero>

        <div
          v-if="shelves"
          class="container mt-16 grid grid-cols-[minmax(0,1fr)] gap-12"
        >
          <BookShelf
            v-if="shelves.sameAuthor"
            :title="t('bookDetail.moreFromAuthor', { author: shelves.sameAuthor.author })"
            :books="shelves.sameAuthor.books"
          />
          <BookShelf
            v-if="shelves.related.length >= MIN_RELATED"
            :title="t('bookDetail.related')"
            :books="shelves.related"
          />
        </div>
      </div>
    </main>

    <AppFooter />

    <Transition name="catalog-bar">
      <div
        v-if="showCatalogBar"
        class="fixed inset-x-0 bottom-0 z-10 border-t border-border bg-surface pt-3 pb-[calc(var(--space-3)+env(safe-area-inset-bottom))] md:hidden"
      >
        <div class="container">
          <a
            class="button button--primary w-full"
            :href="LIBRARY_CATALOG_URL"
            target="_blank"
            rel="noopener noreferrer"
          >
            {{ t('bookDetail.openCatalog') }}
            <IconExternalLink class="size-5" />
            <span class="sr-only">{{ t('common.opensInNewTab') }}</span>
          </a>
        </div>
      </div>
    </Transition>
  </div>
</template>

<script setup lang="ts">
import { computed, nextTick, useTemplateRef, watch } from 'vue'
import { useI18n } from 'vue-i18n'
import { useRoute, useRouter } from 'vue-router'
import AppFooter from '../../../components/AppFooter.vue'
import AppHeader from '../../../components/AppHeader.vue'
import BookShelf from '../../../components/BookShelf.vue'
import IconArrowLeft from '../../../components/icons/IconArrowLeft.vue'
import IconExternalLink from '../../../components/icons/IconExternalLink.vue'
import IconLibrary from '../../../components/icons/IconLibrary.vue'
import { useReadingPreferences } from '../../../composables/useReadingPreferences'
import { pickCoverColor } from '../../../lib/cover-color'
import { LIBRARY_CATALOG_URL } from '../../../lib/library-catalog'
import BookHero from '../components/BookHero.vue'
import BookRecord from '../components/BookRecord.vue'
import BookShareButton from '../components/BookShareButton.vue'
import { useBookDetail } from '../composables/useBookDetail'
import { useScrolledPast } from '../composables/useScrolledPast'

const MIN_RELATED = 3

const { t } = useI18n()
const route = useRoute()
const router = useRouter()
const { hasPreferences } = useReadingPreferences()

const bookId = computed(() => {
  const { id } = route.params
  return typeof id === 'string' ? id : ''
})

const { status, isRefreshing, book, areaName, courseNames, genreNames, shelves, reload } =
  useBookDetail(bookId)

const hero = useTemplateRef<InstanceType<typeof BookHero>>('hero')
const actions = useTemplateRef<HTMLDivElement>('actions')

// No celular, o botão do acervo fica fixo embaixo depois que o original sai da tela.
const scrolledPastActions = useScrolledPast(actions)
const showCatalogBar = computed(() => status.value === 'ready' && scrolledPastActions.value)

// A faixa começa logo abaixo do cabeçalho, atrás do "Voltar", só quando há livro.
const bandTone = computed(() => (book.value ? pickCoverColor(book.value.id) : null))

const fallbackPath = computed(() => (hasPreferences.value ? '/home' : '/'))

// Anos negativos representam obras anteriores à era comum.
const yearLabel = computed(() => {
  const year = book.value?.year ?? 0
  return year < 0 ? t('bookDetail.yearBce', { year: -year }) : String(year)
})

const eyebrow = computed(() => [areaName.value, yearLabel.value].filter(Boolean).join(' · '))

const tags = computed(() => [...(book.value?.subjects ?? []), ...genreNames.value])

// Volta pelo histórico quando o visitante veio de outra tela da aplicação.
function goBack(): void {
  if (typeof router.options.history.state.back === 'string') {
    router.back()
    return
  }
  void router.push(fallbackPath.value)
}

// Título da aba com o nome do livro (ou o aviso de livro inexistente).
watch([status, book], ([currentStatus, currentBook]) => {
  const appName = t('common.appName')
  if (currentStatus === 'ready' && currentBook) {
    document.title = `${currentBook.title} · ${appName}`
  } else if (currentStatus === 'notFound') {
    document.title = `${t('bookDetail.notFound.title')} · ${appName}`
  }
})

// Ao trocar de livro pela prateleira, o foco vai para o novo título assim que ele chega.
watch(
  () => book.value?.id,
  (id, previousId) => {
    if (id && previousId && id !== previousId) {
      void nextTick(() => hero.value?.focusHeading())
    }
  },
)
</script>

<style scoped>
/*
  Faixa de fundo na cor da capa, misturada ao papel para manter o contraste do
  texto; no escuro a mistura é mais forte e o tom recebe uma luminosidade
  mínima, para que capas escuras (carvão, índigo) não se confundam com o fundo.
  Ela se dissolve no fundo da página na parte de baixo.
*/
.book-page {
  --band-height: 420px;

  position: relative;
  isolation: isolate;
}

.book-page--tinted::before {
  content: '';
  position: absolute;
  inset: 0 0 auto;
  z-index: -1;
  height: var(--band-height);
  background: linear-gradient(
    to bottom,
    light-dark(
        color-mix(in srgb, var(--band-tone) 20%, var(--color-bg)),
        color-mix(in srgb, oklch(from var(--band-tone) max(l, 0.5) c h) 40%, var(--color-bg))
      )
      55%,
    var(--color-bg)
  );
}

@media (min-width: 900px) {
  .book-page {
    --band-height: 360px;
  }
}

.skeleton {
  display: block;
  background: var(--color-surface-muted);
}

@media (prefers-reduced-motion: no-preference) {
  .skeleton {
    animation: pulse 1.2s ease-in-out infinite alternate;
  }
}

@media (prefers-reduced-motion: no-preference) {
  .catalog-bar-enter-active,
  .catalog-bar-leave-active {
    transition: transform var(--duration-base) var(--ease-standard);
  }

  .catalog-bar-enter-from,
  .catalog-bar-leave-to {
    transform: translateY(100%);
  }
}

@keyframes pulse {
  to {
    opacity: 0.5;
  }
}
</style>
