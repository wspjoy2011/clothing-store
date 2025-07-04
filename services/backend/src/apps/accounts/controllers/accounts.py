"""Controllers for accounts module"""

from dataclasses import asdict

from fastapi import HTTPException

from apps.accounts.dto.users import CreateUserDTO, UserLoginDTO
from apps.accounts.dto.activation import ActivateAccountDTO
from apps.accounts.interfaces.services import AccountServiceInterface
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
    TokenValidationError
)


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
            detail=str(e)
        )
    except (UserCreationError, UserPasswordError) as e:
        raise HTTPException(
            status_code=400,
            detail=str(e)
        )
    except Exception as e:
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
            detail=str(e)
        )
    except UserAlreadyActivatedError as e:
        raise HTTPException(
            status_code=400,
            detail=str(e)
        )
    except InvalidActivationTokenError as e:
        raise HTTPException(
            status_code=400,
            detail=str(e)
        )
    except ExpiredActivationTokenError as e:
        raise HTTPException(
            status_code=410,
            detail=str(e)
        )
    except (UserCreationError, Exception) as e:
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
            detail=str(e)
        )
    except UserAlreadyActivatedError as e:
        raise HTTPException(
            status_code=400,
            detail=str(e)
        )
    except Exception as e:
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
    except UserNotFoundError as e:
        raise HTTPException(
            status_code=404,
            detail=str(e)
        )
    except UserInactiveError as e:
        raise HTTPException(
            status_code=403,
            detail=str(e)
        )
    except InvalidCredentialsError as e:
        raise HTTPException(
            status_code=401,
            detail=str(e)
        )
    except TokenGenerationError as e:
        raise HTTPException(
            status_code=500,
            detail=str(e)
        )
    except LoginError as e:
        raise HTTPException(
            status_code=500,
            detail=str(e)
        )
    except Exception as e:
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
            detail=str(e)
        )
    except UserNotFoundError as e:
        raise HTTPException(
            status_code=404,
            detail=str(e)
        )
    except TokenValidationError as e:
        raise HTTPException(
            status_code=401,
            detail=str(e)
        )
    except Exception as e:
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
