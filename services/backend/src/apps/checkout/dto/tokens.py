from dataclasses import dataclass
from datetime import datetime


@dataclass
class CartTokenDTO:
    """Data transfer object for cart token for anonymous users"""
    id: int
    token: str
    expires_at: datetime
    created_at: datetime
    updated_at: datetime
