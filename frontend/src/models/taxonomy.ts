/** Grande área do conhecimento; escolha obrigatória na personalização. */
export interface KnowledgeArea {
  id: string
  name: string
}

/** Níveis de ensino oferecidos pelo campus, na ordem em que são exibidos. */
export const COURSE_LEVELS = ['integrated', 'technical', 'undergraduate', 'graduate'] as const

/**
 * Nível de ensino do curso: técnico integrado ao ensino médio, técnico
 * concomitante/subsequente, graduação ou pós-graduação.
 */
export type CourseLevel = (typeof COURSE_LEVELS)[number]

/** Curso do campus, vinculado a uma única grande área e a um nível de ensino. */
export interface Course {
  id: string
  name: string
  areaId: string
  level: CourseLevel
}

/** Gênero literário usado no refinamento opcional das preferências. */
export interface LiteraryGenre {
  id: string
  name: string
}
