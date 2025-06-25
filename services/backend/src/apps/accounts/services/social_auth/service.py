"""
Google social authentication service.
"""

import secrets

from email_validator import validate_email, EmailNotValidError

from oauth.interfaces import OAuthProviderInterface
from oauth.dto import OAuthUserInfo
from oauth.exceptions import OAuthError, TokenVerificationError, UserInfoError

from apps.accounts.dto.users import CreateUserDTO
from apps.accounts.dto.tokens import CreateTokenDTO
from apps.accounts.enums.user_groups import UserGroupEnum
from apps.accounts.interfaces.repositories import (
    UserRepositoryInterface,
    UserGroupRepositoryInterface,
    TokenRepositoryInterface
)
from apps.accounts.services.social_auth.dto import (
    SocialAuthRequest,
    SocialUserProfile,
    SocialAuthResult,
    SocialAuthTokens,
    SocialAuthResponse
)
from apps.accounts.services.social_auth.exceptions import (
    SocialAuthError,
    SocialProviderError,
    SocialTokenError,
    SocialUserInfoError,
    SocialUserValidationError,
    SocialUserLookupError,
    SocialTokenGenerationError
)
from apps.accounts.services.social_auth.interfaces import SocialAuthServiceInterface
from apps.accounts.repositories.exceptions import (
    UserCreationError as RepoUserCreationError
)
from db.transaction_context import atomic
from security.interfaces import PasswordManagerInterface, JWTManagerInterface
from security.exceptions import TokenCreationError as SecurityTokenCreationError
from notifications.email.interfaces import EmailSenderInterface
from notifications.exceptions.email import BaseEmailError
from settings.config import config
from settings.logging_config import get_logger

logger = get_logger(__name__, "social_auth")


class GoogleSocialAuthService(SocialAuthServiceInterface):
    """
    Google social authentication service.
    Uses injected OAuth provider for authentication and handles business logic.
    """

    def __init__(
            self,
            oauth_provider: OAuthProviderInterface,
            user_repository: UserRepositoryInterface,
            user_group_repository: UserGroupRepositoryInterface,
            token_repository: TokenRepositoryInterface,
            password_manager: PasswordManagerInterface,
            jwt_manager: JWTManagerInterface,
            email_sender: EmailSenderInterface
    ):
        """
        Initialize Google social auth service.

        Args:
            oauth_provider: OAuth provider instance (injected)
            user_repository: Repository for user data operations
            user_group_repository: Repository for user group operations
            token_repository: Repository for token operations
            password_manager: Manager for password hashing and verification
            jwt_manager: Manager for JWT token operations
            email_sender: Email sender for notifications
        """
        self._oauth_provider = oauth_provider
        self._user_repository = user_repository
        self._user_group_repository = user_group_repository
        self._token_repository = token_repository
        self._password_manager = password_manager
        self._jwt_manager = jwt_manager
        self._email_sender = email_sender
        self.provider_name = oauth_provider.provider_name

    async def authenticate(self, request: SocialAuthRequest) -> SocialAuthResponse:
        """
        Authenticate user through OAuth provider.

        Args:
            request: Social authentication request

        Returns:
            Social authentication response

        Raises:
            SocialAuthError: If authentication fails
        """
        try:
            oauth_user_info = await self._oauth_provider.authenticate_user(request.access_token)
        except TokenVerificationError as e:
            raise SocialTokenError(
                f"Token verification failed: {str(e)}",
                self.provider_name,
                e.status_code,
                e
            )
        except UserInfoError as e:
            raise SocialUserInfoError(
                f"User info extraction failed: {str(e)}",
                self.provider_name,
                e.missing_fields,
                e
            )
        except OAuthError as e:
            raise SocialProviderError(
                f"OAuth error: {str(e)}",
                self.provider_name,
                e
            )

        user_profile = self._convert_to_social_profile(oauth_user_info)
        self._validate_profile(user_profile)

        try:
            auth_result = await self._handle_user(user_profile)
            tokens = await self._generate_tokens(auth_result)
        except SocialAuthError:
            raise
        except Exception as e:
            logger.error(f"Social authentication failed: {str(e)}", exc_info=True)
            raise SocialAuthError(
                f"Authentication failed: {str(e)}",
                self.provider_name,
                e
            )

        return SocialAuthResponse(
            success=True,
            tokens=tokens,
            user_profile=user_profile,
            is_new_user=not auth_result.user_exists,
            message=f"{self.provider_name.title()} authentication successful",
            provider=self.provider_name
        )

    async def get_supported_providers(self) -> list[str]:
        """
        Get list of supported providers.

        Returns:
            List with current provider name
        """
        return [self.provider_name]

    def _convert_to_social_profile(self, oauth_info: OAuthUserInfo) -> SocialUserProfile:
        """
        Convert OAuth user info to social profile.

        Args:
            oauth_info: OAuth user information

        Returns:
            Social user profile
        """
        return SocialUserProfile(
            provider=oauth_info.provider,
            provider_id=oauth_info.provider_id,
            email=oauth_info.email,
            name=oauth_info.name,
            first_name=oauth_info.first_name,
            last_name=oauth_info.last_name,
            avatar_url=oauth_info.avatar_url,
            locale=oauth_info.locale,
            verified_email=oauth_info.verified_email
        )

    def _validate_profile(self, profile: SocialUserProfile) -> None:
        """
        Validate social user profile.

        Args:
            profile: Social user profile

        Raises:
            SocialUserValidationError: If profile is invalid
        """
        missing_fields = []

        if not profile.email:
            missing_fields.append("email")
        if not profile.provider_id:
            missing_fields.append("provider_id")
        if not profile.name:
            missing_fields.append("name")

        if missing_fields:
            raise SocialUserValidationError(
                f"Missing required fields: {', '.join(missing_fields)}",
                profile.provider
            )

        try:
            validation_result = validate_email(profile.email)
            profile.email = validation_result.normalized
        except EmailNotValidError as e:
            raise SocialUserValidationError(
                f"Invalid email format: {str(e)}",
                profile.provider
            )

        if profile.provider == "google" and not profile.verified_email:
            raise SocialUserValidationError(
                "Google email must be verified",
                profile.provider
            )

    @atomic(['_user_repository', '_user_group_repository'])
    async def _handle_user(self, profile: SocialUserProfile) -> SocialAuthResult:
        """
        Handle user lookup/creation.

        Args:
            profile: Social user profile

        Returns:
            Social authentication result

        Raises:
            SocialUserLookupError: If user operations fail
        """
        logger.info(f"Looking up user for email: {profile.email}")

        existing_user = await self._user_repository.get_user_by_email(profile.email)

        if existing_user:
            logger.info(f"Existing user found for email: {profile.email}, user_id: {existing_user.id}")

            if not existing_user.is_active:
                try:
                    await self._user_repository.update_user_status(existing_user.id, True)
                    logger.info(f"User {existing_user.id} activated through social auth")
                except Exception as e:
                    logger.error(f"Failed to activate user {existing_user.id}: {e}")
                    raise SocialUserLookupError(
                        f"Failed to activate user: {str(e)}",
                        profile.provider,
                        e
                    )

            return SocialAuthResult(
                success=True,
                user_profile=profile,
                user_exists=True,
                user_id=existing_user.id,
                message="User authenticated successfully",
                provider=profile.provider
            )

        logger.info(f"Creating new user for email: {profile.email}")

        default_group_name = UserGroupEnum.get_default_group()
        default_group = await self._user_group_repository.get_group_by_name(default_group_name)
        if not default_group:
            logger.error("Default group 'user' not found in database")
            raise SocialUserLookupError(
                "Default user group not found",
                profile.provider
            )

        random_password = secrets.token_urlsafe(32)
        hashed_password = self._password_manager.hash_password(random_password)

        user_data = CreateUserDTO(
            email=profile.email,
            password=hashed_password,
            group_id=default_group.id
        )

        try:
            created_user = await self._user_repository.create_user(user_data)
            await self._user_repository.update_user_status(created_user.id, True)
        except RepoUserCreationError as e:
            logger.error(f"User creation failed for {profile.email}: {e}")
            raise SocialUserLookupError(
                f"Failed to create user: {str(e)}",
                profile.provider,
                e
            )
        except Exception as e:
            logger.error(f"User handling failed for {profile.email}: {e}", exc_info=True)
            raise SocialUserLookupError(
                f"Database error during user processing: {str(e)}",
                profile.provider,
                e
            )

        logger.info(f"New user created and activated: {profile.email}, user_id: {created_user.id}")

        try:
            await self._send_social_registration_email(profile.email)
            logger.info(f"Welcome email sent to new social user: {profile.email}")
        except BaseEmailError as e:
            logger.warning(f"Failed to send welcome email to {profile.email}: {e}")

        return SocialAuthResult(
            success=True,
            user_profile=profile,
            user_exists=False,
            user_id=created_user.id,
            message="User created and authenticated successfully",
            provider=profile.provider
        )

    async def _generate_tokens(self, auth_result: SocialAuthResult) -> SocialAuthTokens:
        """
        Generate JWT tokens.

        Args:
            auth_result: Authentication result

        Returns:
            JWT tokens

        Raises:
            SocialTokenGenerationError: If token generation fails
        """
        logger.info(f"Generating tokens for user: {auth_result.user_profile.email}")

        user = await self._user_repository.get_user_by_email(auth_result.user_profile.email)
        if not user:
            raise SocialTokenGenerationError(
                "User not found after authentication",
                auth_result.provider
            )

        token_payload = {
            "user_id": user.id,
            "email": user.email,
            "group_id": user.group_id,
            "group_name": user.group_name
        }

        try:
            access_token = self._jwt_manager.create_access_token(token_payload)
            refresh_token = self._jwt_manager.create_refresh_token(token_payload)
            await self._store_refresh_token(user.id, refresh_token)
        except SecurityTokenCreationError as e:
            logger.error(f"JWT token generation failed: {e}")
            raise SocialTokenGenerationError(
                f"Failed to generate authentication tokens: {str(e)}",
                auth_result.provider,
                e
            )
        except Exception as e:
            logger.error(f"Token generation failed: {e}", exc_info=True)
            raise SocialTokenGenerationError(
                f"Token generation error: {str(e)}",
                auth_result.provider,
                e
            )

        logger.info(f"JWT tokens generated successfully for user: {auth_result.user_profile.email}")

        return SocialAuthTokens(
            access_token=access_token,
            refresh_token=refresh_token,
            token_type="bearer",
            expires_in=3600
        )

    async def _store_refresh_token(self, user_id: int, refresh_token: str) -> None:
        """
        Store refresh token in database.

        Args:
            user_id: ID of the user
            refresh_token: JWT refresh token to store

        Raises:
            SocialTokenGenerationError: If token storage fails
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
            raise SocialTokenGenerationError(
                f"Failed to store refresh token: {str(e)}",
                self.provider_name,
                e
            )

    async def _send_social_registration_email(self, email: str) -> None:
        """
        Send welcome email for new social registration.

        Args:
            email: User's email address

        Raises:
            BaseEmailError: If email sending fails
        """
        login_link = config.build_frontend_url('/accounts/login')

        logger.info(f"Sending social registration welcome email to {email}")

        try:
            await self._email_sender.send_activation_complete_email(email, login_link)
            logger.info(f"Social registration welcome email sent successfully to {email}")
        except BaseEmailError as e:
            logger.error(f"Failed to send social registration welcome email to {email}: {e}")
            raise
