# StockFlow API

## Overview

StockFlow is a simple backend service designed for registering stock movements and checking inventory for an imaginary company.

It solves a common inventory-tracking problem for technical test scenarios:
- record incoming (`in`) and outgoing (`out`) stock movements
- validate inputs at the API boundary
- enforce stock consistency rules (no negative inventory)
- expose current stock by `product_id`

High-level functionality:
- `POST /movements`: register a stock movement
- `GET /products/{product_id}/stock`: return current stock for a product

## Project Structure

- `Backend/main.py`
  - FastAPI app setup
  - route definitions
  - API-to-service orchestration
- `Backend/service.py`
  - Pydantic schemas
  - validation helpers
  - business logic service (`StockService`)
  - in-memory stock state
- `Frontend/app.py`
  - Streamlit demo app for interaction testing
- `requirements.txt`
  - project dependencies


## Key Design Decisions

- **Separation of API and business logic**
  - Endpoints in `main.py` remain thin.
  - Inventory rules and state changes are centralized in `StockService`.
- **Input validation strategy**
  - Pydantic handles schema-level constraints (type, required fields, ranges).
  - A dedicated `product_id` validator enforces formatting and sanitization.
- **Error handling approach**
  - Domain and validation issues are surfaced with explicit HTTP errors (`400`, `404`, `422`).
  - Responses are structured and predictable for both API and UI consumers.
- **Simplicity over overengineering**
  - In-memory storage and minimal layers are intentional for assignment scope.
  - Design choices favor clarity and correctness over production-grade infrastructure.

## Validation and Error Handling

Validation rules currently include:
- `product_id`
  - required, trimmed, non-empty
  - max length: 30
  - alphanumeric only (no spaces or special characters)
- `quantity`
  - integer only
  - range: `1` to `1_000_000`
- `type`
  - must be `in` or `out` (case-insensitive normalization)

Error handling behavior:
- invalid payload or path input → `422 Unprocessable Entity`
- outgoing movement for unknown product → `404 Not Found`
- outgoing movement that would create negative stock → `400 Bad Request`
- stock query for unknown product → `404 Not Found`

## Running the Project

### Option 1 — Hosted Demo

Streamlit demo: **`<[StockFlow](https://stockflow-dashboard.streamlit.app/)>`**

You can use the demo to:
- register `in`/`out` stock movements
- validate input rules through the UI
- check current inventory for an existing product

### Option 2 — Run Locally

1. Install dependencies:

```bash
pip install -r requirements.txt
```

2. Start the API server:

```bash
uvicorn Backend.main:app --reload
```

3. Open API docs:
- Swagger UI: `http://127.0.0.1:8000/docs`


4. (Optional) Start the Streamlit demo in a second terminal:

```bash
streamlit run Frontend/app.py
```

## Future Improvements

Current scope is intentionally simple and not production-ready.

Known limitations:
- no persistent storage (in-memory state only)
- no caching layer
- no authentication/authorization
- no load balancing or horizontal scaling setup
- no containerization (Docker)

Reasonable next steps:
- add database persistence and migration strategy
- introduce unit/integration tests with CI checks
- add auth and request-rate protection
- package with Docker for consistent environments
- evolve service design for multi-instance deployments
