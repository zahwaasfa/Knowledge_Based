# ARCANA Knowledge Graph External Knowledge Base

General-purpose external knowledge service for ARCANA: document ingestion, generic Neo4j knowledge graph, optional vector indexing, Graph/Vector retrieval, grounded answer generation, and evidence citations. Existing Bappenas and Notetaker records are retained as domain data and evaluation material; Notetaker is not the service identity.

## Implemented runtime

- FastAPI service (`kb_api.main:app`), OpenAPI at `/docs`, health at `/kb/health`.
- Query endpoint: `POST /kb/query` (`mode`: `graph` or `vector`).
- Independent cross-document evidence endpoint: `POST /kb/retrieve/cross-document`.
- Ingestion supports PDF, DOCX, PPTX, XLSX, CSV, TXT, and Markdown extraction. Actual domain catalogs and metadata adaptation remain configured in current source; see limitations below.
- Neo4j schema and indexes: `schema/`; graph contract: `docs/GRAPH_CONTRACT.md`.

## Quick start

1. Copy `.env.example` to `.env`; set Neo4j connection and credentials. Configure Groq only if answer generation is enabled.
2. Start local Neo4j if needed: `docker compose --profile local-db up -d neo4j`.
3. Initialize schema and ingest configured data: `docker compose run --rm loader`.
4. Start API: `docker compose up -d kb-api`; open `http://localhost:8001/docs`.

Docker runtime installs `requirements-runtime.txt`. Development and evaluation tools use `requirements-evaluation.txt`. Do not distribute `.env`.

## Cross-document endpoint example

```json
{"question":"Which source documents connect the policy and program?","top_k":8}
```

Response includes `evidence`, `source_documents`, `citations`, `graph_links`, `trace`, `filters`, and `status`. It returns retrieval evidence without generating an answer so ARCANA can use its own chatbot synthesis layer.

## Documentation and evaluation

- [Architecture](docs/ARCHITECTURE.md)
- [ARCANA integration contract](docs/ARCANA_INTEGRATION.md)
- [Cross-document retrieval and limits](docs/CROSS_DOCUMENT_RETRIEVAL.md)
- [Evaluation guide](evaluation/README.md) and [original Notetaker benchmark](evaluation/RUNBOOK.md)
- [Synthetic cross-document scenarios](evaluation/cross_document/README.md)
- [Change log](CHANGELOG.md), [test report](TEST_REPORT.md)

## Integration-readiness boundary

The archive contains no ARCANA backend source or deployed integration contract. The service is an integration candidate, not a verified live ARCANA integration. Cross-document expansion currently follows shared graph tags. Canonical entity resolution/disambiguation, conflicting-fact detection, general-purpose configurable domain catalog ingestion, access control, and real-source multi-hop benchmark validation remain follow-up work; details are recorded in the docs and test report.
