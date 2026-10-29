/**
 * Dados públicos do campus, da biblioteca e da equipe exibidos no rodapé.
 *
 * Fonte: página "Fale Conosco" do IF Sudeste MG – Campus Barbacena
 * (https://www.ifsudestemg.edu.br/barbacena/fale-conosco), consultada em
 * outubro de 2026. Atualize aqui se o campus mudar endereço ou contatos.
 */
export const CAMPUS = {
  street: 'Rua Monsenhor José Augusto, nº 204',
  district: 'Bairro São José',
  city: 'Barbacena – MG',
  postalCode: '36205-018',
  /** Telefone da chefia de gabinete. */
  phone: '(32) 3198-1416',
  phoneHref: 'tel:+553231981416',
  email: 'gabinete.barbacena@ifsudestemg.edu.br',
  siteUrl: 'https://www.ifsudestemg.edu.br/barbacena',
  contactUrl: 'https://www.ifsudestemg.edu.br/barbacena/fale-conosco',
} as const

export const LIBRARY = {
  email: 'biblioteca.barbacena@ifsudestemg.edu.br',
  /** Horário regular; em férias escolares o setor costuma ter horário reduzido. */
  hours: '07h às 20h',
} as const

/** Perfis oficiais do IF Sudeste MG nas redes sociais. */
export const SOCIAL_LINKS = [
  { name: 'Instagram', url: 'https://www.instagram.com/ifsudestemg' },
  { name: 'Facebook', url: 'https://www.facebook.com/institutofederalsudestemg' },
  { name: 'YouTube', url: 'https://www.youtube.com/user/IFSUDESTEMGVIDEOS' },
] as const

export const DEVELOPERS = [
  { name: 'Tainara RC Souza', url: 'https://github.com/tainararcs' },
  { name: 'Vinicius JP Silva', url: 'https://github.com/ViniciusJPSilva' },
] as const
