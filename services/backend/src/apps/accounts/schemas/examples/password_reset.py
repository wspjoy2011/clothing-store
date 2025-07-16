"""Examples for password reset schemas for API documentation"""

PASSWORD_RESET_REQUEST_EXAMPLE = {
    "email": "john.doe@example.com"
}

PASSWORD_RESET_CONFIRM_EXAMPLE = {
    "token": "abc123def456ghi789jkl012mno345pqr678stu901vwx234yz567",
    "new_password": "NewSecurePass123!"
}

PASSWORD_RESET_REQUEST_SUCCESS_RESPONSE = {
    "message": "Password reset request processed successfully",
    "email": "john.doe@example.com"
}

PASSWORD_RESET_CONFIRM_SUCCESS_RESPONSE = {
    "message": "Password reset completed successfully"
}

PASSWORD_RESET_REQUEST_VALIDATION_ERROR = {
    "field": "email",
    "message": "value is not a valid email address",
}

PASSWORD_RESET_CONFIRM_VALIDATION_ERROR = {
    "field": "token",
    "message": "Token cannot be empty",
}

PASSWORD_RESET_CONFIRM_WEAK_PASSWORD_ERROR = {
    "field": "new_password",
    "message": "Password must be at least 8 characters long",
}

PASSWORD_RESET_EMAIL_ERROR = {
    "detail": "Failed to send password reset email"
}

PASSWORD_RESET_INVALID_TOKEN_ERROR = {
    "detail": "Invalid or expired password reset token"
}

PASSWORD_RESET_EXPIRED_TOKEN_ERROR = {
    "detail": "Password reset token has expired"
}

PASSWORD_RESET_TOKEN_NOT_FOUND_ERROR = {
    "detail": "Password reset token not found"
}

PASSWORD_RESET_SERVER_ERROR = {
    "detail": "Internal server error occurred during password reset"
}

PASSWORD_CHANGE_EXAMPLE = {
    "old_password": "OldSecurePass123!",
    "new_password": "NewSecurePass456!"
}

PASSWORD_CHANGE_SUCCESS_RESPONSE = {
    "message": "Password changed successfully"
}

PASSWORD_CHANGE_SAME_PASSWORD_ERROR = {
    "field": "new_password",
    "message": "New password must be different from current password"
}
