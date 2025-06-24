"""
Examples for social authentication API documentation.
"""

SOCIAL_AUTH_REQUEST_GOOGLE = {
    "provider": "google",
    "access_token": "ya29.a0AfB_byDGHIJKLMNOPQRSTUVWXYZabcdefghijklmnopqrstuvwxyz1234567890"
}

SOCIAL_AUTH_REQUEST_FACEBOOK = {
    "provider": "facebook",
    "access_token": "EAABwzLixnjYBOZD8ZCnQVQvfD7h2vKCsj4yfmE5sNHTdYwl9ywQUJmP4C8pKuKB"
}

SOCIAL_AUTH_REQUEST_GITHUB = {
    "provider": "github",
    "access_token": "gho_16C7e42F292c6912E7710c838347Ae178B4a"
}

SOCIAL_AUTH_REQUEST_DISCORD = {
    "provider": "discord",
    "access_token": "mfa.VkO_2G4Qv3T--NO--lWetW_tjND--TOKEN--QFTm6YGtzq9PH--4U"
}

SOCIAL_AUTH_SUCCESS_EXISTING_USER = {
    "success": True,
    "tokens": {
        "access_token": "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJzdWIiOiIxMjM0NTY3ODkwIiwibmFtZSI6IkpvaG4gRG9lIiwiaWF0IjoxNTE2MjM5MDIyfQ.SflKxwRJSMeKKF2QT4fwpMeJf36POk6yJV_adQssw5c",
        "refresh_token": "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJzdWIiOiIxMjM0NTY3ODkwIiwibmFtZSI6IkpvaG4gRG9lIiwiaWF0IjoxNTE2MjM5MDIyfQ.cThIIoDvwdueQB468K5xDc5633seEFoqwxjF_xSJyQQ",
        "token_type": "bearer",
        "expires_in": 3600
    },
    "user_profile": {
        "provider": "google",
        "provider_id": "123456789012345678901",
        "email": "john.doe@example.com",
        "name": "John Doe",
        "first_name": "John",
        "last_name": "Doe",
        "avatar_url": "https://lh3.googleusercontent.com/a/default-user=s96-c",
        "locale": "en",
        "verified_email": True
    },
    "is_new_user": False,
    "message": "Google authentication successful",
    "provider": "google"
}

SOCIAL_AUTH_SUCCESS_NEW_USER = {
    "success": True,
    "tokens": {
        "access_token": "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJzdWIiOiI5ODc2NTQzMjEwIiwibmFtZSI6IkphbmUgU21pdGgiLCJpYXQiOjE1MTYyMzkwMjJ9.R7mHd3w2kC8fEwg-dWG_W2cL6kqr1vTz-A3PNhKjOxk",
        "refresh_token": "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJzdWIiOiI5ODc2NTQzMjEwIiwibmFtZSI6IkphbmUgU21pdGgiLCJpYXQiOjE1MTYyMzkwMjJ9.XgKJ-qB4dR6tE1jG-WnE2-vP9qM1kF7x-Y2BNhKjOxk",
        "token_type": "bearer",
        "expires_in": 3600
    },
    "user_profile": {
        "provider": "facebook",
        "provider_id": "10224567890123456",
        "email": "jane.smith@example.com",
        "name": "Jane Smith",
        "first_name": "Jane",
        "last_name": "Smith",
        "avatar_url": "https://graph.facebook.com/10224567890123456/picture?type=large",
        "locale": "en_US",
        "verified_email": True
    },
    "is_new_user": True,
    "message": "Facebook authentication successful",
    "provider": "facebook"
}

SUPPORTED_PROVIDERS_RESPONSE = {
    "providers": ["google", "facebook", "github", "discord"],
    "total_count": 4
}

GOOGLE_USER_PROFILE = {
    "provider": "google",
    "provider_id": "123456789012345678901",
    "email": "user@gmail.com",
    "name": "Google User",
    "first_name": "Google",
    "last_name": "User",
    "avatar_url": "https://lh3.googleusercontent.com/a/default-user=s96-c",
    "locale": "en",
    "verified_email": True
}

FACEBOOK_USER_PROFILE = {
    "provider": "facebook",
    "provider_id": "10224567890123456",
    "email": "user@facebook.com",
    "name": "Facebook User",
    "first_name": "Facebook",
    "last_name": "User",
    "avatar_url": "https://graph.facebook.com/10224567890123456/picture?type=large",
    "locale": "en_US",
    "verified_email": True
}

GITHUB_USER_PROFILE = {
    "provider": "github",
    "provider_id": "12345678",
    "email": "user@github.example.com",
    "name": "GitHub User",
    "first_name": "GitHub",
    "last_name": "User",
    "avatar_url": "https://avatars.githubusercontent.com/u/12345678?v=4",
    "locale": "en",
    "verified_email": True
}

DISCORD_USER_PROFILE = {
    "provider": "discord",
    "provider_id": "123456789012345678",
    "email": "user@discord.example.com",
    "name": "DiscordUser#1234",
    "first_name": "Discord",
    "last_name": "User",
    "avatar_url": "https://cdn.discordapp.com/avatars/123456789012345678/a_1234567890abcdef.png",
    "locale": "en-US",
    "verified_email": True
}

PROVIDER_EMPTY_ERROR = {
    "field": "provider",
    "message": "Provider name cannot be empty"
}

PROVIDER_UNSUPPORTED_ERROR = {
    "field": "provider",
    "message": "Unsupported provider 'twitter'. Supported providers: google, facebook, github, discord"
}

ACCESS_TOKEN_EMPTY_ERROR = {
    "field": "access_token",
    "message": "Access token cannot be empty"
}

ACCESS_TOKEN_TOO_SHORT_ERROR = {
    "field": "access_token",
    "message": "Access token is too short"
}

ACCESS_TOKEN_INVALID_CHARS_ERROR = {
    "field": "access_token",
    "message": "Access token contains invalid characters"
}

EMAIL_INVALID_FORMAT_ERROR = {
    "field": "email",
    "message": "Invalid email format: The email address is not valid"
}

AVATAR_URL_INVALID_ERROR = {
    "field": "avatar_url",
    "message": "Avatar URL must start with http:// or https://"
}

SOCIAL_TOKEN_ERROR = {
    "success": False,
    "error_type": "SocialTokenError",
    "error_message": "Token verification failed: Invalid token signature",
    "provider": "google",
    "details": {
        "status_code": 401,
        "timestamp": "2024-06-24T12:00:00Z"
    }
}

SOCIAL_PROVIDER_ERROR = {
    "success": False,
    "error_type": "SocialProviderError",
    "error_message": "OAuth error: Provider service temporarily unavailable",
    "provider": "facebook",
    "details": {
        "status_code": 503,
        "timestamp": "2024-06-24T12:00:00Z"
    }
}

SOCIAL_USER_INFO_ERROR = {
    "success": False,
    "error_type": "SocialUserInfoError",
    "error_message": "User info extraction failed: Required field 'email' not found",
    "provider": "github",
    "details": {
        "missing_fields": ["email"],
        "timestamp": "2024-06-24T12:00:00Z"
    }
}

SOCIAL_USER_VALIDATION_ERROR = {
    "success": False,
    "error_type": "SocialUserValidationError",
    "error_message": "Missing required fields: email, provider_id",
    "provider": "discord",
    "details": {
        "timestamp": "2024-06-24T12:00:00Z"
    }
}

SOCIAL_CONFIGURATION_ERROR = {
    "success": False,
    "error_type": "SocialConfigurationError",
    "error_message": "Provider configuration invalid: Missing client_id",
    "provider": "google",
    "details": {
        "timestamp": "2024-06-24T12:00:00Z"
    }
}

SOCIAL_USER_LOOKUP_ERROR = {
    "success": False,
    "error_type": "SocialUserLookupError",
    "error_message": "Database error during user lookup: Connection timeout",
    "provider": "facebook",
    "details": {
        "timestamp": "2024-06-24T12:00:00Z"
    }
}

SOCIAL_TOKEN_GENERATION_ERROR = {
    "success": False,
    "error_type": "SocialTokenGenerationError",
    "error_message": "JWT token generation failed: Signing key not found",
    "provider": "github",
    "details": {
        "timestamp": "2024-06-24T12:00:00Z"
    }
}

GOOGLE_EMAIL_NOT_VERIFIED_ERROR = {
    "success": False,
    "error_type": "SocialUserValidationError",
    "error_message": "Google email must be verified",
    "provider": "google",
    "details": {
        "timestamp": "2024-06-24T12:00:00Z"
    }
}


JWT_ACCESS_TOKEN_EXAMPLE = "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJzdWIiOiIxMjM0NTY3ODkwIiwibmFtZSI6IkpvaG4gRG9lIiwiaWF0IjoxNTE2MjM5MDIyfQ.SflKxwRJSMeKKF2QT4fwpMeJf36POk6yJV_adQssw5c"

JWT_REFRESH_TOKEN_EXAMPLE = "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJzdWIiOiIxMjM0NTY3ODkwIiwibmFtZSI6IkpvaG4gRG9lIiwiaWF0IjoxNTE2MjM5MDIyfQ.cThIIoDvwdueQB468K5xDc5633seEFoqwxjF_xSJyQQ"

GOOGLE_ACCESS_TOKEN_EXAMPLES = [
    "ya29.a0AfB_byDGHIJKLMNOPQRSTUVWXYZabcdefghijklmnopqrstuvwxyz1234567890",
    "ya29.a0AfB_byCDE123FGH456IJK789LMN012OPQ345RST678UVW901XYZ234abc567def",
    "ya29.a0AfH_UyAABBCCDDEEFFGGHHIIJJKKLLMMNNOOPPQQRRSSTTUUVVWWXXYYZZ1234"
]

FACEBOOK_ACCESS_TOKEN_EXAMPLES = [
    "EAABwzLixnjYBOZD8ZCnQVQvfD7h2vKCsj4yfmE5sNHTdYwl9ywQUJmP4C8pKuKB",
    "EAABwzLixnjYBAJKnmDp4SFG3kRt8TyuVnm9xQPpMN2HgfwEv4RtKj7sL8uI9pQw",
    "EAABwzLixnjYBAPqwe123RTYuio456ASdfgh789ZXcvbn012MNbvcx345QWerty678"
]

GITHUB_ACCESS_TOKEN_EXAMPLES = [
    "gho_16C7e42F292c6912E7710c838347Ae178B4a",
    "gho_35D8f53G403d7a23F8821d949458Bf289C5b",
    "gho_46E9g64H514e8b34G9932ea5a569Cg39aD6c"
]

DISCORD_ACCESS_TOKEN_EXAMPLES = [
    "mfa.VkO_2G4Qv3T--NO--lWetW_tjND--TOKEN--QFTm6YGtzq9PH--4U",
    "mfa.WlP_3H5Rw4U--XO--mXfuX_ukOE--TOKEN--RGUn7ZHuar0QI--5V",
    "mfa.XmQ_4I6Sx5V--YP--nYgvY_vlPF--TOKEN--SHVo8AIvbs1RJ--6W"
]

SOCIAL_AUTH_WORKFLOW_GOOGLE = {
    "step_1_request": {
        "provider": "google",
        "access_token": "ya29.a0AfB_byDGHIJKLMNOPQRSTUVWXYZabcdefghijklmnopqrstuvwxyz1234567890"
    },
    "step_2_success_response": {
        "success": True,
        "tokens": {
            "access_token": "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9...",
            "refresh_token": "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9...",
            "token_type": "bearer",
            "expires_in": 3600
        },
        "user_profile": {
            "provider": "google",
            "provider_id": "123456789012345678901",
            "email": "user@gmail.com",
            "name": "John Doe",
            "first_name": "John",
            "last_name": "Doe",
            "avatar_url": "https://lh3.googleusercontent.com/a/default-user=s96-c",
            "locale": "en",
            "verified_email": True
        },
        "is_new_user": False,
        "message": "Google authentication successful",
        "provider": "google"
    }
}
