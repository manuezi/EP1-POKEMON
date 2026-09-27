"""
publicar.py — SILVER -> GOLD (PostgreSQL, agregação no próprio banco)

Responsabilidades (R8, seção 5.1):
  - Executar sql/gold.sql (DDL).
  - Repovoar cada tabela do gold com INSERT INTO ... SELECT ... FROM silver.*
    — a agregação é uma operação de conjunto, executada pelo PostgreSQL.
    Em nenhum momento os 100.000 registros da fato trafegam para a memória
    do processo Python (vedado pela seção 5.1 e pelo R11).
  - Ser idempotente (TRUNCATE + INSERT a cada execução).
  - Registrar a contagem de linhas resultante em cada tabela.

Uso:
    python publicar.py
"""

import os

import psycopg

PG_DSN = os.environ.get("PG_DSN", "dbname=pokedex user=postgres host=localhost")
SQL_DIR = os.path.join(os.path.dirname(__file__), "sql")

SQL_FAIXA_VELOCIDADE = """
    CASE
        WHEN diferenca_velocidade <= -50 THEN '1 - Muito mais lento (<= -50)'
        WHEN diferenca_velocidade <= -10 THEN '2 - Mais lento (-49 a -10)'
        WHEN diferenca_velocidade <  10  THEN '3 - Similar (-9 a 9)'
        WHEN diferenca_velocidade <  50  THEN '4 - Mais rápido (10 a 49)'
        ELSE                                  '5 - Muito mais rápido (>= 50)'
    END
"""

DDL_ORDEM_FAIXAS = {
    "1 - Muito mais lento (<= -50)": 1,
    "2 - Mais lento (-49 a -10)": 2,
    "3 - Similar (-9 a 9)": 3,
    "4 - Mais rápido (10 a 49)": 4,
    "5 - Muito mais rápido (>= 50)": 5,
}


def carregar_ddl(conn) -> None:
    with open(os.path.join(SQL_DIR, "gold.sql"), "r", encoding="utf-8") as f:
        ddl = f.read()
    with conn.cursor() as cur:
        cur.execute(ddl)
    conn.commit()


def limpar_tabelas(conn) -> None:
    tabelas = [
        "ranking_pokemon",
        "taxa_vitorias_por_tipo",
        "taxa_vitorias_por_faixa_velocidade",
        "taxa_vitorias_por_multiplicador",
        "matriz_confronto",
        "taxa_vitorias_por_geracao",
    ]
    with conn.cursor() as cur:
        for t in tabelas:
            cur.execute(f"TRUNCATE TABLE gold.{t}")
    conn.commit()


def publicar_ranking_pokemon(conn) -> None:
    with conn.cursor() as cur:
        cur.execute(
            """
            INSERT INTO gold.ranking_pokemon (pokemon_sk, nome, tipo_primario, combates, vitorias, taxa_vitorias)
            SELECT
                p.pokemon_sk,
                p.nome,
                t.nome,
                COUNT(*),
                SUM(f.venceu),
                AVG(f.venceu::numeric)
            FROM silver.fato_confronto f
            JOIN silver.dim_pokemon p ON p.pokemon_sk = f.pokemon_sk
            JOIN silver.dim_tipo t ON t.tipo_sk = p.tipo_primario_sk
            GROUP BY p.pokemon_sk, p.nome, t.nome
            """
        )
    conn.commit()


def publicar_taxa_por_tipo(conn) -> None:
    with conn.cursor() as cur:
        cur.execute(
            """
            INSERT INTO gold.taxa_vitorias_por_tipo (tipo, combates, vitorias, taxa_vitorias)
            SELECT
                t.nome,
                COUNT(*),
                SUM(f.venceu),
                AVG(f.venceu::numeric)
            FROM silver.fato_confronto f
            JOIN silver.dim_pokemon p ON p.pokemon_sk = f.pokemon_sk
            JOIN silver.dim_tipo t ON t.tipo_sk = p.tipo_primario_sk
            GROUP BY t.nome
            """
        )
    conn.commit()


def publicar_taxa_por_faixa_velocidade(conn) -> None:
    with conn.cursor() as cur:
        cur.execute(
            f"""
            SELECT {SQL_FAIXA_VELOCIDADE} AS faixa, COUNT(*), AVG(venceu::numeric)
            FROM silver.fato_confronto
            GROUP BY 1
            """
        )
        for faixa, combates, taxa in cur.fetchall():
            cur.execute(
                """
                INSERT INTO gold.taxa_vitorias_por_faixa_velocidade (faixa, ordem_faixa, combates, taxa_vitorias)
                VALUES (%s, %s, %s, %s)
                """,
                (faixa, DDL_ORDEM_FAIXAS[faixa], combates, taxa),
            )
    conn.commit()


def publicar_taxa_por_multiplicador(conn) -> None:
    with conn.cursor() as cur:
        cur.execute(
            """
            INSERT INTO gold.taxa_vitorias_por_multiplicador (multiplicador, combates, taxa_vitorias)
            SELECT
                e.multiplicador,
                COUNT(*),
                AVG(f.venceu::numeric)
            FROM silver.fato_confronto f
            JOIN silver.dim_pokemon eu ON eu.pokemon_sk = f.pokemon_sk
            JOIN silver.dim_pokemon adv ON adv.pokemon_sk = f.oponente_sk
            JOIN silver.efetividade_tipo e
                ON e.atacante_sk = eu.tipo_primario_sk
               AND e.defensor_sk = adv.tipo_primario_sk
            GROUP BY e.multiplicador
            """
        )
    conn.commit()


def publicar_matriz_confronto(conn) -> None:
    with conn.cursor() as cur:
        cur.execute(
            """
            INSERT INTO gold.matriz_confronto
                (tipo_atacante, tipo_defensor, combates, taxa_vitorias_atacante, multiplicador_efetividade, diverge)
            SELECT
                ta.nome,
                td.nome,
                COUNT(*),
                AVG(f.venceu::numeric),
                e.multiplicador,
                -- diverge: efetividade indica vantagem/desvantagem clara (<>1) mas a
                -- taxa observada não acompanha na mesma direção (ver análise 7 no README)
                (
                    (e.multiplicador > 1 AND AVG(f.venceu::numeric) <= 0.5) OR
                    (e.multiplicador < 1 AND AVG(f.venceu::numeric) >= 0.5)
                )
            FROM silver.fato_confronto f
            JOIN silver.dim_pokemon eu  ON eu.pokemon_sk  = f.pokemon_sk
            JOIN silver.dim_pokemon adv ON adv.pokemon_sk = f.oponente_sk
            JOIN silver.dim_tipo ta ON ta.tipo_sk = eu.tipo_primario_sk
            JOIN silver.dim_tipo td ON td.tipo_sk = adv.tipo_primario_sk
            JOIN silver.efetividade_tipo e
                ON e.atacante_sk = eu.tipo_primario_sk
               AND e.defensor_sk = adv.tipo_primario_sk
            GROUP BY ta.nome, td.nome, e.multiplicador
            """
        )
    conn.commit()


def publicar_taxa_por_geracao(conn) -> None:
    """Análise proposta pelo grupo: a geração de origem influencia a taxa de
    vitórias? Usa a dimensão 'geração' de dim_pokemon, não explorada por
    nenhuma das cinco tabelas anteriores (ver README.md)."""
    with conn.cursor() as cur:
        cur.execute(
            """
            INSERT INTO gold.taxa_vitorias_por_geracao (geracao, combates, taxa_vitorias)
            SELECT
                p.geracao,
                COUNT(*),
                AVG(f.venceu::numeric)
            FROM silver.fato_confronto f
            JOIN silver.dim_pokemon p ON p.pokemon_sk = f.pokemon_sk
            GROUP BY p.geracao
            """
        )
    conn.commit()


def main() -> None:
    with psycopg.connect(PG_DSN) as conn:
        carregar_ddl(conn)
        limpar_tabelas(conn)

        publicar_ranking_pokemon(conn)
        publicar_taxa_por_tipo(conn)
        publicar_taxa_por_faixa_velocidade(conn)
        publicar_taxa_por_multiplicador(conn)
        publicar_matriz_confronto(conn)
        publicar_taxa_por_geracao(conn)

        with conn.cursor() as cur:
            for tabela in [
                "ranking_pokemon",
                "taxa_vitorias_por_tipo",
                "taxa_vitorias_por_faixa_velocidade",
                "taxa_vitorias_por_multiplicador",
                "matriz_confronto",
                "taxa_vitorias_por_geracao",
            ]:
                cur.execute(f"SELECT COUNT(*) FROM gold.{tabela}")
                print(f"[publicar] gold.{tabela}: {cur.fetchone()[0]} linhas")

    print("[publicar] concluído.")


if __name__ == "__main__":
    main()
