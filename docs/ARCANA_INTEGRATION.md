# ARCANA integration guide

## Runtime contract

The service is FastAPI at `kb_api.main:app`. OpenAPI is served at `/docs` and `/openapi.json`. Existing `/kb/query` accepts `question`, `top_k`, optional `corpus` and `document_id`, `mode` (`graph` or `vector`), and optional conversation `context_doc_ids`. Its response includes answer, status, citations, evidence, retrieval trace, timings, and source document IDs.

`POST /kb/retrieve/cross-document` is the independent evidence-retrieval operation. Example request:

```json
{"question":"How does the policy objective connect to the program implementation?","top_k":8}
```

It returns evidence chunks, source documents, citations, graph links used for expansion, trace, and status. It does not generate an answer; ARCANA can pass the returned attributed evidence to its own answer-generation layer. The current graph expansion follows shared `Tag` links, so relevance and entity semantics depend on ingestion quality.

## Integration boundary

No ARCANA backend source or deployed API contract was included in the supplied archive. The team must confirm authentication, network/TLS, request timeout, payload limits, tenant/access-control metadata, document-type taxonomy, and whether ARCANA wants evidence retrieval only or generated answers. Do not expose `debug=true` to end users; debug payloads may include prompts and retrieved text.

## Run

Copy `.env.example` to `.env`, configure Neo4j and optional Groq credentials, then use `docker compose up -d kb-api` (and the loader after schema setup). Health: `/kb/health`; docs: `/docs`.
