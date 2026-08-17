"""Data transfer objects for security operations"""

from dataclasses import dataclass
from datetime import datetime
from typing import Any, Dict, Optional


@dataclass
class JWTPayloadDTO:
    """Data transfer object for JWT payload"""
    user_id: int
    email: str
    group_id: int
    group_name: str
    exp: int
    iat: int
    type: str
    raw_payload: Dict[str, Any]

    @classmethod
    def from_payload(cls, payload: Dict[str, Any]) -> 'JWTPayloadDTO':
        """Create JWTPayloadDTO from raw payload dict"""
        return cls(
            user_id=payload.get('user_id'),
            email=payload.get('email'),
            group_id=payload.get('group_id'),
            group_name=payload.get('group_name'),
            exp=payload.get('exp'),
            iat=payload.get('iat'),
            type=payload.get('type'),
            raw_payload=payload
        )

    @property
    def expiration_datetime(self) -> Optional[datetime]:
        """Get expiration as datetime object"""
        if self.exp:
            return datetime.fromtimestamp(self.exp)
        return None

    @property
    def issued_at_datetime(self) -> Optional[datetime]:
        """Get issued at as datetime object"""
        if self.iat:
            return datetime.fromtimestamp(self.iat)
        return None

    @property
    def is_access_token(self) -> bool:
        """Check if token is access token"""
        return self.type == "access"

    @property
    def is_refresh_token(self) -> bool:
        """Check if token is refresh token"""
        return self.type == "refresh"
