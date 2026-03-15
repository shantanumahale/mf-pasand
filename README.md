# MF Pasand — Mutual Fund Recommender

A mutual fund recommendation app for Indian investors. It matches user financial profiles against ~2,000 mutual funds using vector similarity search, returning personalised recommendations based on risk appetite, investment goals, and financial situation.

Users fill in a short persona form (age, income, risk appetite, goals, SIP budget), and the app returns the top 10 best-matching funds with similarity scores, key metrics, and natural language explanations.

## How It Works

1. **Data ingestion** pulls fund data from AMFI and Kuvera public APIs, computes performance metrics (CAGR, volatility, max drawdown), converts each fund into a natural language description, and generates vector embeddings
2. **Elasticsearch** stores fund data with dense vector embeddings and supports kNN cosine similarity search with hard filters
3. **FastAPI backend** converts user personas into embeddings, queries Elasticsearch, and returns ranked recommendations
4. **Flutter app** provides a clean mobile UI for inputting financial profile and browsing recommendations

## Tech Stack

| Layer | Technology |
|-------|-----------|
| Frontend | Flutter (Dart), Material 3 |
| Backend | FastAPI (Python 3.11) |
| Vector DB | Elasticsearch 8.13 (kNN dense vectors) |
| Embeddings | OpenAI `text-embedding-3-small` (1536 dims) |
| Data Sources | AMFI (mfapi.in), Kuvera (mf.captnemo.in) |
| Containerisation | Docker Compose |

## Project Structure

```
mf-pasand/
├── backend/                  # FastAPI backend + ingestion pipeline
│   ├── app/
│   │   ├── main.py           # FastAPI entry point
│   │   ├── config.py         # Settings (pydantic-settings)
│   │   ├── api/routes/       # recommend.py, funds.py
│   │   ├── models/           # persona.py, fund.py
│   │   ├── services/         # embedding.py, search.py, fund_text.py
│   │   └── ingestion/        # ingest.py, sources/ (amfi, kuvera), merge.py
│   ├── tests/                # 25 tests
│   ├── docker-compose.yml    # FastAPI + Elasticsearch
│   ├── Dockerfile
│   ├── Makefile
│   └── requirements.txt
├── frontend/mf_pasand_app/   # Flutter mobile app
│   └── lib/
│       ├── main.dart
│       ├── theme.dart
│       ├── models/           # user_persona.dart, fund.dart
│       ├── services/         # api_service.dart
│       ├── providers/        # recommendation_provider.dart, fund_provider.dart
│       ├── screens/          # persona, recommendations, fund_detail
│       └── widgets/          # fund_card, metric_card, loading_shimmer
├── system-design/            # Architecture & design docs (Mermaid diagrams)
└── README.md
```

## Prerequisites

- **Docker** and **Docker Compose** (for Elasticsearch and optionally the API)
- **Python 3.11+** (if running the backend outside Docker)
- **Flutter SDK 3.10+** (for the mobile app)
- **OpenAI API key** (for generating embeddings)

## Setup & Run

### 1. Clone and configure environment

```bash
cd mf-pasand/backend
cp .env.example .env
```

Edit `.env` and add your OpenAI API key:

```
ES_HOST=localhost:9200
ES_INDEX=mf-recommendations
OPENAI_API_KEY=sk-your-actual-key-here
EMBEDDING_MODEL=text-embedding-3-small
EMBEDDING_DIMS=1536
```

### 2. Start Elasticsearch

```bash
cd backend
make up
```

This starts Elasticsearch 8.13 on `localhost:9200` (single node, security disabled for dev). Wait a few seconds for it to become healthy:

```bash
curl http://localhost:9200/_cluster/health?pretty
```

### 3. Run the data ingestion pipeline

```bash
cd backend
pip install -r requirements.txt
make ingest
```

This will:
- Fetch the AMFI master list and build scheme code to ISIN mappings
- Filter to ~1,500–2,500 active, direct-plan, growth-option funds
- Fetch NAV history from mfapi.in (rate-limited, async)
- Fetch rich metadata from mf.captnemo.in (rate-limited, async)
- Merge data and compute 1Y/3Y/5Y returns, volatility, and max drawdown
- Generate natural language descriptions for each fund
- Create vector embeddings via OpenAI (batched)
- Bulk index everything into Elasticsearch

The pipeline logs progress throughout. Expect it to take 30–45 minutes depending on API response times.

### 4. Start the FastAPI backend

**Option A — Run directly (with hot reload):**

```bash
cd backend
make dev
```

**Option B — Run via Docker Compose (API + ES together):**

```bash
cd backend
make rebuild
```

The API will be available at `http://localhost:8000`. Verify with:

```bash
curl http://localhost:8000/health
```

### 5. Run the Flutter app

```bash
cd frontend/mf_pasand_app
flutter pub get
flutter run
```

The app connects to `http://localhost:8000` by default. If running on an Android emulator, it automatically uses `10.0.2.2:8000` to reach the host machine.

## API Endpoints

| Method | Endpoint | Description |
|--------|----------|-------------|
| `POST` | `/recommend` | Submit a user persona, get top 10 fund recommendations |
| `GET` | `/funds` | Paginated fund list with optional filters (`category`, `fund_type`) |
| `GET` | `/funds/{scheme_code}` | Full details for a single fund |
| `GET` | `/health` | Health check (verifies Elasticsearch connectivity) |

### Example: Get Recommendations

```bash
curl -X POST http://localhost:8000/recommend \
  -H "Content-Type: application/json" \
  -d '{
    "age": 28,
    "annual_income": 12,
    "investment_horizon": "long",
    "risk_appetite": "high",
    "investment_goal": "wealth_creation",
    "monthly_sip_budget": 10000,
    "preferences": "I prefer index funds"
  }'
```

## Running Tests

```bash
cd backend
make test
```

Runs 25 tests covering:
- Fund-to-natural-text generation (7 tests)
- Persona-to-natural-text generation (3 tests)
- Elasticsearch query builder logic (9 tests)
- API endpoint validation and integration (6 tests)

## Makefile Targets

| Target | Command | Description |
|--------|---------|-------------|
| `make dev` | `uvicorn app.main:app --reload` | Start API with hot reload |
| `make test` | `pytest -v` | Run test suite |
| `make ingest` | `python -m app.ingestion.ingest` | Run data ingestion pipeline |
| `make up` | `docker compose up -d` | Start Elasticsearch |
| `make down` | `docker compose down` | Stop all services |
| `make rebuild` | `docker compose up -d --build` | Rebuild and restart everything |

## System Design

Detailed architecture and design documentation with Mermaid diagrams is in the [`system-design/`](system-design/) folder:

- [Architecture Overview](system-design/architecture-overview.md) — system components, communication patterns, deployment topology
- [Data Ingestion Pipeline](system-design/data-ingestion-pipeline.md) — end-to-end data flow, error handling, rate limiting
- [Data Model](system-design/data-model.md) — Elasticsearch mapping, Pydantic models, field descriptions
- [API Design](system-design/api-design.md) — endpoints, recommendation flow, filter logic
- [Frontend Design](system-design/frontend-design.md) — screen wireframes, navigation, state management
