<!-- Exibe o aviso para recursos sem permissão de acesso. -->
<template>
  <ErrorPage
    :code="403"
    kind="forbidden"
  />
</template>

<script setup lang="ts">
import ErrorPage from '../components/ErrorPage.vue'
</script>
