"""Controllers for accounts module"""

from dataclasses import asdict

from fastapi import HTTPException

from apps.accounts.dto.password_reset import (
    PasswordResetRequestDTO,
    PasswordResetConfirmDTO,
    PasswordChangeDTO
)
from apps.accounts.dto.users import CreateUserDTO, UserLoginDTO
from apps.accounts.dto.activation import ActivateAccountDTO
from apps.accounts.interfaces.services import AccountServiceInterface
from apps.accounts.controllers.errors import client_message
from apps.accounts.validators.token import mask_token_for_logging
from apps.accounts.schemas.jwt_token import RefreshTokenResponse, RefreshTokenRequest
from apps.accounts.schemas.password_reset import (
    PasswordResetRequestSchema,
    PasswordResetRequestResponseSchema,
    PasswordResetConfirmSchema,
    PasswordResetConfirmResponseSchema,
    PasswordChangeResponseSchema,
    PasswordChangeSchema
)
from apps.accounts.schemas.user import (
    CreateUserSchema,
    CreateUserResponseSchema,
    UserResponseSchema,
    UserLoginSchema,
    LoginResponseSchema,
    LogoutSchema,
    LogoutResponseSchema,
    RefreshTokenResponseSchema
)
from apps.accounts.schemas.activation import (
    ActivateAccountSchema,
    ActivateAccountResponseSchema,
    ResendActivationSchema,
    ResendActivationResponseSchema
)
from apps.accounts.services.exceptions import (
    EmailAlreadyExistsError,
    UserCreationError,
    UserPasswordError,
    UserNotFoundError,
    UserAlreadyActivatedError,
    InvalidActivationTokenError,
    ExpiredActivationTokenError,
    UserInactiveError,
    InvalidCredentialsError,
    TokenGenerationError,
    LoginError,
    InvalidRefreshTokenError,
    TokenValidationError,
    PasswordResetEmailError,
    InvalidPasswordResetTokenError,
    ExpiredPasswordResetTokenError,
    PasswordResetTokenNotFoundError,
    PasswordResetError,
    PasswordResetRollbackError,
    IncorrectCurrentPasswordError,
    SamePasswordError,
    PasswordChangeError
)
from security.dto import JWTPayloadDTO
from settings.config import config
from settings.logging_config import get_logger

logger = get_logger(__name__, "accounts_controller")


async def create_user_controller(
        user_data: CreateUserSchema,
        account_service: AccountServiceInterface,
) -> CreateUserResponseSchema:
    """
    Controller for user registration

    Args:
        user_data: User registration data from request
        account_service: Account service for business logic

    Returns:
        CreateUserResponseSchema with created user data and success message

    Raises:
        HTTPException: 409 if email already exists, 400 for other creation errors
    """
    create_user_dto = CreateUserDTO(
        email=str(user_data.email),
        password=user_data.password
    )

    try:
        created_user = await account_service.register_user(create_user_dto)
    except EmailAlreadyExistsError as e:
        raise HTTPException(
            status_code=409,
            detail=client_message(e)
        )
    except (UserCreationError, UserPasswordError) as e:
        raise HTTPException(
            status_code=400,
            detail=client_message(e)
        )
    except Exception as e:
        logger.error(f"Unexpected error during user creation for email {user_data.email}: {e}")
        raise HTTPException(
            status_code=500,
            detail="Internal server error occurred during user creation"
        )
    else:
        user_response = UserResponseSchema(**asdict(created_user))
        return CreateUserResponseSchema(
            user=user_response,
            message="User created successfully"
        )


async def activate_account_controller(
        activation_data: ActivateAccountSchema,
        account_service: AccountServiceInterface,
) -> ActivateAccountResponseSchema:
    """
    Controller for account activation

    Args:
        activation_data: Account activation data from request
        account_service: Account service for business logic

    Returns:
        ActivateAccountResponseSchema with activated user data and success message

    Raises:
        HTTPException: 404 if user not found, 400 for activation errors, 410 for expired token
    """
    activate_account_dto = ActivateAccountDTO(
        email=str(activation_data.email),
        token=activation_data.token
    )

    try:
        activated_user = await account_service.activate_account(activate_account_dto)
    except UserNotFoundError as e:
        raise HTTPException(
            status_code=404,
            detail=client_message(e)
        )
    except UserAlreadyActivatedError as e:
        raise HTTPException(
            status_code=400,
            detail=client_message(e)
        )
    except InvalidActivationTokenError as e:
        raise HTTPException(
            status_code=400,
            detail=client_message(e)
        )
    except ExpiredActivationTokenError as e:
        raise HTTPException(
            status_code=410,
            detail=client_message(e)
        )
    except (UserCreationError, Exception) as e:
        logger.error(f"Unexpected error during account activation for email {activation_data.email}: {e}")
        raise HTTPException(
            status_code=500,
            detail="Internal server error occurred during account activation"
        )
    else:
        user_response = UserResponseSchema(**asdict(activated_user))
        return ActivateAccountResponseSchema(
            user=user_response,
            message="Account activated successfully"
        )


async def resend_activation_controller(
        resend_data: ResendActivationSchema,
        account_service: AccountServiceInterface,
) -> ResendActivationResponseSchema:
    """
    Controller for resending activation email

    Args:
        resend_data: Resend activation data from request
        account_service: Account service for business logic

    Returns:
        ResendActivationResponseSchema with success message and email

    Raises:
        HTTPException: 404 if user not found, 400 if user already activated, 500 for server errors
    """
    try:
        await account_service.resend_activation_email(str(resend_data.email))
    except UserNotFoundError as e:
        raise HTTPException(
            status_code=404,
            detail=client_message(e)
        )
    except UserAlreadyActivatedError as e:
        raise HTTPException(
            status_code=400,
            detail=client_message(e)
        )
    except Exception as e:
        logger.error(f"Unexpected error during activation email resend for email {resend_data.email}: {e}")
        raise HTTPException(
            status_code=500,
            detail="Internal server error occurred during activation email resend"
        )
    else:
        return ResendActivationResponseSchema(
            message="Activation email sent successfully",
            email=str(resend_data.email)
        )


async def login_user_controller(
        login_data: UserLoginSchema,
        account_service: AccountServiceInterface,
) -> LoginResponseSchema:
    """
    Controller for user login

    Args:
        login_data: User login data from request
        account_service: Account service for business logic

    Returns:
        LoginResponseSchema with JWT tokens

    Raises:
        HTTPException: 404 if user not found, 403 if user inactive, 401 for invalid credentials, 500 for server errors
    """
    user_login_dto = UserLoginDTO(
        email=str(login_data.email),
        password=login_data.password
    )

    try:
        login_response = await account_service.login_user(user_login_dto)
    except (UserNotFoundError, UserInactiveError) as e:
        logger.warning(f"Sign-in refused for {login_data.email}: {e}")
        raise HTTPException(
            status_code=401,
            detail=client_message(e)
        )
    except InvalidCredentialsError as e:
        raise HTTPException(
            status_code=401,
            detail=client_message(e)
        )
    except TokenGenerationError as e:
        raise HTTPException(
            status_code=500,
            detail=client_message(e)
        )
    except LoginError as e:
        raise HTTPException(
            status_code=500,
            detail=client_message(e)
        )
    except Exception as e:
        logger.error(f"Unexpected error during user login for email {login_data.email}: {e}")
        raise HTTPException(
            status_code=500,
            detail="Internal server error occurred during user login"
        )
    else:
        return LoginResponseSchema(**asdict(login_response))


async def logout_user_controller(
        logout_data: LogoutSchema,
        account_service: AccountServiceInterface,
) -> LogoutResponseSchema:
    """
    Controller for user logout

    Args:
        logout_data: User logout data from request
        account_service: Account service for business logic

    Returns:
        LogoutResponseSchema with success message

    Note:
        This controller never raises exceptions - logout always succeeds
    """
    await account_service.logout_user(logout_data.refresh_token)
    return LogoutResponseSchema()


async def get_user_by_refresh_token_controller(
        refresh_token: str,
        account_service: AccountServiceInterface,
) -> RefreshTokenResponseSchema:
    """
    Controller for getting user by refresh token

    Args:
        refresh_token: JWT refresh token from Authorization header
        account_service: Account service for business logic

    Returns:
        RefreshTokenResponseSchema with user data and success message

    Raises:
        HTTPException: 401 for invalid/expired tokens, 404 if user not found, 500 for server errors
    """
    try:
        user = await account_service.get_user_by_refresh_token(refresh_token)
    except InvalidRefreshTokenError as e:
        raise HTTPException(
            status_code=401,
            detail=client_message(e)
        )
    except UserNotFoundError as e:
        raise HTTPException(
            status_code=404,
            detail=client_message(e)
        )
    except TokenValidationError as e:
        raise HTTPException(
            status_code=401,
            detail=client_message(e)
        )
    except Exception as e:
        logger.error(f"Unexpected error during user retrieval by refresh token: {e}")
        raise HTTPException(
            status_code=500,
            detail="Internal server error occurred during user retrieval"
        )
    else:
        user_response = UserResponseSchema(**asdict(user))
        return RefreshTokenResponseSchema(
            user=user_response,
            message="User retrieved successfully"
        )


async def request_password_reset_controller(
        request_data: PasswordResetRequestSchema,
        account_service: AccountServiceInterface,
) -> PasswordResetRequestResponseSchema:
    """
    Controller for password reset request

    Args:
        request_data: Password reset request data from request
        account_service: Account service for business logic

    Returns:
        PasswordResetRequestResponseSchema with success message and email

    Raises:
        HTTPException: 500 if email sending fails (only for existing users)
    """
    reset_request_dto = PasswordResetRequestDTO(
        email=str(request_data.email)
    )

    try:
        await account_service.request_password_reset(reset_request_dto)
    except PasswordResetEmailError as e:
        logger.error(f"Password reset email could not be sent for {request_data.email}: {e}")
        raise HTTPException(
            status_code=503,
            detail="Password reset email could not be sent. Please try again."
        )
    except PasswordResetError as e:
        logger.error(f"Password reset could not be started for {request_data.email}: {e}")
        raise HTTPException(
            status_code=503,
            detail="Password reset could not be started. Please try again."
        )
    except Exception as e:
        logger.error(f"Unexpected error during password reset request for email {request_data.email}: {e}")
        raise HTTPException(
            status_code=500,
            detail="Internal server error occurred during password reset request"
        )
    else:
        return PasswordResetRequestResponseSchema(
            message="Password reset request processed successfully",
            email=str(request_data.email)
        )


async def confirm_password_reset_controller(
        confirm_data: PasswordResetConfirmSchema,
        account_service: AccountServiceInterface,
) -> PasswordResetConfirmResponseSchema:
    """
    Controller for password reset confirmation

    Args:
        confirm_data: Password reset confirmation data from request
        account_service: Account service for business logic

    Returns:
        PasswordResetConfirmResponseSchema with success message

    Raises:
        HTTPException: 400 for invalid/expired tokens, 404 for token not found, 500 for server errors
    """
    reset_confirm_dto = PasswordResetConfirmDTO(
        token=confirm_data.token,
        new_password=confirm_data.new_password
    )

    try:
        await account_service.confirm_password_reset(reset_confirm_dto)
    except InvalidPasswordResetTokenError as e:
        raise HTTPException(
            status_code=400,
            detail=client_message(e)
        )
    except ExpiredPasswordResetTokenError as e:
        raise HTTPException(
            status_code=400,
            detail=client_message(e)
        )
    except PasswordResetTokenNotFoundError as e:
        raise HTTPException(
            status_code=404,
            detail=client_message(e)
        )
    except PasswordResetRollbackError as e:
        logger.error(f"Password reset rolled back for token {mask_token_for_logging(confirm_data.token)}: {e}")
        raise HTTPException(
            status_code=503,
            detail="Password reset could not be completed. Please request it again."
        )
    except PasswordResetError as e:
        raise HTTPException(
            status_code=500,
            detail=client_message(e)
        )
    except Exception as e:
        logger.error(
            f"Unexpected error during password reset confirmation with token "
            f"{mask_token_for_logging(confirm_data.token)}: {e}"
        )
        raise HTTPException(
            status_code=500,
            detail="Internal server error occurred during password reset confirmation"
        )
    else:
        return PasswordResetConfirmResponseSchema(
            message="Password reset completed successfully"
        )


async def change_password_controller(
        change_data: PasswordChangeSchema,
        jwt_payload: JWTPayloadDTO,
        account_service: AccountServiceInterface,
) -> PasswordChangeResponseSchema:
    """
    Controller for password change by authenticated user

    Args:
        change_data: Password change data from request
        jwt_payload: JWT payload from verified access token
        account_service: Account service for business logic

    Returns:
        PasswordChangeResponseSchema with success message

    Raises:
        HTTPException: 400 for password errors, 404 for user not found, 500 for server errors
    """
    change_dto = PasswordChangeDTO(
        old_password=change_data.old_password,
        new_password=change_data.new_password
    )

    try:
        await account_service.change_password(jwt_payload.email, change_dto)
    except UserNotFoundError as e:
        raise HTTPException(
            status_code=404,
            detail=client_message(e)
        )
    except IncorrectCurrentPasswordError as e:
        raise HTTPException(
            status_code=400,
            detail=client_message(e)
        )
    except SamePasswordError as e:
        raise HTTPException(
            status_code=400,
            detail=client_message(e)
        )
    except UserPasswordError as e:
        raise HTTPException(
            status_code=400,
            detail=client_message(e)
        )
    except PasswordChangeError as e:
        raise HTTPException(
            status_code=500,
            detail=client_message(e)
        )
    except Exception as e:
        logger.error(f"Unexpected error during password change for user {jwt_payload.email}: {e}")
        raise HTTPException(
            status_code=500,
            detail="Internal server error occurred during password change"
        )
    else:
        return PasswordChangeResponseSchema(
            message="Password changed successfully"
        )


async def refresh_access_token_controller(
        token_data: RefreshTokenRequest,
        account_service: AccountServiceInterface,
) -> RefreshTokenResponse:
    """
    Controller for refreshing access token using refresh token

    Args:
        token_data: Refresh token data from request
        account_service: Account service for business logic

    Returns:
        RefreshTokenResponse with the new token pair

    Raises:
        HTTPException: 401 for invalid/expired tokens, 404 if user not found, 500 for server errors
    """
    try:
        tokens = await account_service.refresh_access_token(token_data.refresh_token)
    except InvalidRefreshTokenError as e:
        raise HTTPException(
            status_code=401,
            detail=client_message(e)
        )
    except UserNotFoundError as e:
        raise HTTPException(
            status_code=404,
            detail=client_message(e)
        )
    except TokenValidationError as e:
        raise HTTPException(
            status_code=401,
            detail=client_message(e)
        )
    except TokenGenerationError as e:
        raise HTTPException(
            status_code=500,
            detail=client_message(e)
        )
    except Exception as e:
        logger.error(f"Unexpected error during token refresh: {e}")
        raise HTTPException(
            status_code=500,
            detail="Internal server error occurred during token refresh"
        )
    else:
        return RefreshTokenResponse(
            access_token=tokens.access_token,
            refresh_token=tokens.refresh_token,
            token_type=tokens.token_type,
            expires_in=config.JWT_ACCESS_TOKEN_EXPIRE_MINUTES * 60
        )
