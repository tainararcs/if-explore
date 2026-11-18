# Lógica do IF Explore

## Sincronização

`sync_catalog` roda a cada 6 h. Ele baixa o acervo inteiro e a situação dos exemplares do PHL e grava tudo numa transação só. Se a resposta vier truncada, nada é aplicado. Durante o sync, cada título recebe **área**, **cursos** e **gêneros**, calculados por funções puras em [classification.py](../backend/catalog/services/classification.py). As regras de curso e gênero são editáveis no admin e passam a valer no próximo sync.

### Área (uma por livro)

A área é decidida nesta ordem:

1. **Faixas da CDD que vencem o CNPq** (`CDD_AREA_OVERRIDES`): 004–006 vai para Tecnologia; 630–639 e 664 vão para Ciências Agrárias.
2. **Código CNPq** do registro, mapeado para uma área no admin.
3. **CDD como reserva** (`CDD_AREA_FALLBACK`), quando o CNPq está vazio ou é "9 = Outros".

### Curso (vários por livro)

O livro pertence a um curso quando:

- um dos seus códigos de bibliografia do PHL está nos `phl_codes` do curso; **ou**
- é um TCC cujo nome de curso, normalizado, bate com o curso.

Os códigos foram inferidos e ficam com `mapping_confirmed=False` até a biblioteca validar.

### Gênero (vários por livro)

O livro recebe um gênero quando:

- a classificação começa com um prefixo do gênero (ex.: `B869.1` para poesia); **ou**
- a CDD é literária (8xx, B869 ou 028.5) ou está vazia, **e** um assunto começa com uma palavra-chave do gênero. Essa trava evita que "MEMÓRIA RAM" vire biografia.

Detalhes:
- A CDD é comparada sem o prefixo de coleção (`CE`, `R`, `LIJ`), pela função `cdd_class`.
- Alguns gêneros também exigem um autor da lista, como "Clássicos brasileiros".

## Exemplares

- O sync lê a situação **resumida, em lote**, e [copy_status.py](../backend/catalog/services/copy_status.py) a converte num status do título.
- A página do livro consulta o PHL **ao vivo** quando o dado tem mais de 15 min, em [availability.py](../backend/catalog/services/availability.py). Se o PHL falhar ou o banco estiver travado pelo sync, a página mostra o dado guardado.

## Recomendações (sem IA)

Ficam em [recommendations.py](../backend/catalog/services/recommendations.py).

- **Candidatos** (`recommendable()`): livros, e-books, audiolivros e TCCs ativos. Ficam de fora os títulos com todos os exemplares indisponíveis e os que não têm exemplar nem link.
- **Afinidade entre livros** (relacionados e parecidos): autor em comum +3, assunto em comum +2, gênero +1 e mesma área +1.
- **Desempate:** livros com capa primeiro, depois os com mais exemplares.

### Prateleiras da home

A home tem três prateleiras, nesta ordem:

1. **Dos seus gêneros:** livros dos gêneros escolhidos, intercalados entre os gêneros. A ordem considera o perfil inteiro: curso +4, área +2, gênero +1,5 e +1 por assunto em comum com os 3 livros escolhidos.
2. **Escolhidos para você:** só curso (+4) e área (+2).
3. **Parecidos com os que você escolheu:** a afinidade dos 3 livros do onboarding, intercalada.

Regras gerais:
- Cada livro aparece uma vez só na página, e os livros escolhidos nunca voltam.
- Prateleiras com menos de 3 livros são descartadas. Por exemplo, sem gêneros escolhidos a primeira não aparece.
- No celular, as três usam o carrossel com um livro em destaque.

### Seed (`shuffleSeed`)

É um número aleatório que o frontend gera e guarda no `sessionStorage`. Ele vai em cada pedido das prateleiras, e o backend o usa para sortear a ordem entre os ~40 melhores candidatos de cada prateleira, com mais chance para os de maior pontuação.

- **A mesma seed dá as mesmas prateleiras**, então voltar de um livro mantém a home como estava.
- **A seed muda** numa visita nova ou ao clicar em "Ver outras sugestões", que fica centralizado abaixo das prateleiras.
- **Sem seed**, a API devolve a ordem de relevância pura.

## Sugestões da IA (Gemini)

O cálculo fica em [discovery.py](../backend/catalog/services/discovery.py), e a rota é `POST /api/recommendations/ai`.

- **Na home:** uma prateleira em destaque no topo. O visitante clica em "Pedir sugestões à IA" e recebe **3 livros, um de cada prateleira**, cada um com o motivo da escolha e a prateleira de onde veio.
- **Candidatos:** até 12 por prateleira, saídos do acervo local, sem repetir o que já está em "Escolhidos para você" nem as sugestões anteriores. A IA só escolhe e explica; nunca busca no catálogo nem inventa títulos.
- **Privacidade:** a IA recebe só o perfil anônimo (nomes das áreas, cursos e gêneros e os títulos escolhidos). Nenhum id vai para ela, e nada é gravado nem registrado em log.
- **Falhas:** se a IA errar um grupo, entra o primeiro candidato daquela prateleira, sem motivo. Se a IA estiver fora do ar, a home mostra um aviso em vez de uma prateleira repetida.
- **Custo:** 1 chamada ao Gemini por clique. A prateleira fica guardada na sessão, então voltar à home não gera chamada nova.

A IA também gera a explicação simplificada na página do livro, guardada no banco depois da primeira vez.

## Catálogo completo

A aba `/catalog` substitui o antigo `/discover`. Ela tem busca, ordenação e filtros (tipo, disponibilidade, área, curso, gênero, idioma e ano), num painel que abre pelo botão "Filtros", e guarda tudo na URL. Os filtros não mostram contagens por opção: elas atrasavam cada seleção. As opções de idioma vêm de `GET /api/languages`. Os equipamentos (chave, fone, computador) nunca aparecem.

## Para aprofundar

- [backend/docs/project-guidelines.md](../backend/docs/project-guidelines.md): convenções do sync, dos dados, da API e da IA
- [backend/README.md](../backend/README.md): comandos, variáveis e endpoints
- [.claude/skills/home-view/SKILL.md](../.claude/skills/home-view/SKILL.md): layout da home e prateleira da IA
- [.claude/skills/catalog-view/SKILL.md](../.claude/skills/catalog-view/SKILL.md): catálogo completo e filtros
- [.claude/skills/ai-discovery-api/SKILL.md](../.claude/skills/ai-discovery-api/SKILL.md): regras da IA e contrato
