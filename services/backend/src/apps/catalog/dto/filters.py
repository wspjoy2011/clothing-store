from dataclasses import dataclass
from typing import List, Optional


@dataclass
class RangeFilterDTO:
    """DTO for range filter data"""
    min: int
    max: int
    type: str = "range"


@dataclass
class CheckboxFilterDTO:
    """DTO for checkbox filter data"""
    values: List[str]
    type: str = "checkbox"


@dataclass
class AvailabilityFilterDTO:
    """DTO for availability filter data"""
    type: str = "boolean"
    default: bool = False


@dataclass
class FiltersDTO:
    """DTO containing all available filters"""
    gender: Optional[CheckboxFilterDTO] = None
    year: Optional[RangeFilterDTO] = None
    is_available: Optional[AvailabilityFilterDTO] = None
