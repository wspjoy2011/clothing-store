"""Controllers for accounts module"""

from dataclasses import asdict

from fastapi import HTTPException

from apps.accounts.dto.users import CreateUserDTO
from apps.accounts.interfaces.services import AccountServiceInterface
from apps.accounts.schemas.user import CreateUserSchema, CreateUserResponseSchema, UserResponseSchema
from apps.accounts.services.exceptions import EmailAlreadyExistsError, UserCreationError, UserPasswordError


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
