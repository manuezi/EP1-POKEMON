-- ============================================================================
-- sql/silver.sql — Modelo dimensional da camada Silver
--
-- Grão da fato: uma linha por PARTICIPAÇÃO em um combate (duas linhas por
-- combate — uma para cada lado). Ver justificativa da decisão 1 no README.md.
--
-- Executado por carregar.py, sempre nesta ordem (dimensões antes da fato).
-- ============================================================================

CREATE SCHEMA IF NOT EXISTS silver;

-- ----------------------------------------------------------------------------
-- dim_tipo — os 18 tipos reais do jogo + 1 membro especial ("Nenhum"),
-- usado quando um Pokémon não possui tipo secundário (RS4).
-- stellar/unknown/shadow (ids 19, 10001, 10002 da PokéAPI) são excluídos:
-- não existem no jogo que originou o dataset de batalhas (ver README, seção
-- "tipos excluídos").
-- ----------------------------------------------------------------------------
CREATE TABLE IF NOT EXISTS silver.dim_tipo (
    tipo_sk        SERIAL PRIMARY KEY,
    tipo_pokeapi_id INTEGER NULL,          -- chave natural da PokéAPI; NULL no membro especial
    nome           VARCHAR(20) NOT NULL UNIQUE
);

-- ----------------------------------------------------------------------------
-- dim_pokemon — um Pokémon (linha do pokemon.csv) já conciliado com a
-- PokéAPI quando possível. Chaves naturais preservadas como atributos (RS3).
-- ----------------------------------------------------------------------------
CREATE TABLE IF NOT EXISTS silver.dim_pokemon (
    pokemon_sk          SERIAL PRIMARY KEY,
    csv_numero          INTEGER NOT NULL UNIQUE,   -- campo # do pokemon.csv (chave natural)
    pokedex_numero      INTEGER NULL,              -- número da Pokédex, quando conciliado
    nome                VARCHAR(60) NOT NULL,      -- 'Desconhecido (#63)' quando ausente na fonte
    tipo_primario_sk    INTEGER NOT NULL REFERENCES silver.dim_tipo(tipo_sk),
    tipo_secundario_sk  INTEGER NOT NULL REFERENCES silver.dim_tipo(tipo_sk), -- aponta p/ membro especial "Nenhum" quando ausente
    hp                  INTEGER NOT NULL,
    ataque              INTEGER NOT NULL,
    defesa              INTEGER NOT NULL,
    ataque_especial     INTEGER NOT NULL,
    defesa_especial     INTEGER NOT NULL,
    velocidade          INTEGER NOT NULL,
    geracao             INTEGER NOT NULL,          -- denormalizado (evita snowflake, RS2)
    lendario            BOOLEAN NOT NULL DEFAULT FALSE,
    mitico              BOOLEAN NOT NULL DEFAULT FALSE,
    bebe                BOOLEAN NOT NULL DEFAULT FALSE,
    categoria_raridade  VARCHAR(20) NOT NULL,      -- 'Comum' | 'Lendário' | 'Mítico' | 'Bebê' (decisão 6)
    habitat             VARCHAR(30) NULL,           -- NULL = conceito inexistente p/ geração (Problema 3, seção 1.4)
    cor                 VARCHAR(20) NULL,
    forma_corporal      VARCHAR(20) NULL,
    e_forma_alternativa BOOLEAN NOT NULL DEFAULT FALSE,
    conciliado          BOOLEAN NOT NULL DEFAULT TRUE,  -- FALSE = não localizado na PokéAPI (R4)
    metodo_conciliacao  VARCHAR(20) NULL            -- 'exato' | 'manual' | 'aproximado' | NULL
);

-- ----------------------------------------------------------------------------
-- efetividade_tipo — a matriz de efetividade de 18x18, materializada para
-- ser consultável em SQL (RS7). PK composta = grão da tabela.
-- ----------------------------------------------------------------------------
CREATE TABLE IF NOT EXISTS silver.efetividade_tipo (
    atacante_sk   INTEGER NOT NULL REFERENCES silver.dim_tipo(tipo_sk),
    defensor_sk   INTEGER NOT NULL REFERENCES silver.dim_tipo(tipo_sk),
    multiplicador NUMERIC(3,2) NOT NULL,   -- 0, 0.5, 1 ou 2
    PRIMARY KEY (atacante_sk, defensor_sk)
);

-- ----------------------------------------------------------------------------
-- fato_confronto — grão: uma participação de um Pokémon em um combate.
-- "oponente_sk" é uma dimensão-papel: referencia dim_pokemon em papel
-- distinto de pokemon_sk (mesmo Pokémon do combate, do lado do adversário).
-- Cada combate de combats.csv gera exatamente DUAS linhas aqui.
-- ----------------------------------------------------------------------------
CREATE TABLE IF NOT EXISTS silver.fato_confronto (
    confronto_sk         BIGSERIAL PRIMARY KEY,
    combate_id           INTEGER NOT NULL,     -- dimensão degenerada: nº da linha em combats.csv
    pokemon_sk           INTEGER NOT NULL REFERENCES silver.dim_pokemon(pokemon_sk),
    oponente_sk          INTEGER NOT NULL REFERENCES silver.dim_pokemon(pokemon_sk),
    atacou_primeiro      BOOLEAN NOT NULL,
    venceu               SMALLINT NOT NULL,    -- 1/0 numérico -> AVG() = taxa de vitórias (RS6, seção 1.3)
    diferenca_velocidade INTEGER NOT NULL      -- velocidade(pokemon) - velocidade(oponente); métrica materializada (decisão 2)
);

CREATE INDEX IF NOT EXISTS ix_fato_confronto_pokemon  ON silver.fato_confronto(pokemon_sk);
CREATE INDEX IF NOT EXISTS ix_fato_confronto_oponente ON silver.fato_confronto(oponente_sk);
CREATE INDEX IF NOT EXISTS ix_fato_confronto_combate  ON silver.fato_confronto(combate_id);
