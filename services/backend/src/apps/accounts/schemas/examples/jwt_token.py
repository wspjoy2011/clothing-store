REFRESH_TOKEN_REQUEST_EXAMPLES = {
    "valid_refresh_token": {
        "summary": "Valid refresh token request",
        "description": "Request to refresh access token using valid refresh token",
        "value": {
            "refresh_token": "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJ1c2VyX2lkIjoxLCJlbWFpbCI6InVzZXJAZXhhbXBsZS5jb20iLCJncm91cF9pZCI6MSwiZ3JvdXBfbmFtZSI6InVzZXIiLCJleHAiOjE3MzY5NjE2MDAsImlhdCI6MTczNjg3NTIwMCwidHlwZSI6InJlZnJlc2gifQ.xyz_refresh_token_signature"
        }
    },
    "expired_refresh_token": {
        "summary": "Expired refresh token request",
        "description": "Request with expired refresh token (will result in error)",
        "value": {
            "refresh_token": "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJ1c2VyX2lkIjoxLCJlbWFpbCI6InVzZXJAZXhhbXBsZS5jb20iLCJncm91cF9pZCI6MSwiZ3JvdXBfbmFtZSI6InVzZXIiLCJleHAiOjE3MzY3ODg4MDAsImlhdCI6MTczNjc4NTIwMCwidHlwZSI6InJlZnJlc2gifQ.xyz_expired_signature"
        }
    },
    "invalid_refresh_token": {
        "summary": "Invalid refresh token request",
        "description": "Request with malformed refresh token",
        "value": {
            "refresh_token": "invalid.token.format"
        }
    }
}

REFRESH_TOKEN_RESPONSE_EXAMPLES = {
    "success": {
        "summary": "Successful token refresh",
        "description": "New access token generated successfully",
        "value": {
            "access_token": "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJ1c2VyX2lkIjoxLCJlbWFpbCI6InVzZXJAZXhhbXBsZS5jb20iLCJncm91cF9pZCI6MSwiZ3JvdXBfbmFtZSI6InVzZXIiLCJleHAiOjE3MzY4NzUyMDAsImlhdCI6MTczNjg3MTYwMCwidHlwZSI6ImFjY2VzcyJ9.abc_new_access_token_signature",
            "token_type": "bearer",
            "expires_in": 3600
        }
    }
}

TOKEN_ERROR_EXAMPLES = {
    "invalid_refresh_token": {
        "summary": "Invalid refresh token",
        "description": "Refresh token is invalid, expired, or malformed",
        "value": {
            "detail": "Invalid refresh token: Token has expired",
            "error_code": "INVALID_REFRESH_TOKEN"
        }
    },
    "token_not_found": {
        "summary": "Token not found in database",
        "description": "Refresh token not found in database or has been revoked",
        "value": {
            "detail": "Refresh token not found or expired",
            "error_code": "TOKEN_NOT_FOUND"
        }
    },
    "user_not_found": {
        "summary": "User not found",
        "description": "User associated with refresh token no longer exists",
        "value": {
            "detail": "User with ID 1 not found",
            "error_code": "USER_NOT_FOUND"
        }
    },
    "token_generation_failed": {
        "summary": "Token generation failed",
        "description": "Failed to generate new access token",
        "value": {
            "detail": "Failed to generate new access token: Internal server error",
            "error_code": "TOKEN_GENERATION_ERROR"
        }
    },
    "validation_error": {
        "summary": "Request validation error",
        "description": "Invalid request data format",
        "value": {
            "detail": [
                {
                    "loc": ["body", "refresh_token"],
                    "msg": "field required",
                    "type": "value_error.missing"
                }
            ]
        }
    },
    "empty_token": {
        "summary": "Empty refresh token",
        "description": "Refresh token is empty or missing",
        "value": {
            "detail": "Token is empty or None",
            "error_code": "EMPTY_TOKEN"
        }
    },
    "invalid_token_signature": {
        "summary": "Invalid token signature",
        "description": "Token signature verification failed",
        "value": {
            "detail": "Invalid refresh token: Invalid token signature",
            "error_code": "INVALID_TOKEN_SIGNATURE"
        }
    },
    "wrong_token_type": {
        "summary": "Wrong token type",
        "description": "Token type is not 'refresh'",
        "value": {
            "detail": "Invalid refresh token: Token type must be 'refresh'",
            "error_code": "INVALID_TOKEN_TYPE"
        }
    }
}

TOKEN_INFO_EXAMPLES = {
    "access_token_info": {
        "summary": "Access token information",
        "description": "Decoded access token payload",
        "value": {
            "user_id": 1,
            "email": "user@example.com",
            "group_id": 1,
            "group_name": "user",
            "token_type": "access",
            "expires_at": 1736875200,
            "issued_at": 1736871600
        }
    },
    "refresh_token_info": {
        "summary": "Refresh token information",
        "description": "Decoded refresh token payload",
        "value": {
            "user_id": 1,
            "email": "user@example.com",
            "group_id": 1,
            "group_name": "user",
            "token_type": "refresh",
            "expires_at": 1736961600,
            "issued_at": 1736875200
        }
    }
}

JWT_TOKEN_EXAMPLES = {
    "requests": REFRESH_TOKEN_REQUEST_EXAMPLES,
    "responses": REFRESH_TOKEN_RESPONSE_EXAMPLES,
    "errors": TOKEN_ERROR_EXAMPLES,
    "token_info": TOKEN_INFO_EXAMPLES
}
