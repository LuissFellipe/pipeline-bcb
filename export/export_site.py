"""Exporta a tabela mensal e o último valor de cada série para o site estático."""

import json
import sys
from datetime import datetime, timezone
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent.parent / "ingest"))
from ingest_bcb import conectar  # noqa: E402

SAIDA = Path(__file__).resolve().parent.parent / "site" / "data"


def num(v):
    return None if v is None else float(v)


def main():
    SAIDA.mkdir(parents=True, exist_ok=True)
    with conectar() as conn:
        meses = conn.execute("""
            select to_char(mes, 'YYYY-MM'), selic_media_aa, ipca_mes, ipca_12m,
                   juro_real_aa, dolar_medio, dolar_var_12m
            from marts.fct_indicadores_mensais order by mes""").fetchall()
        # Os cards mostram o último dado de cada série, e não a média do mês
        # em andamento: a Selic de hoje é a meta vigente, não a média de outubro.
        ultimos = conn.execute("""
            select distinct on (nome_serie) nome_serie, to_char(data, 'YYYY-MM-DD'), valor
            from staging.stg_bcb__series order by nome_serie, data desc""").fetchall()
    dados = {
        "gerado_em": datetime.now(timezone.utc).isoformat(timespec="minutes"),
        "ultimos": {nome: {"data": data, "valor": num(valor)} for nome, data, valor in ultimos},
        "colunas": ["mes", "selic", "ipca_mes", "ipca_12m", "juro_real", "dolar", "dolar_var_12m"],
        "meses": [[m[0], *map(num, m[1:])] for m in meses],
    }
    caminho = SAIDA / "indicadores.json"
    caminho.write_text(json.dumps(dados, separators=(",", ":")))
    print(f"{caminho.name}: {len(meses)} meses, {caminho.stat().st_size / 1024:.0f} KB")


if __name__ == "__main__":
    main()
