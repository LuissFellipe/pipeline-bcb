# Pipeline BCB — Indicadores macroeconômicos

Pipeline ELT que coleta diariamente **Selic, IPCA e dólar** da API pública do Banco Central (SGS), carrega em PostgreSQL e transforma com dbt em uma tabela analítica mensal com **juro real** e **inflação acumulada em 12 meses**.

**Pergunta de negócio:** como juros, inflação e câmbio se comportaram desde 2015 — e quando o juro real esteve alto ou negativo?

## Arquitetura

```
API SGS/BCB ──► ingest_bcb.py ──► Postgres (raw) ──► dbt (staging ──► marts)
                (incremental,                         views         tabelas
                 upsert)                              testadas      analíticas
```

| Camada | Objeto | Descrição |
|---|---|---|
| raw | `raw.sgs_series` | Dados como vieram da API, chave `(codigo_serie, data)` |
| staging | `staging.stg_bcb__series` | Tipagem e testes de qualidade |
| marts | `marts.fct_indicadores_mensais` | Um registro por mês: Selic média, IPCA, IPCA 12m, juro real, dólar |

## Decisões técnicas

- **Carga incremental:** o script consulta a última data carregada por série e busca só o que falta; `ON CONFLICT` torna a execução idempotente.
- **Paginação por janelas:** a API do SGS limita séries diárias a 10 anos por consulta, então a carga inicial é feita em janelas de 5 anos.
- **IPCA 12m composto, não somado:** `exp(sum(ln(1 + taxa)))` sobre uma janela de 12 meses; meses com janela incompleta ficam nulos.
- **Juro real pela equação de Fisher:** `(1 + Selic) / (1 + IPCA 12m) − 1`.

## Como rodar

Requisitos: Docker e [uv](https://docs.astral.sh/uv/).

```bash
cp .env.example .env
uv sync
make pipeline        # sobe o Postgres, ingere e roda dbt build (modelos + testes)
```

Consultar o resultado:

```bash
docker compose exec postgres psql -U bcb -c "select * from marts.fct_indicadores_mensais order by mes desc limit 12"
```

## Próximos passos

- [ ] Agendamento diário (Airflow ou GitHub Actions)
- [ ] Dashboard no Metabase
- [ ] Documentação com `dbt docs generate`
