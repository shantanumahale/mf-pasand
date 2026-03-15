# Data Model

## Overview

The data model centers on a single Elasticsearch index (`mutual_funds`) that stores enriched fund documents with dense vector embeddings. This document describes the index mapping, the fund data model, the Pydantic request/response schemas, and how data from AMFI and Kuvera maps to the final schema.

---

## Elasticsearch Index Mapping

The `mutual_funds` index uses the following field types:

| Field | ES Type | Purpose |
|-------|---------|---------|
| `scheme_code` | `keyword` | Unique AMFI scheme identifier; used as document `_id` |
| `isin` | `keyword` | ISIN code for cross-referencing with Kuvera |
| `scheme_name` | `text` | Full scheme name (searchable) |
| `fund_house` | `keyword` | AMC / fund house name (filterable) |
| `category` | `keyword` | Broad category: Equity, Debt, Hybrid, Solution Oriented, Other |
| `sub_category` | `keyword` | SEBI sub-category: Large Cap, Mid Cap, Small Cap, ELSS, etc. |
| `risk_level` | `keyword` | Riskometer value: Low, Low to Moderate, Moderate, Moderately High, High, Very High |
| `fund_manager` | `keyword` | Name of the fund manager |
| `benchmark_index` | `keyword` | Benchmark index name |
| `latest_nav` | `float` | Most recent NAV value |
| `nav_date` | `date` | Date of the latest NAV |
| `expense_ratio` | `float` | Total expense ratio (percentage) |
| `aum_crores` | `float` | Assets under management in crores |
| `min_sip_amount` | `float` | Minimum SIP investment amount in INR |
| `min_lumpsum_amount` | `float` | Minimum lump sum investment in INR |
| `exit_load` | `text` | Exit load description (free text) |
| `cagr_1y` | `float` | 1-year CAGR (percentage, nullable) |
| `cagr_3y` | `float` | 3-year CAGR (percentage, nullable) |
| `cagr_5y` | `float` | 5-year CAGR (percentage, nullable) |
| `volatility` | `float` | Annualized volatility (percentage) |
| `max_drawdown` | `float` | Maximum drawdown (percentage, negative value) |
| `fund_age_years` | `float` | Years since fund inception |
| `description` | `text` | Natural language description used for embedding |
| `embedding` | `dense_vector` (1536 dims, cosine similarity) | Vector embedding of the fund description |

### Dense Vector Configuration

```
Field: embedding
Type: dense_vector
Dimensions: 1536
Similarity: cosine
Index: true (enables kNN search)
Algorithm: HNSW (default in ES 8.x+)
  - m: 16
  - ef_construction: 100
```

---

## Fund Data Model - ER Diagram

```mermaid
erDiagram
    FUND {
        string scheme_code PK "AMFI scheme code"
        string isin UK "ISIN code"
        string scheme_name "Full scheme name"
        string fund_house "AMC name"
        string category "Equity / Debt / Hybrid / etc."
        string sub_category "Large Cap / Mid Cap / ELSS / etc."
        string risk_level "Low to Very High"
        string fund_manager "Fund manager name"
        string benchmark_index "Benchmark index name"
    }

    NAV_DATA {
        float latest_nav "Most recent NAV"
        date nav_date "Date of latest NAV"
        float fund_age_years "Years since inception"
    }

    PERFORMANCE_METRICS {
        float cagr_1y "1-year CAGR pct"
        float cagr_3y "3-year CAGR pct"
        float cagr_5y "5-year CAGR pct"
        float volatility "Annualized volatility pct"
        float max_drawdown "Max drawdown pct"
    }

    INVESTMENT_DETAILS {
        float expense_ratio "TER percentage"
        float aum_crores "AUM in crores"
        float min_sip_amount "Min SIP in INR"
        float min_lumpsum_amount "Min lumpsum in INR"
        string exit_load "Exit load description"
    }

    EMBEDDING_DATA {
        string description "Natural language description"
        float_array embedding "1536-dim vector"
    }

    FUND ||--|| NAV_DATA : "has"
    FUND ||--|| PERFORMANCE_METRICS : "has"
    FUND ||--|| INVESTMENT_DETAILS : "has"
    FUND ||--|| EMBEDDING_DATA : "has"
```

> Note: In Elasticsearch, these are all fields in a single flat document, not separate tables. The ER diagram groups them logically for clarity.

---

## Pydantic Models

### UserPersona (Request Input)

The persona captures the investor's profile and preferences to drive personalized recommendations.

```mermaid
classDiagram
    class UserPersona {
        +int age
        +string risk_tolerance
        +string investment_horizon
        +list~string~ goals
        +float monthly_sip_budget
        +string experience_level
        +list~string~ preferred_categories
        +string tax_regime
    }
```

| Field | Type | Constraints | Description |
|-------|------|------------|-------------|
| `age` | integer | 18 to 100 | Investor's age; influences risk and horizon recommendations |
| `risk_tolerance` | string (enum) | `"low"`, `"moderate"`, `"high"` | Self-assessed risk appetite |
| `investment_horizon` | string (enum) | `"short"` (less than 3Y), `"medium"` (3-7Y), `"long"` (7Y+) | Planned holding period |
| `goals` | list of strings | At least 1 required; values like `"retirement"`, `"wealth_creation"`, `"tax_saving"`, `"emergency_fund"`, `"child_education"`, `"house_purchase"` | Financial goals driving the investment |
| `monthly_sip_budget` | float | Greater than 0 | Monthly SIP amount the investor can commit (INR) |
| `experience_level` | string (enum) | `"beginner"`, `"intermediate"`, `"advanced"` | Investing experience; influences fund complexity in recommendations |
| `preferred_categories` | list of strings | Optional; values like `"equity"`, `"debt"`, `"hybrid"` | Category preferences (if any); used as hard filters |
| `tax_regime` | string (enum) | Optional; `"old"`, `"new"` | Tax regime; influences ELSS recommendation relevance |

### Fund (Response Object)

```mermaid
classDiagram
    class Fund {
        +string scheme_code
        +string isin
        +string scheme_name
        +string fund_house
        +string category
        +string sub_category
        +string risk_level
        +string fund_manager
        +string benchmark_index
        +float latest_nav
        +string nav_date
        +float expense_ratio
        +float aum_crores
        +float min_sip_amount
        +float min_lumpsum_amount
        +string exit_load
        +float cagr_1y
        +float cagr_3y
        +float cagr_5y
        +float volatility
        +float max_drawdown
        +float fund_age_years
    }
```

| Field | Nullable | Notes |
|-------|----------|-------|
| `scheme_code` | No | Always present |
| `isin` | Yes | May be null if ISIN mapping not found |
| `scheme_name` | No | Always present from AMFI |
| `fund_house` | Yes | From Kuvera; null if not enriched |
| `category` | Yes | From Kuvera; null if not enriched |
| `sub_category` | Yes | From Kuvera; null if not enriched |
| `risk_level` | Yes | From Kuvera; null if not enriched |
| `cagr_1y`, `cagr_3y`, `cagr_5y` | Yes | Null if insufficient NAV history |
| `volatility`, `max_drawdown` | Yes | Null if insufficient NAV history |
| All other fields | Yes | Dependent on data source availability |

### RecommendationResponse (API Response)

```mermaid
classDiagram
    class RecommendationResponse {
        +string persona_summary
        +list~ScoredFund~ recommendations
        +int total_candidates
        +string model_used
    }

    class ScoredFund {
        +Fund fund
        +float relevance_score
        +int rank
    }

    class Fund {
        +string scheme_code
        +string scheme_name
        +string category
        +... other fields
    }

    RecommendationResponse "1" --> "*" ScoredFund : contains
    ScoredFund "1" --> "1" Fund : wraps
```

| Field | Type | Description |
|-------|------|-------------|
| `persona_summary` | string | The natural language text generated from the persona (useful for debugging/transparency) |
| `recommendations` | list of ScoredFund | Top 10 recommended funds, ordered by relevance score (descending) |
| `total_candidates` | integer | Total number of funds that matched the hard filters before kNN ranking |
| `model_used` | string | Embedding model identifier used for this recommendation (e.g., `text-embedding-3-small`) |

---

## Data Source Mapping

The following diagram shows which fields come from which data source and how they combine into the final Elasticsearch document.

```mermaid
flowchart LR
    subgraph "AMFI / mfapi.in"
        A1["scheme_code"]
        A2["scheme_name (raw)"]
        A3["NAV history (time series)"]
    end

    subgraph "NAVAll.txt (AMFI)"
        N1["ISIN mapping<br/>(scheme_code to ISIN)"]
    end

    subgraph "Kuvera / mf.captnemo.in"
        K1["scheme_name (clean)"]
        K2["fund_house"]
        K3["category"]
        K4["sub_category"]
        K5["risk_level"]
        K6["fund_manager"]
        K7["benchmark_index"]
        K8["expense_ratio"]
        K9["aum_crores"]
        K10["min_sip_amount"]
        K11["min_lumpsum_amount"]
        K12["exit_load"]
    end

    subgraph "Computed (Pipeline)"
        C1["cagr_1y"]
        C2["cagr_3y"]
        C3["cagr_5y"]
        C4["volatility"]
        C5["max_drawdown"]
        C6["fund_age_years"]
        C7["description"]
    end

    subgraph "OpenAI"
        E1["embedding (1536 dims)"]
    end

    subgraph "Elasticsearch Document"
        DOC["Final Fund Document"]
    end

    A1 --> DOC
    A3 --> C1 & C2 & C3 & C4 & C5 & C6
    N1 --> DOC
    K1 & K2 & K3 & K4 & K5 & K6 & K7 & K8 & K9 & K10 & K11 & K12 --> DOC
    C1 & C2 & C3 & C4 & C5 & C6 & C7 --> DOC
    C7 --> E1
    E1 --> DOC
```

### Field Precedence Rules

| Scenario | Rule |
|----------|------|
| Both AMFI and Kuvera provide `scheme_name` | Use Kuvera's version (cleaner formatting) |
| Kuvera data unavailable for a fund | Use AMFI data only; Kuvera-sourced fields are null |
| NAV history too short for a metric | Set that metric to null; other metrics still computed |
| ISIN mapping not found | Skip Kuvera enrichment entirely; log and continue |
| Fund has no NAV data at all | Skip the fund entirely (cannot compute any useful data) |
