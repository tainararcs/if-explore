/// <reference types="vite/client" />

/** Variáveis `VITE_` usadas pelo frontend (veja `.env.example`). */
interface ImportMetaEnv {
  /** Endereço base da API; padrão `/api` quando ausente. */
  readonly VITE_API_BASE_URL?: string
  /** Chave da API do Google Books; sem ela, a prévia de leitura fica desligada. */
  readonly VITE_GOOGLE_BOOKS_API_KEY?: string
}

interface ImportMeta {
  readonly env: ImportMetaEnv
}
