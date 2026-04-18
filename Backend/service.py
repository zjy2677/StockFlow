from __future__ import annotations
from typing import Dict
from fastapi import HTTPException
from pydantic import BaseModel, Field, field_validator

class MovementRequest(BaseModel):
  message: str
  product_id: str
  quantity: str

