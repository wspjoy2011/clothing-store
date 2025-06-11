from typing import Optional, Union
from datetime import datetime, date

from apps.accounts.dto.tokens import (
    ActivationTokenDTO,
    PasswordResetTokenDTO,
    RefreshTokenDTO
)
from apps.accounts.dto.users import (
    UserDTO,
    UserWithProfileDTO,
    UserProfileDTO,
    UserGroupDTO
)


class DateConverterMixin:
    """Mixin for converting database values to datetime and date objects"""

    def convert_to_datetime(self, value: Union[datetime, str, None]) -> Optional[datetime]:
        """Convert database value to datetime"""
        if value is None:
            return None
        if isinstance(value, datetime):
            return value
        if isinstance(value, str):
            try:
                return datetime.fromisoformat(value.replace('Z', '+00:00'))
            except ValueError:
                return None
        return value

    def convert_to_date(self, value: Union[date, datetime, str, None]) -> Optional[date]:
        """Convert database value to date"""
        if value is None:
            return None
        if isinstance(value, date):
            return value
        if isinstance(value, datetime):
            return value.date()
        if isinstance(value, str):
            try:
                return date.fromisoformat(value)
            except ValueError:
                return None
        return value


class DTOMapperMixin:
    """Mixin for mapping database rows to DTO objects"""

    def convert_to_datetime(self, value: Union[datetime, str, None]) -> Optional[datetime]:
        """Stub method for datetime conversion. Must be implemented by inheriting classes."""
        raise NotImplementedError(
            "Subclass must implement convert_to_datetime method or inherit from DateConverterMixin")

    def convert_to_date(self, value: Union[date, datetime, str, None]) -> Optional[date]:
        """Stub method for date conversion. Must be implemented by inheriting classes."""
        raise NotImplementedError("Subclass must implement convert_to_date method or inherit from DateConverterMixin")

    def map_to_user_dto(self, row) -> UserDTO:
        """Map database row to UserDTO"""
        return UserDTO(
            id=int(row[0]),
            email=row[1],
            is_active=bool(row[2]),
            created_at=self.convert_to_datetime(row[3]),
            updated_at=self.convert_to_datetime(row[4]),
            group_id=int(row[5]) if row[5] else None,
            group_name=row[6] if row[6] else None
        )

    def map_user_dto_with_group_name(self, row, group_name: Optional[str]) -> UserDTO:
        """Create UserDTO from row data with separate group_name parameter"""
        return UserDTO(
            id=int(row[0]),
            email=row[1],
            is_active=bool(row[2]),
            created_at=self.convert_to_datetime(row[3]),
            updated_at=self.convert_to_datetime(row[4]),
            group_id=int(row[5]) if row[5] else None,
            group_name=group_name
        )

    def map_to_user_with_profile_dto(self, row) -> UserWithProfileDTO:
        """Map database row to UserWithProfileDTO"""
        return UserWithProfileDTO(
            id=int(row[0]),
            email=row[1],
            is_active=bool(row[2]),
            created_at=self.convert_to_datetime(row[3]),
            updated_at=self.convert_to_datetime(row[4]),
            group_id=int(row[5]) if row[5] else None,
            group_name=row[6] if row[6] else None,
            first_name=row[7],
            last_name=row[8],
            avatar=row[9],
            gender=row[10],
            date_of_birth=self.convert_to_date(row[11]),
            info=row[12]
        )

    def map_to_profile_dto(self, row) -> UserProfileDTO:
        """Map database row to UserProfileDTO"""
        return UserProfileDTO(
            id=int(row[0]),
            first_name=row[1],
            last_name=row[2],
            avatar=row[3],
            gender=row[4],
            date_of_birth=self.convert_to_date(row[5]),
            info=row[6],
            user_id=int(row[7])
        )

    def map_to_group_dto(self, row) -> UserGroupDTO:
        """Map database row to UserGroupDTO"""
        return UserGroupDTO(
            id=int(row[0]),
            name=row[1]
        )

    def map_to_activation_token_dto(self, row) -> ActivationTokenDTO:
        """Map database row to ActivationTokenDTO"""
        return ActivationTokenDTO(
            id=int(row[0]),
            token=row[1],
            expires_at=self.convert_to_datetime(row[2]),
            user_id=int(row[3])
        )

    def map_to_password_reset_token_dto(self, row) -> PasswordResetTokenDTO:
        """Map database row to PasswordResetTokenDTO"""
        return PasswordResetTokenDTO(
            id=int(row[0]),
            token=row[1],
            expires_at=self.convert_to_datetime(row[2]),
            user_id=int(row[3])
        )

    def map_to_refresh_token_dto(self, row) -> RefreshTokenDTO:
        """Map database row to RefreshTokenDTO"""
        return RefreshTokenDTO(
            id=int(row[0]),
            token=row[1],
            expires_at=self.convert_to_datetime(row[2]),
            user_id=int(row[3])
        )


class AccountsRepositoryMixin(DateConverterMixin, DTOMapperMixin):
    """Base mixin for database repositories that provides data conversion and DTO mapping functionality"""
    pass
