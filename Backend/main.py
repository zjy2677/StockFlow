from __future__ import annotations
from fastapi import FastAPI, HTTPException
from Backend.service import(
    MovementRequest,
    MovementResponse,
    StockResponse,
    service,
)

# create a fastapi object app with tile and version
app = FastAPI(title="StockFlow API", version="1.0.0")

# Endpoint 1
@app.post("/movements", response_model=MovementResponse, status_code=201)
def create_movement(movement: MovementRequest) -> MovementResponse:
    try:
        return service.register_movement(movement)
    except HTTPException:
        raise

# Endpoint 2
@app.get("/products/{product_id}/stock", response_model=StockResponse)
def read_stock(product_id: str) -> StockResponse:
    try:
        return service.get_stock(product_id)
    except HTTPException:
        raise
