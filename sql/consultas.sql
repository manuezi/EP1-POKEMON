-- ============================================================================
-- sql/consultas.sql — As 8 análises exigidas (R9)
--
-- Análises 1 e 2: sobre o cadastro, lidas diretamente do schema silver.
-- Análises 3 a 8: leitura direta de uma tabela já agregada do schema gold
-- (apenas WHERE / ORDER BY / LIMIT — nenhum GROUP BY, função de agregação
-- ou junção com o silver nesta consulta final).
-- ============================================================================

-- ----------------------------------------------------------------------------
-- Análise 1 — Quantidade de Pokémon por tipo primário e por geração
-- (matriz tipo x geração; verificação de consistência da conciliação)
-- ----------------------------------------------------------------------------
SELECT
    t.nome            AS tipo_primario,
    p.geracao,
    COUNT(*)          AS quantidade
FROM silver.dim_pokemon p
JOIN silver.dim_tipo t ON t.tipo_sk = p.tipo_primario_sk
GROUP BY t.nome, p.geracao
ORDER BY p.geracao, t.nome;

-- ----------------------------------------------------------------------------
-- Análise 2 — Média de cada atributo de status por tipo primário
-- ----------------------------------------------------------------------------
SELECT
    t.nome                          AS tipo_primario,
    ROUND(AVG(p.hp), 1)             AS hp_medio,
    ROUND(AVG(p.ataque), 1)         AS ataque_medio,
    ROUND(AVG(p.defesa), 1)         AS defesa_media,
    ROUND(AVG(p.ataque_especial), 1) AS ataque_especial_medio,
    ROUND(AVG(p.defesa_especial), 1) AS defesa_especial_media,
    ROUND(AVG(p.velocidade), 1)     AS velocidade_media
FROM silver.dim_pokemon p
JOIN silver.dim_tipo t ON t.tipo_sk = p.tipo_primario_sk
GROUP BY t.nome
ORDER BY velocidade_media DESC;

-- ----------------------------------------------------------------------------
-- Análise 3 — Taxa de vitórias por Pokémon: 10 maiores e 10 menores
-- Corte mínimo de combates: 20 (justificativa no README.md — abaixo disso,
-- a variância da taxa é dominada pelo tamanho da amostra, não pelo Pokémon).
-- ----------------------------------------------------------------------------
(
    SELECT nome, tipo_primario, combates, taxa_vitorias
    FROM gold.ranking_pokemon
    WHERE combates >= 20
    ORDER BY taxa_vitorias DESC, combates DESC
    LIMIT 10
)
UNION ALL
(
    SELECT nome, tipo_primario, combates, taxa_vitorias
    FROM gold.ranking_pokemon
    WHERE combates >= 20
    ORDER BY taxa_vitorias ASC, combates DESC
    LIMIT 10
);

-- ----------------------------------------------------------------------------
-- Análise 4 — Taxa de vitórias por tipo primário, ordenada
-- ----------------------------------------------------------------------------
SELECT tipo, combates, vitorias, taxa_vitorias
FROM gold.taxa_vitorias_por_tipo
ORDER BY taxa_vitorias DESC;

-- ----------------------------------------------------------------------------
-- Análise 5 — Relação entre diferença de velocidade e vitória
-- ----------------------------------------------------------------------------
SELECT faixa, combates, taxa_vitorias
FROM gold.taxa_vitorias_por_faixa_velocidade
ORDER BY ordem_faixa;

-- ----------------------------------------------------------------------------
-- Análise 6 — Relação entre vantagem de tipo (efetividade) e vitória
-- ----------------------------------------------------------------------------
SELECT multiplicador, combates, taxa_vitorias
FROM gold.taxa_vitorias_por_multiplicador
ORDER BY multiplicador;

-- ----------------------------------------------------------------------------
-- Análise 7 — Matriz de confronto 18x18: taxa observada x multiplicador,
-- e as posições em que os dois valores divergem
-- ----------------------------------------------------------------------------
SELECT tipo_atacante, tipo_defensor, combates, taxa_vitorias_atacante, multiplicador_efetividade
FROM gold.matriz_confronto
ORDER BY tipo_atacante, tipo_defensor;

-- posições divergentes (efetividade indica vantagem/desvantagem que a taxa não confirma)
SELECT tipo_atacante, tipo_defensor, combates, taxa_vitorias_atacante, multiplicador_efetividade
FROM gold.matriz_confronto
WHERE diverge = TRUE
ORDER BY combates DESC;

-- ----------------------------------------------------------------------------
-- Análise 8 (proposta pelo grupo) — Taxa de vitórias por geração de origem
-- Pergunta de negócio: Pokémon de gerações mais recentes (com stats em tese
-- mais "poderosos" no design do jogo) vencem mais? Usa a dimensão geração,
-- não explorada pelas análises 3 a 7.
-- ----------------------------------------------------------------------------
SELECT geracao, combates, taxa_vitorias
FROM gold.taxa_vitorias_por_geracao
ORDER BY geracao;
