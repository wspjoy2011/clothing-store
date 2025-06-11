"""User group enumerations"""

from enum import Enum


class UserGroupEnum(str, Enum):
    """Enumeration for user groups that correspond to database values"""

    USER = "user"
    MODERATOR = "moderator"
    ADMIN = "admin"

    def __str__(self) -> str:
        """Return string representation of the enum value"""
        return self.value

    @classmethod
    def get_default_group(cls) -> str:
        """Get default group for new user registration"""
        return cls.USER.value

    @classmethod
    def get_all_groups(cls) -> list[str]:
        """Get list of all available groups"""
        return [group.value for group in cls]

    @classmethod
    def is_valid_group(cls, group_name: str) -> bool:
        """Check if group name is valid"""
        return group_name in cls.get_all_groups()
