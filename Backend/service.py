from __future__ import annotations
from typing import Dict
from fastapi import HTTPException
from pydantic import BaseModel, Field, field_validator
import re 

# define a global value checker
def id_value_checker(value: str) -> str:
    # cleans spaces in the front and at the end
    clean_id = value.strip()
    
    # make sure that product_id is not empty 
    if not clean_id:
        raise ValueError("product_id must be a non-empty string")
      
    # removes all the valid characters, anything remains -> invalid
    remaining = re.sub(r"[A-Za-z0-9]","",clean_id)
    if remaining:
        special_characters = re.sub(r" ","",remaining)
        if " " in remaining:
            if special_characters:
                raise ValueError(f"Your input product_id contains invalid special characters {set(special_characters)} and empty space(s)")
            else:
                raise ValueError("Your input product_id contains invalid empty space(s)")
        raise ValueError(f"Your input product_id contains invalid special characters {set(special_characters)}")
    if len(clean_id) > 30:
        raise ValueError("product_id is too long and exceeds 30 characters")
    return clean_id

# This will later be used by POST method
class MovementRequest(BaseModel):
    # No default set to product_id but it has to conatin at least 1 character and at most 30 characters
    product_id: str = Field(...,min_length=1,max_length=30)
    # No default set to quantity but it has to be greater than or equal to 1
    quantity: int = Field(...,ge=1, le=1_000_000)
    # "type" is either in/out defined as string 
    type: str

    # Validator for the product_id
    @field_validator("product_id")
    @classmethod
    def validate_product_id(cls, value: str) -> str:
        return id_value_checker(value)
   

    # frontend will make sure user can only select "in" or "out" but validation is also need for security reasons? 
    @field_validator("type")
    @classmethod
    def validate_type(cls, value: str) -> str:
        # check if type is in "in" or "out"
        normalized = value.strip().lower()
        if normalized not in {"in","out"}:
            raise ValueError("type must be either 'in' or 'out'")
        return normalized
      
# This is for structuring a response
class MovementResponse(BaseModel):
    message: str
    product_id: str
    current_stock: int 

# This will later be used by GET method
class StockResponse(BaseModel):
    product_id: str
    current_stock: int

# This is where backend logic lives
class StockService:
    def __init__(self) -> None:
        # initiate a private run-time dic to store product_id and corresponding inventory 
        self._stock: Dict[str,int]={}

    def register_movement(self, movement: MovementRequest) -> MovementResponse:
        product_id = movement.product_id
        quantity = movement.quantity
        if movement.type == "in":
            # get current stock if exists else default 0
            current_stock = self._stock.get(product_id, 0)
            # update current stock with quantity 
            current_stock += quantity
            # update current stock in dic
            self._stock[product_id] = current_stock      
            return MovementResponse(
                message = "This in-stock movement has been registered in the database successfully",
                product_id = product_id,
                current_stock = current_stock,
            )
      
        if product_id not in self._stock:
            raise HTTPException(
                status_code = 404,
                detail = "This product was never registered in the database",
            )
        
        current_stock = self._stock[product_id]
        current_stock -= quantity 
        if current_stock < 0:
            raise HTTPException(
                status_code=400,
                detail="Negative stock after this operation, insufficient stock for this movement",
            )

        self._stock[product_id] = current_stock
        return MovementResponse(
            message="This out-stock movement has been registered in the database successfully",
            product_id = product_id,
            current_stock = current_stock,
        )
      
    def get_stock(self, product_id: str) -> StockResponse:
        try:
             clean_id = id_value_checker(product_id)
        except ValueError as e:
            raise HTTPException(
                status_code=422,
                detail=str(e),
            )
        if clean_id not in self._stock:
            raise HTTPException(
                status_code=404,
                detail= "Product with this product_id was never registered in the database",
            )
        return StockResponse(product_id=clean_id, current_stock=self._stock[clean_id])
        
        
stock_service = StockService()
