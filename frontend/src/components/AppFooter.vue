<!--
  Rodapé das páginas: apresentação do projeto, contatos da biblioteca e do
  campus, redes sociais do IF e quem desenvolveu.
-->
<template>
  <footer class="border-t border-border bg-surface text-small text-text-muted [&_a]:no-underline [&_a:hover]:underline">
    <div class="container grid gap-10 py-12 sm:grid-cols-2 md:grid-cols-3 md:gap-8 md:py-16 lg:grid-cols-[1.3fr_1fr_1.2fr_1fr]">
      <section
        class="sm:col-span-2 md:col-span-3 lg:col-span-1"
        aria-labelledby="footer-about"
      >
        <h2
          id="footer-about"
          class="sr-only"
        >
          {{ t('common.appName') }}
        </h2>
        <RouterLink
          to="/"
          class="inline-flex min-h-11 items-center gap-3 text-text no-underline"
          :aria-label="t('common.brandHomeLabel')"
        >
          <BrandMark />
          <span class="font-display text-[1.25rem] leading-none">{{ t('common.appName') }}</span>
        </RouterLink>
        <p class="mt-3 max-w-[36ch]">
          {{ t('common.footer.description') }}
        </p>
        <p class="mt-3 max-w-[36ch] text-caption">
          {{ t('common.footer.disclaimer') }}
        </p>
      </section>

      <section aria-labelledby="footer-library">
        <h2
          id="footer-library"
          class="eyebrow mb-3 font-body"
        >
          {{ t('common.footer.library') }}
        </h2>
        <ul class="m-0 grid list-none gap-2 p-0">
          <li class="text-text">
            {{ t('common.libraryName') }}
          </li>
          <li>{{ t('common.footer.hours', { hours: LIBRARY.hours }) }}</li>
          <li>
            <a
              :href="`mailto:${LIBRARY.email}`"
              class="[overflow-wrap:anywhere]"
            >{{ LIBRARY.email }}</a>
          </li>
          <li>
            <ExternalLink :href="LIBRARY_CATALOG_URL">
              {{ t('common.footer.catalog') }}
            </ExternalLink>
          </li>
        </ul>
      </section>

      <section aria-labelledby="footer-campus">
        <h2
          id="footer-campus"
          class="eyebrow mb-3 font-body"
        >
          {{ t('common.footer.campus') }}
        </h2>
        <address class="grid gap-2 not-italic">
          <span class="text-text">{{ t('common.institution') }}</span>
          <span>
            {{ CAMPUS.street }}<br>
            {{ CAMPUS.district }} · {{ t('common.footer.postalCode', { code: CAMPUS.postalCode }) }}<br>
            {{ CAMPUS.city }}
          </span>
          <a :href="CAMPUS.phoneHref">{{ CAMPUS.phone }}</a>
          <a
            :href="`mailto:${CAMPUS.email}`"
            class="[overflow-wrap:anywhere]"
          >{{ CAMPUS.email }}</a>
        </address>
        <ul class="m-0 mt-3 grid list-none gap-2 p-0">
          <li>
            <ExternalLink :href="CAMPUS.contactUrl">
              {{ t('common.footer.contact') }}
            </ExternalLink>
          </li>
          <li>
            <ExternalLink :href="CAMPUS.siteUrl">
              {{ t('common.footer.campusSite') }}
            </ExternalLink>
          </li>
        </ul>
      </section>

      <div class="grid content-start gap-8">
        <section aria-labelledby="footer-social">
          <h2
            id="footer-social"
            class="eyebrow mb-3 font-body"
          >
            {{ t('common.footer.social') }}
          </h2>
          <ul class="m-0 flex list-none flex-wrap gap-x-4 gap-y-2 p-0">
            <li
              v-for="link in SOCIAL_LINKS"
              :key="link.url"
            >
              <ExternalLink :href="link.url">
                {{ link.name }}
              </ExternalLink>
            </li>
          </ul>
        </section>

        <section aria-labelledby="footer-developers">
          <h2
            id="footer-developers"
            class="eyebrow mb-3 font-body"
          >
            {{ t('common.footer.developedBy') }}
          </h2>
          <ul class="m-0 grid list-none gap-2 p-0">
            <li
              v-for="developer in DEVELOPERS"
              :key="developer.url"
            >
              <ExternalLink :href="developer.url">
                {{ developer.name }}
              </ExternalLink>
            </li>
          </ul>
        </section>
      </div>
    </div>

    <div class="border-t border-border">
      <div class="container flex flex-col gap-1 py-5 text-caption sm:flex-row sm:justify-between">
        <p>{{ t('common.footer.copyright', { year }) }}</p>
        <p>{{ t('common.footer.mockNotice') }}</p>
      </div>
    </div>
  </footer>
</template>

<script setup lang="ts">
import { useI18n } from 'vue-i18n'
import { CAMPUS, DEVELOPERS, LIBRARY, SOCIAL_LINKS } from '../lib/campus-info'
import { LIBRARY_CATALOG_URL } from '../lib/library-catalog'
import BrandMark from './BrandMark.vue'
import ExternalLink from './ExternalLink.vue'

const { t } = useI18n()
const year = new Date().getFullYear()
</script>
