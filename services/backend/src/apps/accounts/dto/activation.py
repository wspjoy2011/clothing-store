"""Data transfer objects for account activation"""

from dataclasses import dataclass


@dataclass
class ActivateAccountDTO:
    """Data transfer object for account activation request"""
    email: str
    token: str
