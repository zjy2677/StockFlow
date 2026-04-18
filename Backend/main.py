from __future__ import annotations
from fastapi import FastAPI, HTTPException
from backend.service import(
    MovementRequest,
    MovementResponse,
    StockResponse,
    StockService,
)

# create a fastapi object app with tile and version
app = FastAPI(title="StockFlow API", version="1.0.0")

# create a StockService obkect
service = StockService()
