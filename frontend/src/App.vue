<!-- Disponibiliza o roteador principal da aplicação. -->
<template>
  <RouterView />
  <ScrollToTopButton v-if="!route.meta.focusMode" />
</template>

<script setup lang="ts">
import { useRoute } from 'vue-router'
import ScrollToTopButton from './components/ScrollToTopButton.vue'

const route = useRoute()
</script>
