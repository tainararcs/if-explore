import type { Course, KnowledgeArea, LiteraryGenre } from '../../models/taxonomy'

export const knowledgeAreas: KnowledgeArea[] = [
  { id: 'exact-sciences', name: 'Ciências Exatas e da Terra' },
  { id: 'biological-sciences', name: 'Ciências Biológicas' },
  { id: 'agricultural-sciences', name: 'Ciências Agrárias' },
  { id: 'health-sciences', name: 'Ciências da Saúde' },
  { id: 'humanities', name: 'Ciências Humanas' },
  { id: 'applied-social-sciences', name: 'Ciências Sociais Aplicadas' },
  { id: 'technology', name: 'Tecnologia e Computação' },
  { id: 'languages-arts', name: 'Linguagens, Letras e Artes' },
]

// Cursos listados em ifsudestemg.edu.br/barbacena/cursos (outubro de 2026), incluindo
// os que estão com novas turmas suspensas, pois ainda têm alunos matriculados.
export const courses: Course[] = [
  { id: 'agroindustry-integrated', name: 'Agroindústria', areaId: 'agricultural-sciences', level: 'integrated' },
  { id: 'agriculture-integrated', name: 'Agropecuária', areaId: 'agricultural-sciences', level: 'integrated' },
  { id: 'food-integrated', name: 'Alimentos', areaId: 'agricultural-sciences', level: 'integrated' },
  { id: 'hospitality-integrated', name: 'Hospedagem', areaId: 'applied-social-sciences', level: 'integrated' },
  { id: 'chemistry-integrated', name: 'Química', areaId: 'exact-sciences', level: 'integrated' },
  { id: 'nursing-technician', name: 'Enfermagem', areaId: 'health-sciences', level: 'technical' },
  { id: 'events-technician', name: 'Eventos', areaId: 'applied-social-sciences', level: 'technical' },
  { id: 'it-technician', name: 'Informática', areaId: 'technology', level: 'technical' },
  { id: 'environment-technician', name: 'Meio Ambiente', areaId: 'biological-sciences', level: 'technical' },
  { id: 'workplace-safety-technician', name: 'Segurança do Trabalho', areaId: 'health-sciences', level: 'technical' },
  { id: 'agriculture-distance', name: 'Agropecuária (EaD)', areaId: 'agricultural-sciences', level: 'technical' },
  { id: 'administration', name: 'Bacharelado em Administração', areaId: 'applied-social-sciences', level: 'undergraduate' },
  { id: 'agronomy', name: 'Bacharelado em Agronomia', areaId: 'agricultural-sciences', level: 'undergraduate' },
  { id: 'food-technology', name: 'Tecnologia em Alimentos', areaId: 'agricultural-sciences', level: 'undergraduate' },
  { id: 'biology-teaching', name: 'Licenciatura em Ciências Biológicas', areaId: 'biological-sciences', level: 'undergraduate' },
  { id: 'physical-education-teaching', name: 'Licenciatura em Educação Física', areaId: 'health-sciences', level: 'undergraduate' },
  { id: 'physical-education', name: 'Bacharelado em Educação Física', areaId: 'health-sciences', level: 'undergraduate' },
  { id: 'environmental-management', name: 'Bacharelado em Gestão Ambiental', areaId: 'biological-sciences', level: 'undergraduate' },
  { id: 'tourism-management', name: 'Tecnologia em Gestão de Turismo', areaId: 'applied-social-sciences', level: 'undergraduate' },
  { id: 'tourism-management-distance', name: 'Tecnologia em Gestão de Turismo (EaD)', areaId: 'applied-social-sciences', level: 'undergraduate' },
  { id: 'nutrition', name: 'Bacharelado em Nutrição', areaId: 'health-sciences', level: 'undergraduate' },
  { id: 'chemistry-teaching', name: 'Licenciatura em Química', areaId: 'exact-sciences', level: 'undergraduate' },
  { id: 'internet-systems', name: 'Tecnologia em Sistemas para Internet', areaId: 'technology', level: 'undergraduate' },
  { id: 'information-systems', name: 'Bacharelado em Sistemas de Informação', areaId: 'technology', level: 'undergraduate' },
  {
    id: 'protected-areas-specialization',
    name: 'Especialização em Planejamento e Gestão de Áreas Naturais Protegidas',
    areaId: 'biological-sciences',
    level: 'graduate',
  },
]

export const literaryGenres: LiteraryGenre[] = [
  { id: 'romance', name: 'Romance' },
  { id: 'adventure', name: 'Aventura' },
  { id: 'mystery', name: 'Suspense e mistério' },
  { id: 'fantasy', name: 'Fantasia' },
  { id: 'science-fiction', name: 'Ficção científica' },
  { id: 'horror', name: 'Terror' },
  { id: 'poetry', name: 'Poesia' },
  { id: 'brazilian-classics', name: 'Clássicos brasileiros' },
  { id: 'biography', name: 'Biografias e memórias' },
  { id: 'comics', name: 'Quadrinhos' },
  { id: 'humor', name: 'Humor' },
  { id: 'short-stories', name: 'Crônicas e contos' },
]
