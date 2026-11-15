/// <reference types="vite/client" />

/** Variáveis `VITE_` usadas pelo frontend (veja `.env.example`). */
interface ImportMetaEnv {
  /** Endereço base da API; padrão `/api` quando ausente. */
  readonly VITE_API_BASE_URL?: string
}

interface ImportMeta {
  readonly env: ImportMetaEnv
}
