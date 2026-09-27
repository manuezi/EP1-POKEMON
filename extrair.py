"""
extrair.py — FONTES -> BRONZE (MongoDB)

Responsabilidades (R1, R2, R3):
  - Consultar a PokéAPI (pokemon, pokemon-species, type) para as gerações I-VI
    (721 espécies) e TODAS as formas alternativas (varieties[]).
  - Baixar pokemon.csv e combats.csv e carregar linha a linha.
  - Gravar cada documento na camada bronze SEM QUALQUER TRANSFORMAÇÃO,
    com metadados de linhagem (_fonte, _url/_arquivo, _ingerido_em).
  - Cache em disco em dados_brutos/, consultado antes de qualquer requisição
    HTTP. Na segunda execução, com o cache presente, zero requisições são
    realizadas (verificado pela correção).

Uso:
    python extrair.py
"""

import csv
import io
import json
import os
import time
from datetime import datetime, timezone

import requests
from pymongo import MongoClient

MONGO_URI = os.environ.get("MONGO_URI", "mongodb://localhost:27017")
DB_NAME = "pokedex_bronze"

POKEAPI_BASE = "https://pokeapi.co/api/v2"
POKEMON_CSV_URL = (
    "https://raw.githubusercontent.com/cdiener/pokemon_app/master/pokemon.csv"
)
COMBATS_CSV_URL = (
    "https://raw.githubusercontent.com/cdiener/pokemon_app/master/combats.csv"
)

CACHE_DIR = "dados_brutos"
SLEEP_BETWEEN_REQUESTS = 0.1

N_ESPECIES = 721

TIPO_IDS = list(range(1, 20)) + [10001, 10002]

session = requests.Session()


def _agora_iso() -> str:
    return datetime.now(timezone.utc).isoformat()


def _cache_path(*parts: str) -> str:
    return os.path.join(CACHE_DIR, *parts)


def obter_json(url: str, cache_rel_path: str) -> dict:
    """Retorna o JSON de `url`, usando o cache em disco quando disponível.

    Só realiza requisição HTTP quando o arquivo de cache correspondente
    não existe. Isso garante que a segunda execução do script não gere
    novas requisições à API (requisito verificado na correção).
    """
    caminho = _cache_path(cache_rel_path)
    if os.path.exists(caminho):
        with open(caminho, "r", encoding="utf-8") as f:
            return json.load(f)

    resp = session.get(url, timeout=30)
    resp.raise_for_status()
    dado = resp.json()

    os.makedirs(os.path.dirname(caminho), exist_ok=True)
    with open(caminho, "w", encoding="utf-8") as f:
        json.dump(dado, f, ensure_ascii=False)

    time.sleep(SLEEP_BETWEEN_REQUESTS)
    return dado


def obter_texto(url: str, cache_rel_path: str) -> str:
    caminho = _cache_path(cache_rel_path)
    if os.path.exists(caminho):
        with open(caminho, "r", encoding="utf-8") as f:
            return f.read()

    resp = session.get(url, timeout=60)
    resp.raise_for_status()
    texto = resp.text

    os.makedirs(os.path.dirname(caminho), exist_ok=True)
    with open(caminho, "w", encoding="utf-8") as f:
        f.write(texto)

    return texto


def upsert(colecao, _id: str, documento: dict) -> None:
    """Upsert por chave natural — garante idempotência (R3)."""
    documento = dict(documento)
    documento["_id"] = _id
    colecao.replace_one({"_id": _id}, documento, upsert=True)


def extrair_tipos(db) -> None:
    colecao = db["tipos"]
    for tipo_id in TIPO_IDS:
        url = f"{POKEAPI_BASE}/type/{tipo_id}"
        dado = obter_json(url, f"tipos/{tipo_id}.json")
        doc = {
            "_fonte": "pokeapi",
            "_url": url,
            "_ingerido_em": _agora_iso(),
            **dado,
        }
        upsert(colecao, f"tipo/{tipo_id}", doc)
    print(f"[extrair] tipos: {len(TIPO_IDS)} documentos processados")


def extrair_especies_e_formas(db) -> None:
    """Para cada uma das 721 espécies, extrai a espécie e TODAS as suas
    variedades (formas), incluindo as formas alternativas (Mega, Primal,
    Therian, etc.), conforme varieties[]."""
    col_pokemon = db["pokemon"]
    col_especies = db["especies"]

    n_pokemon = 0
    for especie_id in range(1, N_ESPECIES + 1):
        url_especie = f"{POKEAPI_BASE}/pokemon-species/{especie_id}"
        especie = obter_json(url_especie, f"especies/{especie_id}.json")
        doc_especie = {
            "_fonte": "pokeapi",
            "_url": url_especie,
            "_ingerido_em": _agora_iso(),
            **especie,
        }
        upsert(col_especies, f"especie/{especie_id}", doc_especie)

        for variedade in especie.get("varieties", []):
            poke_ref = variedade["pokemon"]
            poke_url = poke_ref["url"]
            poke_id = poke_url.rstrip("/").split("/")[-1]
            pokemon = obter_json(poke_url, f"pokemon/{poke_id}.json")
            doc_pokemon = {
                "_fonte": "pokeapi",
                "_url": poke_url,
                "_ingerido_em": _agora_iso(),
                "_especie_id": especie_id,
                **pokemon,
            }
            upsert(col_pokemon, f"pokemon/{poke_id}", doc_pokemon)
            n_pokemon += 1

    print(f"[extrair] especies: {N_ESPECIES} documentos processados")
    print(f"[extrair] pokemon (formas + padrão): {n_pokemon} documentos processados")


def extrair_pokemon_csv(db) -> None:
    texto = obter_texto(POKEMON_CSV_URL, "csv/pokemon.csv")
    colecao = db["pokemon_csv"]
    leitor = csv.DictReader(io.StringIO(texto))
    n = 0
    for linha in leitor:
        numero = linha["#"]
        doc = {
            "_fonte": "csv:pokemon.csv",
            "_arquivo": "pokemon.csv",
            "_ingerido_em": _agora_iso(),
            **{k: v for k, v in linha.items()},
        }
        upsert(colecao, f"pokemon_csv/{numero}", doc)
        n += 1
    print(f"[extrair] pokemon_csv: {n} documentos processados")


def extrair_combates_csv(db) -> None:
    texto = obter_texto(COMBATS_CSV_URL, "csv/combats.csv")
    colecao = db["combates"]
    leitor = csv.DictReader(io.StringIO(texto))
    n = 0
    for i, linha in enumerate(leitor, start=1):
        doc = {
            "_fonte": "csv:combats.csv",
            "_arquivo": "combats.csv",
            "_ingerido_em": _agora_iso(),
            **{k: v for k, v in linha.items()},
        }
        upsert(colecao, f"combate/{i}", doc)
        n += 1
    print(f"[extrair] combates: {n} documentos processados")


def main() -> None:
    client = MongoClient(MONGO_URI)
    db = client[DB_NAME]

    extrair_tipos(db)
    extrair_especies_e_formas(db)
    extrair_pokemon_csv(db)
    extrair_combates_csv(db)

    print("[extrair] concluído.")


if __name__ == "__main__":
    main()
