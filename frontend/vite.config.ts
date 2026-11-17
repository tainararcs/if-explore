import tailwindcss from '@tailwindcss/vite'
import vue from '@vitejs/plugin-vue'
import { defineConfig, loadEnv } from 'vite'

// https://vite.dev/config/
export default defineConfig(({ mode }) => {
  // Lê também variáveis sem o prefixo VITE_, que ficam só na configuração e não vão ao navegador.
  const env = loadEnv(mode, process.cwd(), '')

  return {
    plugins: [vue(), tailwindcss()],
    // Flags de compilação do vue-i18n: somente Composition API e sem devtools em produção.
    define: {
      __VUE_I18N_FULL_INSTALL__: true,
      __VUE_I18N_LEGACY_API__: false,
      __INTLIFY_PROD_DEVTOOLS__: false,
    },
    // Em desenvolvimento, /api vai para o backend Django; em produção, o proxy reverso
    // serve a API no mesmo domínio.
    server: {
      // No Docker com o código montado do host, os eventos de arquivo não chegam ao
      // container: WATCH_POLLING=true troca por verificação periódica.
      watch: env.WATCH_POLLING === 'true' ? { usePolling: true, interval: 300 } : undefined,
      proxy: {
        '/api': {
          target: env.API_PROXY_TARGET || 'http://localhost:8000',
          changeOrigin: true,
        },
      },
    },
  }
})
