from typing import List, Optional

from pydantic import BaseModel


class RangeFilterSchema(BaseModel):
    """Schema for range filter data"""
    min: int
    max: int
    type: str = "range"


class CheckboxFilterSchema(BaseModel):
    """Schema for checkbox filter data"""
    values: List[str]
    type: str = "checkbox"


class FiltersResponseSchema(BaseModel):
    """API response schema for filters data"""
    gender: Optional[CheckboxFilterSchema] = None
    year: Optional[RangeFilterSchema] = None
