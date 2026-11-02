# System architecture (implemented)

```mermaid
flowchart LR
  D[PDF DOCX PPTX XLSX CSV TXT MD] --> I[Ingestion and chunking]
  M[Metadata catalog] --> I
  I --> X[Extraction and generic ontology mapping]
  X --> N[(Neo4j Documents Chunks Entities)]
  I --> V[Optional embeddings]
  V --> N
  Q[ARCANA backend] --> A[FastAPI]
  A --> R[Shared retrieval search]
  R --> G[Graph / vector modes]
  R --> C[Cross-document orchestration]
  G --> L[Grounded answer generation]
  C --> Q
  L --> Q
  E[Evaluation scripts and datasets] -. separate dependencies .-> A
```

Runtime is in `kb`, `kb_api`, `ui`, `schema`, and deployment files. Evaluation scripts and retained results live in `evaluation`, `scripts`, and `reports`. Docker runtime installs `requirements-runtime.txt`; development/evaluation installs `requirements-evaluation.txt`.
