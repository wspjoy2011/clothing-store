import datetime as datetime_lib
from datetime import datetime

from apps.accounts.dto.tokens import CreateTokenDTO
from apps.accounts.dto.users import LoginResponseDTO, UserDTO, UserLoginDTO
from apps.accounts.interfaces.repositories import (
    TokenRepositoryInterface,
    UserRepositoryInterface,
)
from apps.accounts.interfaces.services import AuthenticationServiceInterface
from apps.accounts.repositories.exceptions import TokenCreationError
from apps.accounts.services.exceptions import (
    InvalidCredentialsError,
    InvalidRefreshTokenError,
    LoginError,
    TokenGenerationError,
    TokenValidationError,
    UserInactiveError,
    UserNotFoundError,
)
from db.interfaces import TransactionManagerInterface
from security.exceptions import (
    EmptyPasswordError,
    EmptyTokenError,
    ExpiredTokenError,
    InvalidTokenError,
    InvalidTokenTypeError,
    VerificationError,
)
from security.exceptions import TokenCreationError as SecurityTokenCreationError
from security.interfaces import JWTManagerInterface, PasswordManagerInterface
from settings.logging_config import get_logger

logger = get_logger(__name__, "accounts")


class AuthenticationService(AuthenticationServiceInterface):
    """Service for signing users in and out and refreshing their session"""

    def __init__(
            self,
            user_repository: UserRepositoryInterface,
            token_repository: TokenRepositoryInterface,
            password_manager: PasswordManagerInterface,
            jwt_manager: JWTManagerInterface,
            transaction_manager: TransactionManagerInterface
    ):
        """
        Initialize the service

        Args:
            user_repository: Repository for user data operations
            token_repository: Repository for token operations
            password_manager: Manager for password hashing and verification
            jwt_manager: Manager for JWT token operations
            transaction_manager: Manager owning transaction boundaries
        """
        self._user_repository = user_repository
        self._token_repository = token_repository
        self._password_manager = password_manager
        self._jwt_manager = jwt_manager
        self._transaction_manager = transaction_manager

    async def login_user(self, login_data: UserLoginDTO) -> LoginResponseDTO:
        """
        Authenticate user and generate JWT tokens

        Args:
            login_data: User login credentials (email and password)

        Returns:
            LoginResponseDTO with access and refresh tokens

        Raises:
            UserNotFoundError: If user with given email is not found
            UserInactiveError: If user account is not activated
            InvalidCredentialsError: If password is incorrect
            TokenGenerationError: If JWT token generation fails
            LoginError: If login fails for other reasons
        """
        logger.info(f"Starting login process for email: {login_data.email}")

        user = await self._user_repository.get_user_by_email(login_data.email)
        if not user:
            logger.warning(f"Login failed: User with email {login_data.email} not found")
            raise UserNotFoundError(f"User with email '{login_data.email}' not found")

        if not user.is_active:
            logger.warning(f"Login failed: User with email {login_data.email} is not activated")
            raise UserInactiveError(f"User account with email '{login_data.email}' is not activated")

        hashed_password = await self._user_repository.get_hashed_password_by_email(login_data.email)
        if not hashed_password:
            logger.error(f"Login failed: Could not retrieve password for email {login_data.email}")
            raise InvalidCredentialsError("Invalid email or password")

        try:
            password_valid = await self._password_manager.verify_password(login_data.password, hashed_password)
            if not password_valid:
                logger.warning(f"Login failed: Invalid password for email {login_data.email}")
                raise InvalidCredentialsError("Invalid email or password")
        except (EmptyPasswordError, VerificationError) as e:
            logger.error(f"Password verification failed for user {login_data.email}: {e}")
            raise InvalidCredentialsError("Invalid email or password")

        token_payload = {
            "user_id": user.id,
            "email": user.email,
            "group_id": user.group_id,
            "group_name": user.group_name
        }

        try:
            access_token = self._jwt_manager.create_access_token(token_payload)
            refresh_token = self._jwt_manager.create_refresh_token(token_payload)

            logger.info(f"JWT tokens generated successfully for user: {login_data.email}, user_id: {user.id}")

            await self._store_refresh_token(user.id, refresh_token)

        except SecurityTokenCreationError as e:
            logger.error(f"JWT token generation failed for user {user.id}: {e}")
            raise TokenGenerationError(f"Failed to generate authentication tokens: {e}", e)
        except Exception as e:
            logger.error(f"Unexpected error during login for user {user.id}: {e}")
            raise LoginError(f"Login failed due to unexpected error: {e}", e)
        else:
            return LoginResponseDTO(
                access_token=access_token,
                refresh_token=refresh_token
            )

    async def logout_user(self, refresh_token: str) -> None:
        """
        Logout user by removing refresh token from database

        Args:
            refresh_token: Refresh token to be removed

        Returns:
            None - always succeeds, no exceptions raised even if token doesn't exist
        """
        logger.info("Starting user logout process")

        try:
            await self._token_repository.delete_refresh_token(refresh_token)
            logger.info("Logout completed successfully")
        except Exception as e:
            logger.warning(f"Error during logout (ignored): {e}")

        return None

    async def get_user_by_refresh_token(self, refresh_token: str) -> UserDTO:
        """
        Get user information by refresh token

        Args:
            refresh_token: Valid refresh token

        Returns:
            UserDTO with user information

        Raises:
            InvalidRefreshTokenError: If refresh token is invalid or expired
            UserNotFoundError: If user associated with token is not found
            TokenValidationError: If token validation fails
        """
        logger.info("Starting get user by refresh token process")

        try:
            token_payload = self._jwt_manager.verify_refresh_token(refresh_token)
            logger.debug(f"Refresh token verified successfully for email: {token_payload.get('email')}")
        except Exception as e:
            logger.warning(f"Invalid refresh token provided: {e}")
            raise InvalidRefreshTokenError("Invalid or expired refresh token")

        stored_token = await self._token_repository.get_refresh_token_by_token(refresh_token)
        if not stored_token:
            logger.warning("Refresh token not found in database")
            raise InvalidRefreshTokenError("Refresh token not found or has been revoked")

        current_time = datetime.now(datetime_lib.UTC)
        if stored_token.expires_at <= current_time:
            logger.warning("Refresh token has expired")
            try:
                await self._token_repository.delete_refresh_token(refresh_token)
            except Exception as e:
                logger.warning(f"Failed to delete expired token: {e}")
            raise InvalidRefreshTokenError("Refresh token has expired")

        user_email = token_payload.get('email')
        if not user_email:
            logger.error("Email not found in refresh token payload")
            raise TokenValidationError("Invalid token payload: missing email")

        user = await self._user_repository.get_user_by_email(user_email)
        if not user:
            logger.warning(f"User with email {user_email} not found")
            raise UserNotFoundError(f"User with email '{user_email}' not found")

        logger.info(f"User retrieved successfully by refresh token for email: {user_email}")
        return user

    async def refresh_access_token(self, refresh_token: str) -> LoginResponseDTO:
        """
        Exchange a refresh token for a new pair, invalidating the one presented

        Business logic: Verify the token, confirm it is still stored, then issue a
        new pair and replace the stored token in one transaction, so a leaked
        refresh token stops working as soon as its owner uses it once

        Args:
            refresh_token: Valid refresh token

        Returns:
            New access and refresh tokens

        Raises:
            InvalidRefreshTokenError: If refresh token is invalid, expired, or not found in database
            UserNotFoundError: If user associated with token is not found
            TokenValidationError: If token validation fails
            TokenGenerationError: If new access token generation fails
        """
        logger.info("Starting access token refresh")

        try:
            payload = self._jwt_manager.verify_refresh_token(refresh_token)
            user_id = payload.get("user_id")

            if not user_id:
                logger.warning("Refresh token payload missing user_id")
                raise InvalidRefreshTokenError("Invalid refresh token payload")

            logger.debug(f"Refresh token payload verified for user_id: {user_id}")
        except (ExpiredTokenError, InvalidTokenError,
                InvalidTokenTypeError, EmptyTokenError) as e:
            logger.warning(f"Refresh token verification failed: {e}")
            raise InvalidRefreshTokenError(f"Invalid refresh token: {str(e)}", e)
        except Exception as e:
            logger.error(f"Unexpected error during refresh token verification: {e}")
            raise TokenValidationError(f"Token validation failed: {str(e)}", e)

        try:
            stored_token = await self._token_repository.get_refresh_token_by_token(refresh_token)
        except Exception as e:
            logger.error(f"Error checking refresh token in database: {e}")
            raise TokenValidationError(f"Failed to validate refresh token: {str(e)}", e)

        if not stored_token:
            logger.warning(f"Refresh token not found in database for user_id: {user_id}")
            raise InvalidRefreshTokenError("Refresh token not found or expired")

        logger.debug(f"Refresh token found in database for user_id: {user_id}")

        try:
            user = await self._user_repository.get_user_by_id(user_id)
            if not user:
                logger.warning(f"User not found for user_id: {user_id}")
                raise UserNotFoundError(f"User with ID {user_id} not found")

            logger.debug(f"User found for token refresh: {user.email}")
        except Exception as e:
            logger.error(f"Error getting user for token refresh: {e}")
            raise UserNotFoundError(f"Failed to get user data: {str(e)}", e)

        try:
            token_payload = {
                "user_id": user.id,
                "email": user.email,
                "group_id": user.group_id,
                "group_name": user.group_name
            }

            new_access_token = self._jwt_manager.create_access_token(token_payload)
            new_refresh_token = self._jwt_manager.create_refresh_token(token_payload)
            logger.info(f"New token pair created for user: {user.email}")

            async with self._transaction_manager.atomic():
                await self._token_repository.delete_refresh_token(refresh_token)
                await self._store_refresh_token(user.id, new_refresh_token)

            logger.info(f"Refresh token rotated for user {user.id}")

            return LoginResponseDTO(
                access_token=new_access_token,
                refresh_token=new_refresh_token
            )

        except SecurityTokenCreationError as e:
            logger.error(f"Failed to create new access token for user {user.id}: {e}")
            raise TokenGenerationError(f"Failed to generate new access token: {str(e)}", e)
        except Exception as e:
            logger.error(f"Unexpected error creating access token for user {user.id}: {e}")
            raise TokenGenerationError(f"Token generation failed: {str(e)}", e)

    async def _store_refresh_token(self, user_id: int, refresh_token: str) -> None:
        """
        Store refresh token in database

        Args:
            user_id: ID of the user
            refresh_token: JWT refresh token to store

        Raises:
            TokenCreationError: If token storage fails
        """
        try:
            expiration = self._jwt_manager.get_token_expiration(refresh_token)

            token_data = CreateTokenDTO(
                token=refresh_token,
                expires_at=expiration,
                user_id=user_id
            )

            await self._token_repository.create_refresh_token(token_data)
            logger.debug(f"Refresh token stored successfully for user {user_id}")

        except Exception as e:
            logger.error(f"Failed to store refresh token for user {user_id}: {e}")
            raise TokenCreationError(f"Failed to store refresh token for user {user_id}", e)
