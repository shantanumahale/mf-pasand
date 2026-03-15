# Claude Code Prompt: Mutual Fund Recommender App

## Project Overview

Build a Mutual Fund Recommender application that suggests Indian mutual funds to users based on their financial persona. The app uses vector similarity search to match user profiles against fund descriptions stored as embeddings in Elasticsearch.

**Tech Stack:**

- **Frontend:** Flutter (mobile-first, can be web too)
- **Backend:** FastAPI (Python)
- **Search/Vector DB:** Elasticsearch 8.x+ (with native kNN support)
- **Data Sources:** AMFI (via mfapi.in) and Kuvera (via mf.captnemo.in)
- **Embedding Model:** OpenAI `text-embedding-3-small` (1536 dimensions) — use the openai Python SDK. Make the embedding provider swappable later via an abstraction layer, but start with OpenAI.

**Project Structure:**

```
mf-recommender/
├── backend/
│   ├── app/
│   │   ├── main.py                  # FastAPI app entry point
│   │   ├── config.py                # Settings via pydantic-settings (ES host, OpenAI key, etc.)
│   │   ├── api/
│   │   │   ├── routes/
│   │   │   │   ├── recommend.py     # POST /recommend endpoint
│   │   │   │   └── funds.py         # GET /funds, GET /funds/{id} for browsing
│   │   │   └── deps.py              # Shared dependencies (ES client, embedding client)
│   │   ├── models/
│   │   │   ├── persona.py           # Pydantic model for user persona input
│   │   │   └── fund.py              # Pydantic model for fund data
│   │   ├── services/
│   │   │   ├── embedding.py         # Embedding generation (abstracts OpenAI)
│   │   │   ├── search.py            # Elasticsearch query builder (kNN + filters)
│   │   │   └── fund_text.py         # JSON-to-natural-language converter
│   │   └── ingestion/
│   │       ├── ingest.py            # Main ingestion orchestrator
│   │       ├── sources/
│   │       │   ├── amfi.py          # Fetch from mfapi.in
│   │       │   └── kuvera.py        # Fetch from mf.captnemo.in
│   │       └── merge.py             # Merge AMFI + Kuvera data by scheme code/ISIN
│   ├── requirements.txt
│   ├── Dockerfile
│   └── docker-compose.yml           # FastAPI + Elasticsearch
├── frontend/
│   └── (Flutter app)
└── README.md
```

---

## Part 1: Data Ingestion Pipeline

### Step 1: Fetch fund data from free APIs

**Source 1 — mfapi.in (AMFI data):**

- `GET https://api.mfapi.in/mf` → returns list of all scheme codes and names
- `GET https://api.mfapi.in/mf/{scheme_code}` → returns scheme info + historical NAV
- No auth required, no rate limits
- We need: scheme_code, scheme_name, historical NAV (to compute 1Y/3Y/5Y returns ourselves)

**Source 2 — mf.captnemo.in (Kuvera data):**

- `GET https://mf.captnemo.in/{ISIN}.json` → returns rich metadata
- Fields we want: ISIN, aum, category, crisil_rating, expense_ratio, fund_category, fund_house, fund_manager, fund_type, fund_rating, min SIP/lumpsum, maturity_type, direct/regular flag
- No auth required

**Merging strategy:**

- mfapi.in gives us scheme codes + NAV history
- mf.captnemo.in gives us rich metadata keyed by ISIN
- We need a mapping between scheme codes and ISINs. AMFI's master data (https://www.amfiindia.com/spages/NAVAll.txt) contains both scheme codes and ISINs in the same row. Parse this file to build the mapping.

**Filtering:**

- Only keep active, open-ended, direct-plan, growth-option funds
- Filter out: regular plans, IDCW/dividend plans, closed-ended funds, FMPs, institutional plans
- This should leave us with roughly 1,500–2,500 funds

### Step 2: Compute derived metrics from NAV history

For each fund, compute:

- `returns_1y`: 1-year CAGR
- `returns_3y`: 3-year CAGR
- `returns_5y`: 5-year CAGR (null if fund is younger)
- `volatility_1y`: annualized standard deviation of daily returns over 1 year
- `max_drawdown_1y`: maximum peak-to-trough decline over 1 year

Handle edge cases: funds with insufficient history should have null for metrics they can't compute.

### Step 3: Convert to natural language descriptions

Write a function `to_natural_text(fund: dict) -> str` that takes the merged + enriched fund data and produces a paragraph like:

```
"Axis Bluechip Fund Direct Growth is a large cap equity fund managed by Axis Mutual Fund
with moderately high risk (CRISIL rated). It has an expense ratio of 0.49% and manages
assets worth ₹34,521 crores. The fund has delivered 18.5% returns over 1 year, 12.3%
annualized over 3 years, and 14.1% annualized over 5 years, with moderate volatility.
It is suitable for long-term investors seeking stable large-cap equity exposure. Minimum
SIP investment is ₹500 and minimum lumpsum is ₹5,000. The fund is managed by
Shreyash Devalkar."
```

Guidelines:

- Translate raw numbers into natural language (don't just dump values)
- Add interpretive phrases where possible: "low expense ratio", "high volatility", "suitable for risk-averse investors"
- Handle missing fields gracefully — skip them, don't output "None"
- Keep all descriptions roughly similar in length (100–200 words)

### Step 4: Generate embeddings and index into Elasticsearch

**Elasticsearch index mapping:**

```json
{
  "mappings": {
    "properties": {
      "scheme_code": { "type": "keyword" },
      "scheme_name": { "type": "text" },
      "isin": { "type": "keyword" },
      "fund_house": { "type": "keyword" },
      "category": { "type": "keyword" },
      "fund_type": { "type": "keyword" },
      "crisil_rating": { "type": "keyword" },
      "expense_ratio": { "type": "float" },
      "aum_cr": { "type": "float" },
      "returns_1y": { "type": "float" },
      "returns_3y": { "type": "float" },
      "returns_5y": { "type": "float" },
      "volatility_1y": { "type": "float" },
      "max_drawdown_1y": { "type": "float" },
      "min_sip": { "type": "float" },
      "min_lumpsum": { "type": "float" },
      "fund_manager": { "type": "text" },
      "natural_text": { "type": "text" },
      "fund_embedding": {
        "type": "dense_vector",
        "dims": 1536,
        "index": true,
        "similarity": "cosine"
      }
    }
  }
}
```

- Embed each fund's `natural_text` using OpenAI's text-embedding-3-small
- Batch the embedding calls (OpenAI supports batch embedding) to minimize API calls
- Index all documents into Elasticsearch
- The entire ingestion pipeline should be runnable as: `python -m app.ingestion.ingest`

---

## Part 2: FastAPI Backend

### Persona Input Model

```python
class UserPersona(BaseModel):
    age: int
    annual_income: Optional[float] = None        # in lakhs
    investment_horizon: str                        # "short" (<3y), "medium" (3-7y), "long" (7y+)
    risk_appetite: str                             # "low", "moderate", "high", "very_high"
    investment_goal: str                           # "wealth_creation", "tax_saving", "retirement", "child_education", "emergency_fund", "regular_income"
    monthly_sip_budget: Optional[float] = None     # in rupees
    lumpsum_available: Optional[float] = None      # in rupees
    existing_investments: Optional[str] = None     # free text: "I have FDs and some SBI mutual funds"
    preferences: Optional[str] = None              # free text: "I prefer index funds", "no sectoral funds"
```

### Recommendation Endpoint: `POST /recommend`

1. **Convert persona to natural text** — similar to fund descriptions, convert the structured persona into a paragraph:

   ```
   "28-year-old investor with high risk appetite and a long investment horizon of 7+ years.
   Goal is wealth creation. Can invest ₹10,000 monthly via SIP. Has some existing FDs.
   Prefers index funds and wants to avoid sectoral funds."
   ```

2. **Generate embedding** of this persona text using the same model

3. **Build Elasticsearch query** combining:
   - kNN vector search on `fund_embedding` (top 50 candidates)
   - Hard filters based on persona:
     - If `risk_appetite` is "low" → filter `crisil_rating` to ["Low", "Low to Moderate"]
     - If `investment_goal` is "tax_saving" → filter `category` to ELSS
     - If `investment_goal` is "emergency_fund" → filter `fund_type` to Debt, `category` to liquid/overnight/ultra-short
     - If `monthly_sip_budget` exists → filter `min_sip <= budget`
   - The filters should be additive and smart — not every persona field maps to a hard filter

4. **Return top 10 recommendations** with:
   - Fund name, category, fund house
   - Key metrics (returns, expense ratio, risk grade)
   - A similarity score
   - The natural language description

### Additional Endpoints

- `GET /funds` — paginated list of all indexed funds with basic filters (category, fund_type, risk)
- `GET /funds/{scheme_code}` — full details of a single fund
- `GET /health` — health check that verifies Elasticsearch connectivity

---

## Part 3: Flutter Frontend

Build a clean, minimal mobile app with these screens:

### Screen 1: Persona Input Form

- Step-by-step or single-page form collecting all UserPersona fields
- Use dropdowns for structured fields (risk_appetite, investment_horizon, goal)
- Free text fields for existing_investments and preferences
- A "Get Recommendations" CTA button

### Screen 2: Recommendations List

- Shows top 10 recommended funds as cards
- Each card shows: fund name, category, fund house, 3Y returns, expense ratio, risk grade, similarity score as a match percentage
- Tapping a card navigates to the detail screen

### Screen 3: Fund Detail

- Full fund information: all metrics, fund manager, natural language description
- Perhaps a simple chart showing 1Y/3Y/5Y returns comparison

### Design Guidelines

- Use Material 3 / Material You design language
- Keep it clean and minimal — think Kuvera/Groww aesthetic
- Use a calming color palette (blues/greens for finance)
- Proper loading states and error handling

---

## Part 4: Docker Setup

Create a `docker-compose.yml` that spins up:

- **Elasticsearch 8.x** (single node, security disabled for dev)
- **FastAPI** backend

The Flutter app runs natively on device/emulator so it doesn't need containerization.

Include a `Makefile` or shell scripts for common operations:

- `make ingest` — run the data ingestion pipeline
- `make dev` — start docker-compose and run FastAPI with hot reload
- `make test` — run tests

---

## Important Implementation Notes

1. **Embedding model is swappable** — use an abstract base class for the embedding provider. Start with OpenAI but make it easy to switch to sentence-transformers or Cohere later.

2. **Environment variables** — all secrets (OpenAI API key) and config (ES host, index name) should be in `.env` and loaded via pydantic-settings. Include a `.env.example`.

3. **Error handling** — the ingestion pipeline should be resilient. If mf.captnemo.in is down or a specific ISIN returns 404, log the error and continue with the next fund. Don't let one bad fund crash the entire pipeline.

4. **Rate limiting on external APIs** — add reasonable delays between API calls during ingestion (especially to mf.captnemo.in since it's an unofficial API). Use asyncio + httpx with a semaphore for concurrent but rate-limited fetching.

5. **Logging** — use Python's logging module throughout. The ingestion pipeline should log progress: "Fetched 500/2000 funds", "Generated embeddings for batch 3/10", "Indexed 2000 documents into Elasticsearch".

6. **Tests** — write tests for:
   - `to_natural_text()` with various fund profiles (complete data, missing fields)
   - Persona-to-text conversion
   - Elasticsearch query builder (verify filters are correctly applied for different persona types)
   - API endpoint integration tests with a test Elasticsearch index

7. **No Celery, no RabbitMQ, no Redis** — this is intentionally simple infrastructure. The ingestion is a batch script. The API is synchronous request-response. Don't add complexity that isn't needed.
