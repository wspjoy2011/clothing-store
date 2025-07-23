from typing import List, Optional

from pydantic import BaseModel


class RangeFilterSchema(BaseModel):
    """Schema for range filter data"""
    min: int
    max: int
    type: str = "range"


class PriceRangeFilterSchema(BaseModel):
    """Schema for price range filter data"""
    min: float
    max: float
    type: str = "price_range"


class CheckboxFilterSchema(BaseModel):
    """Schema for checkbox filter data"""
    values: List[str]
    type: str = "checkbox"


class AvailabilityFilterSchema(BaseModel):
    """Schema for availability filter data"""
    type: str = "boolean"
    default: bool = False


class FiltersResponseSchema(BaseModel):
    """API response schema for filters data"""
    gender: Optional[CheckboxFilterSchema] = None
    year: Optional[RangeFilterSchema] = None
    price: Optional[PriceRangeFilterSchema] = None
    is_available: Optional[AvailabilityFilterSchema] = None
