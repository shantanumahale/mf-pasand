# MF Pasand - System Design Documentation

**MF Pasand** is a Mutual Fund Recommender application that uses semantic search to match investor personas with suitable mutual fund schemes. It combines enriched fund data from multiple Indian financial data sources, generates vector embeddings from natural-language fund descriptions, and serves personalized recommendations through a mobile-first Flutter interface.

---

## Table of Contents

| Document | Description |
|----------|-------------|
| [Architecture Overview](./architecture-overview.md) | High-level system architecture, component responsibilities, communication patterns, and deployment topology |
| [Data Ingestion Pipeline](./data-ingestion-pipeline.md) | End-to-end data flow from external APIs through enrichment, embedding generation, and Elasticsearch indexing |
| [Data Model](./data-model.md) | Elasticsearch index mapping, fund data model, Pydantic schemas, and field-level documentation |
| [API Design](./api-design.md) | All REST API endpoints, request/response shapes, recommendation flow, filter logic, and error handling |
| [Frontend Design](./frontend-design.md) | Screen flows, wireframe-style layouts, design guidelines, state management, and UX patterns |

---

## Technology Stack

| Layer | Technology |
|-------|-----------|
| Mobile App | Flutter (Dart), Material 3 |
| Backend API | FastAPI (Python 3.11+) |
| Search / Vector DB | Elasticsearch 8.x+ (kNN dense vector search) |
| Embedding Model | OpenAI `text-embedding-3-small` (1536 dimensions), swappable |
| Data Sources | AMFI via mfapi.in, Kuvera via mf.captnemo.in |
| Containerization | Docker Compose (backend + Elasticsearch) |

---

## How to Read These Documents

1. Start with the **Architecture Overview** to understand the big picture.
2. Read the **Data Ingestion Pipeline** to understand how fund data flows into the system.
3. Review the **Data Model** to see exactly what data is stored and how it is structured.
4. Study the **API Design** to understand how the frontend communicates with the backend.
5. Finally, explore the **Frontend Design** to see the user-facing experience.

All diagrams in these documents use **Mermaid** notation and can be rendered in any Mermaid-compatible viewer (GitHub, VS Code with Mermaid extension, etc.).
