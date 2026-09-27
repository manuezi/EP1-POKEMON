-- ============================================================================
-- sql/gold.sql — Tabelas agregadas de consumo (camada Gold)
--
-- Cada tabela já está no grão da pergunta correspondente. As consultas
-- finais (sql/consultas.sql) fazem apenas SELECT / WHERE / ORDER BY / LIMIT
-- sobre estas tabelas — nenhuma agregação ocorre na consulta final.
-- Populadas por publicar.py com INSERT INTO ... SELECT ... FROM silver.*
-- (agregação executada pelo PostgreSQL, não pelo processo Python).
-- ============================================================================

CREATE SCHEMA IF NOT EXISTS gold;

-- Análise 3 — taxa de vitórias por Pokémon
CREATE TABLE IF NOT EXISTS gold.ranking_pokemon (
    pokemon_sk       INTEGER PRIMARY KEY,
    nome             VARCHAR(60) NOT NULL,
    tipo_primario    VARCHAR(20) NOT NULL,
    combates         INTEGER NOT NULL,   -- corte mínimo é aplicado na consulta, não aqui
    vitorias         INTEGER NOT NULL,
    taxa_vitorias    NUMERIC(5,4) NOT NULL
);

-- Análise 4 — taxa de vitórias por tipo primário
CREATE TABLE IF NOT EXISTS gold.taxa_vitorias_por_tipo (
    tipo             VARCHAR(20) PRIMARY KEY,
    combates         INTEGER NOT NULL,
    vitorias         INTEGER NOT NULL,
    taxa_vitorias    NUMERIC(5,4) NOT NULL
);

-- Análise 5 — relação entre diferença de velocidade e vitória
CREATE TABLE IF NOT EXISTS gold.taxa_vitorias_por_faixa_velocidade (
    faixa            VARCHAR(30) PRIMARY KEY,
    ordem_faixa      INTEGER NOT NULL,   -- para ORDER BY na consulta, sem recalcular
    combates         INTEGER NOT NULL,
    taxa_vitorias    NUMERIC(5,4) NOT NULL
);

-- Análise 6 — relação entre vantagem de tipo e vitória
CREATE TABLE IF NOT EXISTS gold.taxa_vitorias_por_multiplicador (
    multiplicador    NUMERIC(3,2) PRIMARY KEY,
    combates         INTEGER NOT NULL,
    taxa_vitorias    NUMERIC(5,4) NOT NULL
);

-- Análise 7 — matriz de confronto 18x18
CREATE TABLE IF NOT EXISTS gold.matriz_confronto (
    tipo_atacante              VARCHAR(20) NOT NULL,
    tipo_defensor              VARCHAR(20) NOT NULL,
    combates                   INTEGER NOT NULL,
    taxa_vitorias_atacante     NUMERIC(5,4) NOT NULL,
    multiplicador_efetividade  NUMERIC(3,2) NOT NULL,
    diverge                    BOOLEAN NOT NULL,  -- TRUE quando taxa e multiplicador discordam de direção
    PRIMARY KEY (tipo_atacante, tipo_defensor)
);

-- Análise 8 (proposta pelo grupo) — taxa de vitórias por geração
-- Usa a dimensão "geração", não utilizada por nenhuma das 5 tabelas acima.
CREATE TABLE IF NOT EXISTS gold.taxa_vitorias_por_geracao (
    geracao          INTEGER PRIMARY KEY,
    combates         INTEGER NOT NULL,
    taxa_vitorias    NUMERIC(5,4) NOT NULL
);
