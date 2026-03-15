# Frontend Design

## Overview

The MF Pasand mobile app is built with **Flutter**, targeting both Android and iOS with a single codebase. The app follows a mobile-first design philosophy with a calming, trustworthy aesthetic inspired by Indian fintech apps like Kuvera and Groww. The interface is intentionally simple: three screens guide the user from persona input to personalized recommendations to detailed fund exploration.

---

## Screen Flow / Navigation

```mermaid
stateDiagram-v2
    [*] --> PersonaInput : App Launch

    PersonaInput --> Loading : Submit Persona
    Loading --> RecommendationsList : Recommendations Loaded
    Loading --> ErrorState : API Error

    ErrorState --> PersonaInput : Retry / Edit Persona

    RecommendationsList --> FundDetail : Tap Fund Card
    RecommendationsList --> PersonaInput : Edit Persona / Back

    FundDetail --> RecommendationsList : Back

    state PersonaInput {
        [*] --> BasicInfo
        BasicInfo --> GoalsRisk
        GoalsRisk --> BudgetPreferences
        BudgetPreferences --> ReviewSubmit
    }
```

### Navigation Rules

| From | To | Trigger | Transition |
|------|----|---------|------------|
| Persona Input | Loading | User taps "Get Recommendations" | Push with loading overlay |
| Loading | Recommendations List | API responds successfully | Replace loading with results |
| Loading | Error State | API returns error or timeout | Show error with retry option |
| Recommendations List | Fund Detail | User taps a fund card | Push detail screen |
| Fund Detail | Recommendations List | User taps back / swipe back | Pop |
| Recommendations List | Persona Input | User taps "Edit Persona" | Pop to root |
| Error State | Persona Input | User taps "Try Again" | Pop to persona form |

---

## Screen 1: Persona Input Form

### Layout

```mermaid
flowchart TD
    subgraph "Persona Input Screen"
        HEADER["App Bar: MF Pasand Logo + Title"]

        subgraph "Step Indicator"
            S1["Step 1<br/>About You"]
            S2["Step 2<br/>Goals & Risk"]
            S3["Step 3<br/>Budget"]
            S4["Step 4<br/>Review"]
            S1 --- S2 --- S3 --- S4
        end

        subgraph "Step 1 - Basic Info"
            AGE["Age Slider / Number Input<br/>Range: 18 - 100"]
            EXP["Experience Level<br/>Segmented Control<br/>Beginner | Intermediate | Advanced"]
            TAX["Tax Regime (Optional)<br/>Toggle: Old | New"]
        end

        subgraph "Step 2 - Goals & Risk"
            GOALS["Investment Goals<br/>Multi-select Chips<br/>Retirement | Wealth Creation |<br/>Tax Saving | Emergency Fund |<br/>Child Education | House Purchase"]
            RISK["Risk Tolerance<br/>Visual Slider with Icons<br/>Low | Moderate | High"]
            HORIZON["Investment Horizon<br/>Segmented Control<br/>Short (less than 3Y) | Medium (3-7Y) | Long (7Y+)"]
        end

        subgraph "Step 3 - Budget & Preferences"
            SIP["Monthly SIP Budget<br/>Slider + Text Input<br/>Range: 500 - 100,000 INR"]
            CATS["Preferred Categories (Optional)<br/>Multi-select Chips<br/>Equity | Debt | Hybrid"]
        end

        subgraph "Step 4 - Review & Submit"
            SUMMARY["Summary Card<br/>All selections displayed<br/>for review"]
            SUBMIT["Primary Button<br/>Get My Recommendations"]
        end

        HEADER --> S1
    end
```

### Interaction Details

| Element | Type | Behavior |
|---------|------|----------|
| Age | Slider with numeric input | Defaults to 30; slider range 18-100; user can also type directly |
| Experience Level | Segmented control (3 options) | Single select; defaults to "Beginner" |
| Tax Regime | Optional toggle | Defaults to unselected; informational tooltip explains relevance |
| Goals | Chip group | Multi-select; at least one required; chips highlight on selection |
| Risk Tolerance | Custom slider with emoji/icon indicators | Three stops; visual feedback (green for low, yellow for moderate, red for high) |
| Investment Horizon | Segmented control | Single select; shows years range below each option |
| Monthly SIP Budget | Slider + editable text field | Slider for quick selection; text field for precise input; minimum 500 INR |
| Preferred Categories | Chip group | Optional multi-select; if none selected, all categories are considered |
| Review card | Read-only summary | Shows all selections; each row is tappable to jump back to that step |
| Submit button | Elevated button | Disabled until all required fields are filled; shows loading spinner on tap |

### Step Navigation

- Users can swipe between steps or tap the step indicator
- Back button returns to the previous step (or exits app from Step 1)
- Each step validates its inputs before allowing forward navigation
- The step indicator shows completion state (filled dot for completed, outlined for current, dimmed for future)

---

## Screen 2: Recommendations List

### Layout

```mermaid
flowchart TD
    subgraph "Recommendations Screen"
        HEADER2["App Bar: Recommendations<br/>Back Arrow | Edit Persona Button"]

        PERSONA_CHIP["Persona Summary Bar<br/>Collapsed: 30y old, Moderate risk, Long term<br/>Tappable to expand full summary"]

        subgraph "Fund Card 1 (Rank #1)"
            RANK1["#1 Badge"]
            NAME1["HDFC Mid-Cap Opportunities Direct Growth"]
            CAT1["Chip: Equity - Mid Cap"]
            SCORE1["Match Score: 94%"]
            subgraph "Metrics Row 1"
                CAGR1_1Y["1Y: 24.5%"]
                CAGR1_3Y["3Y: 18.2%"]
                CAGR1_5Y["5Y: 15.8%"]
            end
            subgraph "Details Row 1"
                AUM1["AUM: 34,500 Cr"]
                ER1["Expense: 0.75%"]
                RISK1["Risk: High"]
            end
            SIP1["Min SIP: 500"]
        end

        subgraph "Fund Card 2 (Rank #2)"
            RANK2["#2 Badge"]
            NAME2["Parag Parikh Flexi Cap Direct Growth"]
            CAT2["Chip: Equity - Flexi Cap"]
            SCORE2["Match Score: 91%"]
            METRICS2["1Y: 22.1% | 3Y: 19.5% | 5Y: 17.2%"]
            DETAILS2["AUM: 51,200 Cr | Expense: 0.63%"]
        end

        MORE["... Cards 3 through 10 ..."]

        HEADER2 --> PERSONA_CHIP
        PERSONA_CHIP --> RANK1
    end
```

### Card Design Details

| Element | Visual Treatment |
|---------|-----------------|
| Rank badge | Circular badge, top-left of card; gold for #1, silver for #2, bronze for #3, neutral for #4-#10 |
| Fund name | Bold, primary text; truncated with ellipsis if too long |
| Category chip | Small colored chip (green for Equity, blue for Debt, purple for Hybrid) |
| Match score | Prominent percentage; color-coded (green above 80%, yellow 60-80%, neutral below 60%) |
| CAGR values | Three columns; green for positive, red for negative; "N/A" for null values |
| AUM and Expense ratio | Secondary text row; compact format |
| Risk level | Color-coded text (green/yellow/red) |
| Min SIP | Shown only if relevant; format: "SIP from 500" |
| Card itself | Elevated card with subtle shadow; rounded corners (12dp); tappable with ripple effect |

### Empty and Error States

```mermaid
flowchart TD
    subgraph "Empty State"
        EMPTY_ICON["Illustration: No results"]
        EMPTY_TEXT["No funds match your criteria.<br/>Try adjusting your preferences."]
        EMPTY_ACTION["Button: Edit Persona"]
    end

    subgraph "Error State"
        ERR_ICON["Illustration: Connection error"]
        ERR_TEXT["Could not fetch recommendations.<br/>Please check your connection."]
        ERR_ACTION["Button: Try Again"]
    end
```

---

## Screen 3: Fund Detail

### Layout

```mermaid
flowchart TD
    subgraph "Fund Detail Screen"
        HEADER3["App Bar: Fund Name (scrollable)<br/>Back Arrow"]

        subgraph "Hero Section"
            FUND_NAME["HDFC Mid-Cap Opportunities<br/>Direct Plan - Growth"]
            AMC_NAME["HDFC Asset Management"]
            CAT_CHIP["Equity - Mid Cap"]
            RISK_BADGE["Risk: High"]
            MATCH_SCORE["Your Match: 94%"]
        end

        subgraph "NAV Section"
            NAV_VALUE["Current NAV: 412.35"]
            NAV_DATE["as of 14 Mar 2026"]
        end

        subgraph "Performance Card"
            PERF_HEADER["Returns (CAGR)"]
            PERF_1Y["1 Year: 24.5%"]
            PERF_3Y["3 Year: 18.2%"]
            PERF_5Y["5 Year: 15.8%"]
            VOL["Volatility: 14.2%"]
            DD["Max Drawdown: -18.5%"]
        end

        subgraph "Fund Information Card"
            FM["Fund Manager: Chirag Setalvad"]
            BENCH["Benchmark: Nifty Midcap 150 TRI"]
            AUM_D["AUM: 34,500 Crores"]
            ER_D["Expense Ratio: 0.75%"]
            AGE_D["Fund Age: 8.5 Years"]
        end

        subgraph "Investment Details Card"
            MIN_SIP_D["Min SIP: 500"]
            MIN_LUMP_D["Min Lumpsum: 5,000"]
            EXIT_D["Exit Load: 1% if redeemed<br/>within 1 year"]
        end

        HEADER3 --> FUND_NAME
        FUND_NAME --> NAV_VALUE
        NAV_VALUE --> PERF_HEADER
        PERF_HEADER --> FM
        FM --> MIN_SIP_D
    end
```

### Section Details

| Section | Content | Visual Notes |
|---------|---------|--------------|
| Hero | Fund name, AMC, category chip, risk badge, match score | Large text; category and risk as colored chips; match score in a circular progress indicator |
| NAV | Current NAV value and date | Prominent number; date in secondary text |
| Performance | CAGR values, volatility, max drawdown | Bar chart or horizontal indicators showing relative performance; green/red color coding |
| Fund Information | Manager, benchmark, AUM, expense ratio, age | Clean key-value layout; each row with icon + label + value |
| Investment Details | Min SIP, min lumpsum, exit load | Card with investment-relevant info; exit load as expandable text if lengthy |

---

## Design Guidelines

### Color Palette

```mermaid
flowchart LR
    subgraph "Primary Colors"
        P1["Primary<br/>#1565C0<br/>Deep Blue"]
        P2["Primary Light<br/>#4FC3F7<br/>Light Blue"]
        P3["Primary Dark<br/>#0D47A1<br/>Dark Blue"]
    end

    subgraph "Accent Colors"
        A1["Accent<br/>#00897B<br/>Teal Green"]
        A2["Accent Light<br/>#4DB6AC<br/>Light Teal"]
    end

    subgraph "Semantic Colors"
        SEM1["Positive<br/>#2E7D32<br/>Green"]
        SEM2["Negative<br/>#C62828<br/>Red"]
        SEM3["Warning<br/>#F9A825<br/>Amber"]
        SEM4["Neutral<br/>#616161<br/>Grey"]
    end

    subgraph "Backgrounds"
        BG1["Surface<br/>#FFFFFF<br/>White"]
        BG2["Background<br/>#F5F7FA<br/>Off-white"]
        BG3["Card<br/>#FFFFFF<br/>White + elevation"]
    end

    style P1 fill:#1565C0,color:#FFF
    style P2 fill:#4FC3F7,color:#000
    style P3 fill:#0D47A1,color:#FFF
    style A1 fill:#00897B,color:#FFF
    style A2 fill:#4DB6AC,color:#000
    style SEM1 fill:#2E7D32,color:#FFF
    style SEM2 fill:#C62828,color:#FFF
    style SEM3 fill:#F9A825,color:#000
    style SEM4 fill:#616161,color:#FFF
    style BG1 fill:#FFFFFF,color:#000
    style BG2 fill:#F5F7FA,color:#000
    style BG3 fill:#FFFFFF,color:#000
```

### Design System

| Aspect | Guideline |
|--------|-----------|
| **Framework** | Material 3 (Material You) |
| **Typography** | Google Fonts - Inter or Poppins; headings in semi-bold, body in regular |
| **Spacing** | 8dp grid system; consistent padding (16dp horizontal, 12dp vertical for cards) |
| **Border radius** | 12dp for cards, 8dp for chips and buttons, 24dp for FABs |
| **Elevation** | Cards: 1-2dp elevation; bottom sheets: 8dp; dialogs: 16dp |
| **Icons** | Material Symbols (outlined style); consistent 24dp size |
| **Aesthetic** | Calming blue/green palette; clean whitespace; inspired by Kuvera and Groww |
| **Dark mode** | Planned for future; initial release is light mode only |

### Accessibility

| Aspect | Guideline |
|--------|-----------|
| Contrast ratio | Minimum 4.5:1 for body text, 3:1 for large text (WCAG AA) |
| Touch targets | Minimum 48dp x 48dp for all interactive elements |
| Screen reader | All interactive elements have semantic labels |
| Font scaling | Supports system font size preferences; layout adapts without overflow |

---

## State Management

```mermaid
flowchart TD
    subgraph "State Architecture"
        subgraph "Persona State"
            PS["PersonaState<br/>- age: int<br/>- risk_tolerance: string<br/>- investment_horizon: string<br/>- goals: list<br/>- monthly_sip_budget: float<br/>- experience_level: string<br/>- preferred_categories: list<br/>- tax_regime: string<br/>- current_step: int<br/>- is_valid: bool"]
        end

        subgraph "Recommendation State"
            RS["RecommendationState<br/>- status: idle / loading / success / error<br/>- recommendations: list of ScoredFund<br/>- persona_summary: string<br/>- total_candidates: int<br/>- error_message: string"]
        end

        subgraph "Fund Detail State"
            FD["FundDetailState<br/>- status: idle / loading / success / error<br/>- fund: Fund<br/>- error_message: string"]
        end
    end

    PS -- "Submit persona" --> RS
    RS -- "Tap fund card" --> FD
```

### State Management Approach

| Aspect | Decision | Rationale |
|--------|----------|-----------|
| **Library** | Provider or Riverpod | Lightweight, Flutter-native, sufficient for 3-screen app |
| **Pattern** | ChangeNotifier + Consumer (Provider) or StateNotifier (Riverpod) | Simple, testable, well-documented |
| **API layer** | Repository pattern with a single ApiClient | Centralized HTTP logic; easy to mock for testing |
| **State persistence** | None (in-memory only) | App is lightweight; persona can be re-entered quickly |

### State Transitions

```mermaid
stateDiagram-v2
    [*] --> Idle : App starts

    state RecommendationState {
        Idle --> Loading : Submit persona
        Loading --> Success : API returns data
        Loading --> Error : API fails
        Error --> Loading : Retry
        Success --> Idle : Edit persona
    }
```

---

## Loading States

```mermaid
flowchart TD
    subgraph "Loading States by Screen"
        subgraph "Recommendations Loading"
            RL_SHIMMER["Shimmer placeholder cards<br/>(3 skeleton cards visible)"]
            RL_TEXT["Finding your perfect funds..."]
            RL_PROGRESS["Linear progress indicator<br/>in app bar"]
        end

        subgraph "Fund Detail Loading"
            FD_SHIMMER["Shimmer placeholders<br/>for each section"]
            FD_PROGRESS["Circular progress indicator<br/>centered"]
        end
    end
```

| Screen | Loading Indicator | Behavior |
|--------|-------------------|----------|
| Persona Submit | Button shows circular spinner; form fields disabled | Prevents double submission |
| Recommendations List | 3 shimmer skeleton cards + "Finding your perfect funds..." text | Communicates progress; skeleton matches card layout |
| Fund Detail | Section-level shimmer placeholders | Each card section shows its shimmer independently |

---

## Error Handling UX

| Error Type | User-Facing Message | Action Offered |
|------------|---------------------|----------------|
| Network error (no internet) | "No internet connection. Please check your network and try again." | "Try Again" button |
| Server error (5xx) | "Something went wrong on our end. Please try again in a moment." | "Try Again" button |
| Timeout | "The request took too long. Please try again." | "Try Again" button |
| No results (empty recommendations) | "No funds match your criteria. Try adjusting your risk tolerance or budget." | "Edit Preferences" button |
| Invalid input (client-side validation) | Inline error message below the specific field | Field highlights in red; message in error color |

### Error Display Pattern

- **Inline errors** (validation): Shown directly below the offending input field; field border turns red
- **Full-screen errors** (network/server): Centered illustration + message + action button; replaces content area
- **Snackbar errors** (non-critical): Bottom snackbar for transient issues (e.g., "Could not load fund details, showing cached data")
- **No toast messages**: Avoid toasts as they are easy to miss on mobile; prefer persistent error states
