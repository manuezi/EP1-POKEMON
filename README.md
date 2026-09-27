# EP01 — ETL e Arquitetura Medalhão: Pokémon

**Integrantes:** Emanuelly Gomes, Gabriel Frasão.

---

## 1. Procedimento de execução

### 1.1 Pré-requisitos
- Python 3.11+
- MongoDB acessível (local, contêiner ou VM da disciplina)
- PostgreSQL acessível
- `pip install -r requirements.txt`

### 1.2 Variáveis de ambiente
```bash
export MONGO_URI="mongodb://localhost:27017"
export PG_DSN="dbname=pokedex user=postgres host=localhost"
```
Crie o banco `pokedex` no PostgreSQL antes de rodar (`createdb pokedex`); o MongoDB cria o banco `pokedex_bronze` automaticamente na primeira escrita.

### 1.3 Ordem de execução
```bash
python extrair.py     # fontes  -> bronze (MongoDB)
python carregar.py    # bronze  -> silver (PostgreSQL)
python publicar.py    # silver  -> gold   (PostgreSQL)
```
`sql/consultas.sql` pode então ser executado com `psql -d pokedex -f sql/consultas.sql`.

Cada script é idempotente e pode ser reexecutado livremente. `extrair.py`, na segunda execução, não realiza nenhuma requisição HTTP (usa o cache em `dados_brutos/`). `carregar.py` e `publicar.py` truncam e repovoam suas tabelas a cada execução.

---

## 2. Por que MongoDB na camada Bronze

A resposta de `/pokemon/{id}` é um JSON profundamente aninhado e de forma **irregular entre registros**: o array `stats[]` tem tamanho fixo, mas `abilities[]` e, principalmente, `varieties[]` (na resposta de espécie) têm cardinalidade variável entre Pokémon — uma espécie sem formas alternativas tem uma `variety`, outras têm até cinco. Forçar esse formato em uma tabela relacional na camada bronze exigiria decidir, já na extração, como achatar essas listas (uma tabela `pokemon_abilities` à parte? colunas `ability_1`, `ability_2`?) — e qualquer uma dessas decisões já é uma transformação, vedada nesta camada. Um banco de documentos armazena a resposta exatamente como veio, byte a byte, preservando a árvore original e adiando toda decisão estrutural para o `carregar.py`, que é onde ela pertence.

---

## 3. Grão da tabela fato e diagrama do esquema estrela

> **Grão de `silver.fato_confronto`: uma linha representa a participação de um Pokémon em um dos lados de um combate.** Cada combate de `combats.csv` gera exatamente duas linhas nesta tabela — uma por combatente —, totalizando 100.000 linhas para os 50.000 combates.

```
                         ┌──────────────────┐
                         │    dim_tipo      │
                         │  (18 + "Nenhum") │
                         └─────────┬────────┘
                                   │ tipo_primario_sk / tipo_secundario_sk
                                   │
      ┌────────────────────┐      │      ┌─────────────────────┐
      │    dim_pokemon      │◄────┴─────►│  efetividade_tipo    │
      │  (pokemon_sk = PK)  │             │ (atacante_sk,        │
      └──────────┬──────────┘             │  defensor_sk) -> mult│
                 │  pokemon_sk             └─────────────────────┘
                 │  oponente_sk (mesma dimensão, papel distinto)
                 ▼
      ┌───────────────────────────┐
      │    fato_confronto         │
      │  combate_id (degenerada)  │
      │  atacou_primeiro          │
      │  venceu (0/1)             │
      │  diferenca_velocidade     │
      └───────────────────────────┘
```

`dim_pokemon` é referenciada **duas vezes** pela fato (`pokemon_sk` e `oponente_sk`) — uma dimensão-papel (*role-playing dimension*), já que ambas as colunas apontam para a mesma tabela em papéis diferentes (o combatente e seu adversário).

`geracao`, `habitat`, `cor`, `forma_corporal` e `categoria_raridade` foram **denormalizados como colunas de `dim_pokemon`**, em vez de tabelas de dimensão próprias ligadas a `dim_pokemon` — isso seria snowflake (dimensão ligada a dimensão), vedado pela RS2. Como nenhuma dessas colunas precisa ser referenciada diretamente pela fato (nenhuma análise obrigatória agrupa por geração ligada à fato, exceto a análise proposta, que a acessa via `dim_pokemon`), a estrutura sugerida no enunciado (`dim_geracao` como ponto próprio da estrela) foi simplificada para uma coluna — divergência justificada pela ausência de necessidade de um FK direto da fato para geração.

---

## 4. As seis decisões de modelagem (seção 4.2)

**1) Grão da fato — participação (2 linhas/combate).**
Optamos pelo grão "uma linha por participação" em vez de "uma linha por combate". Com esse grão, a taxa de vitórias de qualquer agrupamento se reduz a `AVG(venceu)` sobre uma única coluna — exatamente o que RS6 exige. A alternativa (uma linha por combate, com `pokemon_a_sk`/`pokemon_b_sk`/`vencedor_sk`) exigiria, em toda consulta agregada, um `UNION` ou um `CASE` para verificar em qual das duas colunas cada Pokémon aparece, sob risco real de dupla contagem. O custo aceito foi dobrar o volume da fato (100.000 em vez de 50.000 linhas) — irrelevante na escala deste trabalho.

**2) Comparação entre os lados — `diferenca_velocidade` materializada na fato.**
A diferença de velocidade é gravada como coluna numérica na carga (`velocidade(pokemon) - velocidade(oponente)`), e não recalculada em cada consulta. Isso custa uma coluna extra por linha da fato, mas torna a análise 5 uma simples `GROUP BY` sobre uma métrica aditiva já pronta (RS6), sem exigir dois `JOIN`s com `dim_pokemon` na consulta final sobre o gold.

**3) Efetividade de tipos — tabela `efetividade_tipo` (bridge) usando apenas o tipo primário do defensor.**
Adotamos uma tabela-ponte com grão (tipo atacante, tipo defensor) → multiplicador, com os 4 valores da matriz original (0, 0,5, 1, 2). A análise 6 e a matriz da análise 7 usam o **tipo primário** de ambos os lados — não o multiplicador combinado dos dois tipos do defensor (que assumiria 6 valores possíveis). Essa simplificação foi escolhida porque o próprio combate, no dataset, não distingue "tipo do golpe usado" — as batalhas são decididas por comparação de status simulada, não por movimentos reais —, então a leitura mais direta e auditável da "vantagem de tipo" nesta base é a relação entre os tipos primários. Custo: a análise 6 não captura o efeito completo de defensores com dois tipos.

**4) Representação do oponente — dimensão-papel via segunda chave estrangeira.**
`oponente_sk` referencia `dim_pokemon` da mesma forma que `pokemon_sk`. Não criamos uma dimensão separada "dim_oponente": seria uma cópia integral de `dim_pokemon` sem necessidade, já que o oponente é a mesma entidade em outro papel.

**5) Atributos de status — residem em `dim_pokemon`; apenas a diferença de velocidade é duplicada na fato.**
Os seis atributos de status (HP, Ataque, Defesa, Ataque/Defesa Especial, Velocidade) descrevem o Pokémon e ficam em `dim_pokemon`, sua fonte de verdade. Duplicar todos os seis na fato não traria benefício, pois só a velocidade é usada nas análises obrigatórias (análise 5); por isso apenas sua diferença foi materializada (decisão 2), evitando duplicação desnecessária de espaço.

**6) Categoria de raridade — derivada na carga.**
`categoria_raridade` (`Comum` / `Lendário` / `Mítico` / `Bebê`) é calculada uma vez em `carregar.py`, a partir dos três booleanos da PokéAPI, e gravada como coluna. Resolver por `CASE` em cada consulta seria equivalente em resultado, mas repetiria a mesma lógica em toda consulta que precisasse da categoria; como a derivação é barata e estável, preferimos pagar o custo uma vez na carga.

---

## 5. Tipos excluídos (`stellar`, `unknown`, `shadow`)

`/type/` retorna 21 tipos, mas o dataset de batalhas (`pokemon.csv`, coluna `Type 1`/`Type 2`) só usa os 18 tipos reais do jogo em que essas batalhas se baseiam. `stellar` (introduzido em Scarlet/Violet), `unknown` (tipo "???" legado) e `shadow` (mecânica de jogos derivados) nunca aparecem como tipo de nenhum Pokémon em `pokemon.csv` e, portanto, nunca poderiam ser referenciados por `dim_pokemon.tipo_primario_sk`/`tipo_secundario_sk`. Foram excluídos de `dim_tipo` e de `efetividade_tipo` — incluí-los infl­aria a matriz sem que nenhuma linha do modelo os utilizasse.

---

## 6. Problemas 2 e 3 — por que exigem tratamentos distintos

- **Problema 2 (linha 63 sem nome):** dado **ausente** — a informação existe (o Pokémon é real, participa de combates), mas não foi registrada. Como o nome é a única chave de conciliação disponível (Problema 1), este registro **não pode ser conciliado com a PokéAPI**. Ele permanece em `dim_pokemon` com `nome = 'Desconhecido (#63)'`, `conciliado = FALSE`, `pokedex_numero = NULL` e atributos de espécie (`habitat`, `cor`, `forma_corporal`) em `NULL` — mas seus atributos de combate (tipo, status) vêm do próprio CSV e são preservados. Suas batalhas **não são descartadas** (R5): a fato referencia normalmente seu `pokemon_sk`.
- **Problema 3 (`habitat` nulo pós-geração III):** conceito **inaplicável** — não há ausência de dado a corrigir; o campo não existe no domínio para essas espécies. Por isso `habitat` permanece `NULL` sem qualquer sinalização adicional: é seu estado semanticamente correto, não uma falha de conciliação.

A distinção prática: no Problema 2, `conciliado = FALSE` sinaliza uma falha de processo; no Problema 3, `conciliado = TRUE` com `habitat IS NULL` é o resultado esperado e correto.

## 7. Conciliação de chaves (R4)

A conciliação (`carregar.py::conciliar`) tenta, nesta ordem: (1) um mapeamento manual explícito para as formas cujo nome no CSV não seria recuperável por regra simples (`Primal Kyogre`, `Deoxys Attack Forme`, `Wormadam Trash Cloak`, etc. — a lista completa do enunciado, seção 1.1); (2) uma regra específica para o padrão `Mega <Nome> [X|Y]`, reordenando para `<nome>-mega[-x|-y]`; (3) uma normalização genérica (minúsculas, espaços/pontuação → hífen); (4) como último recurso, aproximação por similaridade textual (`difflib`, corte de 85%). Registros que não conciliam por nenhuma dessas vias (apenas a linha 63, no cenário esperado) ficam com `conciliado = FALSE`. O relatório completo é escrito em `conciliacao.csv` a cada execução de `carregar.py`, com uma linha por registro do CSV, o método usado e o resultado.

## 8. Idempotência por camada

- **Bronze:** `upsert` (`replace_one` com `upsert=True`) usando `_id` = chave natural (`pokemon/25`, `pokemon_csv/63`, `combate/14032`). Reexecutar substitui o mesmo documento, nunca duplica. O cache em `dados_brutos/` impede novas requisições HTTP na segunda execução.
- **Silver/Gold:** `TRUNCATE` de todas as tabelas no início de `carregar.py`/`publicar.py`, seguido de repovoamento completo. Como `CREATE TABLE IF NOT EXISTS` só age na primeira execução, o padrão truncate-and-reload garante o mesmo estado final a cada execução, sem exigir lógica de upsert linha a linha em SQL.

## 9. Ambiente

MongoDB e PostgreSQL podem rodar na VM da disciplina, localmente ou em contêineres — o pipeline só depende das variáveis `MONGO_URI` e `PG_DSN`.

## 10. Análise proposta pelo grupo

**Pergunta:** a taxa de vitórias varia conforme a geração de origem do Pokémon? (Pokémon de gerações mais recentes tendem a ter status de cadastro mais altos, por design do jogo — isso se reflete nas batalhas simuladas?)

**Capacidade exigida e não coberta pelas análises 1–7:** nenhuma das tabelas gold anteriores agrupa por `geracao`; a única análise obrigatória que toca geração (análise 1) é sobre o cadastro, não sobre batalhas. `gold.taxa_vitorias_por_geracao` é a única tabela do gold cujo grão é "uma geração" cruzado com o resultado das batalhas.

Tabela: `gold.taxa_vitorias_por_geracao`. Resultado e interpretação em `RELATORIO.md`.

---