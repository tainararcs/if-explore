/** Grande área do conhecimento; escolha obrigatória na personalização. */
export interface KnowledgeArea {
  id: string
  name: string
}

/** Curso do campus, vinculado a uma única grande área. */
export interface Course {
  id: string
  name: string
  areaId: string
}

/** Gênero literário usado no refinamento opcional das preferências. */
export interface LiteraryGenre {
  id: string
  name: string
}
