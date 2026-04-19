# StockFlow

## What It Does and Why It Matters

Inventory mistakes are expensive, especially in fast-moving operations where teams need to register product movements quickly and still trust the numbers they see. When stock records are inconsistent or delayed, teams over-order, miss fulfillments, or lose time reconciling data manually.

StockFlow was built to address this gap with a clean, practical prototype: **register inbound/outbound movements with strict validation, enforce non-negative stock rules, and retrieve current inventory instantly for a given product**. The goal is clarity over complexity — a transparent workflow that is easy to test, reason about, and extend.

## Product Overview

StockFlow includes both a backend API and a lightweight Streamlit interface.

- The **backend** (FastAPI) exposes two core endpoints:
  - `POST /movements` to register stock in/out events
  - `GET /products/{product_id}/stock` to retrieve current stock
- The **frontend** (Streamlit) provides two side-by-side forms:
  - **Stock Register** for movement submission
  - **Inventory Checker** for stock lookup
- A sidebar user guide explains input rules and expected behavior.

The system enforces validation at request time and at business-rule level, then returns explicit success/error responses so users know exactly what happened.

## Architecture Overview

The repository is seperated into these parts:

1. **Backend/**
   - `main.py`: FastAPI app and route definitions.
   - `service.py`: Validation helpers, request/response schemas, and stock business logic.
   - `__init__.py`: Package marker.

2. **Frontend/**
   - `app.py`: Streamlit UI with forms, session-state feedback, and background styling.
   - `photo/background_img.png`: UI background asset.

3. **requirements.txt**
   - Python dependencies for backend and frontend runtime.

```text
├── Backend/
│   ├── __init__.py
│   ├── main.py
│   └── service.py
│
├── Frontend/
│   ├── app.py
│   └── photo/
│       └── background_img.png
│
├── requirements.txt
└── README.md
```

## Backend Logic

The backend uses an in-memory dictionary (`product_id -> current_stock`) and a rule-based flow.

### 1) Input Validation

For movement registration:
- `product_id`
  - Required, trimmed, non-empty
  - Alphanumeric only
  - Maximum length: 30
- `quantity`
  - integer only
  - range: `1` to `1_000_000`
  - Integer only
  - Range: 1 to 1,000,000
- `type`
  - Must be `in` or `out` (normalized case-insensitively)
For stock lookup:
- `product_id` is validated with the same shared validator.

### 2) Movement Registration Logic (`POST /movements`)

For each request (`product_id`, `quantity`, `type`):

1. Validate payload via Pydantic + custom validator.
2. If `type == in`, increase current stock (default starts from 0).
3. If `type == out`:
   - Reject unknown product IDs (`404`).
   - Reject operations that would create negative stock (`400`).
4. Return success response with updated `current_stock`.

### 3) Stock Retrieval Logic (`GET /products/{product_id}/stock`)

1. Validate `product_id` format.
2. Reject unknown products (`404`).
3. Return `product_id` and current stock value.

## How to Run (Local)

### 1. Install dependencies

```bash
pip install -r requirements.txt
```

### 2. Start the backend API

```bash
python -m uvicorn Backend.main:app --reload
```

### 3. Open backend docs (You can test here)

- Swagger UI: `http://127.0.0.1:8000/docs`

### 4. Start the frontend app (optional)

```bash
streamlit run Frontend/app.py
```

## Access the Application

- Frontend (local): `http://localhost:8501`
- Backend API (local): `http://localhost:8000`
- Hosted Streamlit demo: `https://stockflow-dashboard.streamlit.app/`

## Known Limitations

- **State is in-memory only**. Stock data resets whenever the backend process restarts.


## What is Not Delievered

To be transparent for future maintainers:

- **No persistent storage layer** (e.g., PostgreSQL/Redis).
- **No movement history/audit trail endpoint** — only latest stock state is stored.

## What Could Be Done in the Future

- **Backend**
  - Add persistent storage with transaction-safe updates.
  - Add movement history logs and filtering endpoints.

