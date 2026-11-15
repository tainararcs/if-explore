<!-- Exibe o aviso para rotas inexistentes. -->
<template>
  <ErrorPage
    :code="404"
    kind="notFound"
  />
</template>

<script setup lang="ts">
import ErrorPage from '../components/ErrorPage.vue'
</script>
