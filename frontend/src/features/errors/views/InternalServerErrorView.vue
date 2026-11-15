<!-- Exibe o aviso para erros internos do servidor. -->
<template>
  <ErrorPage
    :code="500"
    kind="serverError"
  />
</template>

<script setup lang="ts">
import ErrorPage from '../components/ErrorPage.vue'
</script>
