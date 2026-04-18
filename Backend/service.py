from __future__ import annotations
from typing import Dict
from fastapi import HTTPException
from pydantic import BaseModel, Field, field_validator

class MovementRequest(BaseModel):
  # No default set to product_id but it has to conatin at least 1 character
  product_id = Field(...,min_length=1)
  # No default set to quantity but it has to be greater than or equal to 0
  quantity = Field(...,ge=0)
  # "type" is either in/out defined as string 
  type: str

  # Validator for the product_id
  @field_validator("product_id")
  @classmethod
  def validate_product_id(cls, value: str) -> str:
    clean_id = value.strip()
    if not clean_id:
      raise ValueError("product_id must be a non-empty string")
    return clean_id




