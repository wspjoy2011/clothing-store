"""Controllers for accounts module"""

from dataclasses import asdict

from fastapi import HTTPException

from apps.accounts.dto.users import CreateUserDTO
from apps.accounts.dto.activation import ActivateAccountDTO
from apps.accounts.interfaces.services import AccountServiceInterface
from apps.accounts.schemas.user import CreateUserSchema, CreateUserResponseSchema, UserResponseSchema
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
    ExpiredActivationTokenError
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
