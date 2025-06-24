from dataclasses import dataclass
from typing import Dict, Any, Optional


@dataclass
class OAuthUserInfo:
    """
    Standardized user information from OAuth providers.
    """
    provider: str
    provider_id: str
    email: str
    name: str
    first_name: Optional[str] = None
    last_name: Optional[str] = None
    avatar_url: Optional[str] = None
    locale: Optional[str] = None
    verified_email: bool = True
    raw_data: Optional[Dict[str, Any]] = None
