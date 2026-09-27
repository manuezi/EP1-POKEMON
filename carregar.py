"""
carregar.py — BRONZE -> SILVER (PostgreSQL)

Responsabilidades (R4, R5, R6, R7):
  - Ler exclusivamente da camada bronze (MongoDB). Nunca acessa a PokéAPI
    nem os arquivos CSV originais (verificado na correção com a rede
    desligada).
  - Conciliar o campo # do pokemon.csv com o número da Pokédex, por nome
    (Problema 1, seção 1.4).
  - Executar sql/silver.sql (DDL) e popular as tabelas do esquema estrela.
  - Ser idempotente: TRUNCATE + INSERT a cada execução, sem duplicar linhas.
  - Emitir conciliacao.csv (R4).

Uso:
    python carregar.py
"""

import csv
import difflib
import os
import re

import psycopg
from pymongo import MongoClient

MONGO_URI = os.environ.get("MONGO_URI", "mongodb://localhost:27017")
MONGO_DB = "pokedex_bronze"
PG_DSN = os.environ.get("PG_DSN", "dbname=pokedex user=postgres host=localhost")

SQL_DIR = os.path.join(os.path.dirname(__file__), "sql")

TIPOS_EXCLUIDOS_POKEAPI_ID = {19, 10001, 10002}

MAPEAMENTO_MANUAL = {
    "Primal Kyogre": "kyogre-primal",
    "Primal Groudon": "groudon-primal",
    "Deoxys Attack Forme": "deoxys-attack",
    "Deoxys Defense Forme": "deoxys-defense",
    "Deoxys Speed Forme": "deoxys-speed",
    "Giratina Altered Forme": "giratina-altered",
    "Giratina Origin Forme": "giratina-origin",
    "Shaymin Sky Forme": "shaymin-sky",
    "Tornadus Therian Forme": "tornadus-therian",
    "Thundurus Therian Forme": "thundurus-therian",
    "Landorus Therian Forme": "landorus-therian",
    "Kyurem Black": "kyurem-black",
    "Kyurem White": "kyurem-white",
    "Keldeo Resolute Forme": "keldeo-resolute",
    "Meloetta Pirouette Forme": "meloetta-pirouette",
    "Darmanitan Zen Mode": "darmanitan-zen",
    "Wormadam Trash Cloak": "wormadam-trash",
    "Wormadam Sandy Cloak": "wormadam-sandy",
    "Wormadam Plant Cloak": "wormadam-plant",
    "Pumpkaboo Small Size": "pumpkaboo-small",
    "Pumpkaboo Large Size": "pumpkaboo-large",
    "Pumpkaboo Super Size": "pumpkaboo-super",
    "Gourgeist Small Size": "gourgeist-small",
    "Gourgeist Large Size": "gourgeist-large",
    "Gourgeist Super Size": "gourgeist-super",
    "Aegislash Blade Forme": "aegislash-blade",
    "Aegislash Shield Forme": "aegislash-shield",
    "Hoopa Unbound": "hoopa-unbound",
}

_RE_MEGA = re.compile(r"^Mega (.+?)( X| Y)?$")


def slugify_padrao(nome: str) -> str:
    """Normalização genérica: minúsculas, espaços -> hífen, remove pontuação."""
    s = nome.strip().lower()
    s = re.sub(r"[.'’]", "", s)
    s = re.sub(r"[^a-z0-9]+", "-", s)
    return s.strip("-")


def candidatos_slug(nome_csv: str) -> list:
    """Gera candidatos de slug PokeAPI a partir do nome do CSV, na ordem de
    preferência: mapeamento manual, reordenação de 'Mega X/Y', slug padrão."""
    candidatos = []

    if nome_csv in MAPEAMENTO_MANUAL:
        candidatos.append(MAPEAMENTO_MANUAL[nome_csv])

    m = _RE_MEGA.match(nome_csv)
    if m:
        base, sufixo = m.group(1), (m.group(2) or "").strip().lower()
        base_slug = slugify_padrao(base)
        candidatos.append(f"{base_slug}-mega-{sufixo}" if sufixo else f"{base_slug}-mega")

    candidatos.append(slugify_padrao(nome_csv))
    return candidatos


def conciliar(nome_csv: str, nomes_pokeapi: set, nomes_pokeapi_lista: list):
    """Retorna (slug_pokeapi_ou_None, metodo) para um nome do CSV."""
    if not nome_csv or not nome_csv.strip():
        return None, None  # Problema 2: linha 63 sem nome — não conciliável por nome

    for slug in candidatos_slug(nome_csv):
        if slug in nomes_pokeapi:
            metodo = "manual" if nome_csv in MAPEAMENTO_MANUAL else "exato"
            return slug, metodo

    # último recurso: aproximação por similaridade textual
    slug_base = slugify_padrao(nome_csv)
    aproximados = difflib.get_close_matches(slug_base, nomes_pokeapi_lista, n=1, cutoff=0.85)
    if aproximados:
        return aproximados[0], "aproximado"

    return None, None


def categoria_raridade(is_legendary: bool, is_mythical: bool, is_baby: bool) -> str:
    if is_mythical:
        return "Mítico"
    if is_legendary:
        return "Lendário"
    if is_baby:
        return "Bebê"
    return "Comum"


def carregar_ddl(pg_conn) -> None:
    with open(os.path.join(SQL_DIR, "silver.sql"), "r", encoding="utf-8") as f:
        ddl = f.read()
    with pg_conn.cursor() as cur:
        cur.execute(ddl)
    pg_conn.commit()


def limpar_tabelas(pg_conn) -> None:
    """Trunca na ordem inversa de dependência — garante reexecução idempotente."""
    with pg_conn.cursor() as cur:
        cur.execute("TRUNCATE TABLE silver.fato_confronto RESTART IDENTITY;")
        cur.execute("TRUNCATE TABLE silver.efetividade_tipo;")
        cur.execute("TRUNCATE TABLE silver.dim_pokemon RESTART IDENTITY CASCADE;")
        cur.execute("TRUNCATE TABLE silver.dim_tipo RESTART IDENTITY CASCADE;")
    pg_conn.commit()


def carregar_dim_tipo(pg_conn, tipos_bronze: list) -> dict:
    """Retorna dict nome_tipo -> tipo_sk. Inclui o membro especial 'Nenhum'."""
    mapa = {}
    with pg_conn.cursor() as cur:
        cur.execute(
            "INSERT INTO silver.dim_tipo (tipo_pokeapi_id, nome) VALUES (NULL, 'Nenhum') RETURNING tipo_sk"
        )
        mapa["nenhum"] = cur.fetchone()[0]

        for doc in tipos_bronze:
            if doc.get("id") in TIPOS_EXCLUIDOS_POKEAPI_ID:
                continue
            cur.execute(
                "INSERT INTO silver.dim_tipo (tipo_pokeapi_id, nome) VALUES (%s, %s) RETURNING tipo_sk",
                (doc["id"], doc["name"]),
            )
            mapa[doc["name"]] = cur.fetchone()[0]
    pg_conn.commit()
    return mapa


def carregar_dim_pokemon(pg_conn, db, mapa_tipo: dict):
    """Concilia pokemon_csv <-> pokemon/especies da PokéAPI e popula
    silver.dim_pokemon. Retorna (mapa_csv_numero_para_sk, linhas_conciliacao)."""

    pokemon_docs = {d["name"]: d for d in db["pokemon"].find({})}
    especies_docs = {d["id"]: d for d in db["especies"].find({})}
    nomes_pokeapi = set(pokemon_docs.keys())
    nomes_pokeapi_lista = list(nomes_pokeapi)

    mapa_csv_sk = {}
    linhas_conciliacao = []

    with pg_conn.cursor() as cur:
        for csv_doc in db["pokemon_csv"].find({}).sort("_id", 1):
            numero = int(csv_doc["#"])
            nome_csv = csv_doc.get("Name") or ""

            slug, metodo = conciliar(nome_csv, nomes_pokeapi, nomes_pokeapi_lista)
            pokeapi_pokemon = pokemon_docs.get(slug) if slug else None
            especie = None
            if pokeapi_pokemon is not None:
                especie = especies_docs.get(pokeapi_pokemon.get("_especie_id"))

            if pokeapi_pokemon is not None:
                nome_final = nome_csv
                pokedex_numero = pokeapi_pokemon["_especie_id"]
                e_forma_alt = not pokeapi_pokemon.get("is_default", True)
                geracao = int(especie["generation"]["url"].rstrip("/").split("/")[-1]) if especie else 0
                habitat = especie["habitat"]["name"] if (especie and especie.get("habitat")) else None
                cor = especie["color"]["name"] if (especie and especie.get("color")) else None
                forma = especie["shape"]["name"] if (especie and especie.get("shape")) else None
                lendario = bool(especie["is_legendary"]) if especie else False
                mitico = bool(especie["is_mythical"]) if especie else False
                bebe = bool(especie["is_baby"]) if especie else False
                conciliado = True
            else:
                nome_final = nome_csv.strip() or f"Desconhecido (#{numero})"
                pokedex_numero = None
                e_forma_alt = False
                geracao = int(csv_doc.get("Generation") or 0)
                habitat = None
                cor = None
                forma = None
                lendario = str(csv_doc.get("Legendary", "")).strip().lower() == "true"
                mitico = False
                bebe = False
                conciliado = False
                metodo = None

            tipo1_nome = (csv_doc.get("Type 1") or "").strip().lower()
            tipo2_nome = (csv_doc.get("Type 2") or "").strip().lower()
            tipo1_sk = mapa_tipo.get(tipo1_nome, mapa_tipo["nenhum"])
            tipo2_sk = mapa_tipo.get(tipo2_nome, mapa_tipo["nenhum"]) if tipo2_nome else mapa_tipo["nenhum"]

            cur.execute(
                """
                INSERT INTO silver.dim_pokemon (
                    csv_numero, pokedex_numero, nome, tipo_primario_sk, tipo_secundario_sk,
                    hp, ataque, defesa, ataque_especial, defesa_especial, velocidade,
                    geracao, lendario, mitico, bebe, categoria_raridade,
                    habitat, cor, forma_corporal, e_forma_alternativa,
                    conciliado, metodo_conciliacao
                ) VALUES (
                    %s, %s, %s, %s, %s,
                    %s, %s, %s, %s, %s, %s,
                    %s, %s, %s, %s, %s,
                    %s, %s, %s, %s,
                    %s, %s
                ) RETURNING pokemon_sk
                """,
                (
                    numero, pokedex_numero, nome_final, tipo1_sk, tipo2_sk,
                    int(csv_doc["HP"]), int(csv_doc["Attack"]), int(csv_doc["Defense"]),
                    int(csv_doc["Sp. Atk"]), int(csv_doc["Sp. Def"]), int(csv_doc["Speed"]),
                    geracao, lendario, mitico, bebe,
                    categoria_raridade(lendario, mitico, bebe),
                    habitat, cor, forma, e_forma_alt,
                    conciliado, metodo,
                ),
            )
            sk = cur.fetchone()[0]
            mapa_csv_sk[numero] = sk

            linhas_conciliacao.append(
                {
                    "csv_numero": numero,
                    "nome_csv": nome_csv,
                    "conciliado": conciliado,
                    "metodo": metodo or "",
                    "pokedex_numero": pokedex_numero or "",
                }
            )
    pg_conn.commit()
    return mapa_csv_sk, linhas_conciliacao


def carregar_efetividade_tipo(pg_conn, db, mapa_tipo: dict) -> None:
    """Materializa a matriz 18x18 a partir de damage_relations (RS7)."""
    tipos_por_nome = {d["name"]: d for d in db["tipos"].find({})}
    nomes_reais = [n for n in mapa_tipo if n != "nenhum"]

    with pg_conn.cursor() as cur:
        for atacante in nomes_reais:
            doc = tipos_por_nome[atacante]
            relacoes = doc["damage_relations"]
            dobro = {t["name"] for t in relacoes["double_damage_to"]}
            metade = {t["name"] for t in relacoes["half_damage_to"]}
            nulo = {t["name"] for t in relacoes["no_damage_to"]}

            for defensor in nomes_reais:
                if defensor in nulo:
                    mult = 0
                elif defensor in dobro:
                    mult = 2
                elif defensor in metade:
                    mult = 0.5
                else:
                    mult = 1
                cur.execute(
                    "INSERT INTO silver.efetividade_tipo (atacante_sk, defensor_sk, multiplicador) VALUES (%s, %s, %s)",
                    (mapa_tipo[atacante], mapa_tipo[defensor], mult),
                )
    pg_conn.commit()


def carregar_fato_confronto(pg_conn, db, mapa_csv_sk: dict) -> None:
    velocidade_por_sk = {}
    with pg_conn.cursor() as cur:
        cur.execute("SELECT pokemon_sk, velocidade FROM silver.dim_pokemon")
        for sk, vel in cur.fetchall():
            velocidade_por_sk[sk] = vel

        registros = 0
        for i, combate in enumerate(db["combates"].find({}).sort("_id", 1), start=1):
            n1 = int(combate["First_pokemon"])
            n2 = int(combate["Second_pokemon"])
            vencedor = int(combate["Winner"])

            sk1, sk2 = mapa_csv_sk.get(n1), mapa_csv_sk.get(n2)
            if sk1 is None or sk2 is None:
                continue  # não deveria ocorrer se a extração/conciliação está completa

            v1 = velocidade_por_sk[sk1]
            v2 = velocidade_por_sk[sk2]

            linhas = [
                (i, sk1, sk2, True,  1 if vencedor == n1 else 0, v1 - v2),
                (i, sk2, sk1, False, 1 if vencedor == n2 else 0, v2 - v1),
            ]
            cur.executemany(
                """
                INSERT INTO silver.fato_confronto
                    (combate_id, pokemon_sk, oponente_sk, atacou_primeiro, venceu, diferenca_velocidade)
                VALUES (%s, %s, %s, %s, %s, %s)
                """,
                linhas,
            )
            registros += 2
    pg_conn.commit()
    print(f"[carregar] fato_confronto: {registros} linhas (esperado: 100000, ~2x 50000 combates)")


def escrever_conciliacao_csv(linhas: list) -> None:
    caminho = os.path.join(os.path.dirname(__file__), "conciliacao.csv")
    with open(caminho, "w", newline="", encoding="utf-8") as f:
        w = csv.DictWriter(f, fieldnames=["csv_numero", "nome_csv", "conciliado", "metodo", "pokedex_numero"])
        w.writeheader()
        w.writerows(linhas)

    total = len(linhas)
    conciliados = sum(1 for l in linhas if l["conciliado"])
    print(f"[carregar] conciliacao.csv: {conciliados}/{total} registros conciliados")


def main() -> None:
    mongo = MongoClient(MONGO_URI)
    db = mongo[MONGO_DB]

    with psycopg.connect(PG_DSN) as pg_conn:
        carregar_ddl(pg_conn)
        limpar_tabelas(pg_conn)

        tipos_bronze = list(db["tipos"].find({}))
        mapa_tipo = carregar_dim_tipo(pg_conn, tipos_bronze)

        mapa_csv_sk, linhas_conciliacao = carregar_dim_pokemon(pg_conn, db, mapa_tipo)
        escrever_conciliacao_csv(linhas_conciliacao)

        carregar_efetividade_tipo(pg_conn, db, mapa_tipo)
        carregar_fato_confronto(pg_conn, db, mapa_csv_sk)

        with pg_conn.cursor() as cur:
            for tabela in ["dim_tipo", "dim_pokemon", "efetividade_tipo", "fato_confronto"]:
                cur.execute(f"SELECT COUNT(*) FROM silver.{tabela}")
                print(f"[carregar] silver.{tabela}: {cur.fetchone()[0]} linhas")

    print("[carregar] concluído.")


if __name__ == "__main__":
    main()
