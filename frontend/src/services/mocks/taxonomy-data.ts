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

// Lista provisória: confirmar com a página de cursos do campus.
export const courses: Course[] = [
  { id: 'agronomy', name: 'Agronomia', areaId: 'agricultural-sciences' },
  { id: 'animal-science', name: 'Zootecnia', areaId: 'agricultural-sciences' },
  { id: 'nutrition', name: 'Nutrição', areaId: 'health-sciences' },
  { id: 'physical-education', name: 'Educação Física', areaId: 'health-sciences' },
  { id: 'information-systems', name: 'Sistemas de Informação', areaId: 'technology' },
  { id: 'internet-systems', name: 'Tecnologia em Sistemas para Internet', areaId: 'technology' },
  {
    id: 'environmental-management',
    name: 'Tecnologia em Gestão Ambiental',
    areaId: 'biological-sciences',
  },
  { id: 'biology-teaching', name: 'Licenciatura em Ciências Biológicas', areaId: 'biological-sciences' },
  {
    id: 'tourism-management',
    name: 'Tecnologia em Gestão de Turismo',
    areaId: 'applied-social-sciences',
  },
  { id: 'administration', name: 'Administração', areaId: 'applied-social-sciences' },
  { id: 'physics-teaching', name: 'Licenciatura em Física', areaId: 'exact-sciences' },
  { id: 'mathematics-teaching', name: 'Licenciatura em Matemática', areaId: 'exact-sciences' },
  { id: 'chemistry-teaching', name: 'Licenciatura em Química', areaId: 'exact-sciences' },
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
