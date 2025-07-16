import {ref} from 'vue'

export function usePasswordChangeValidation() {
    const oldPassword = ref('')
    const newPassword = ref('')
    const confirmPassword = ref('')
    const showOldPassword = ref(false)
    const showNewPassword = ref(false)
    const showConfirmPassword = ref(false)

    const oldPasswordRules = [
        value => !!value || 'Current password is required',
        value => value.length >= 1 || 'Current password cannot be empty'
    ]

    const newPasswordRules = [
        value => !!value || 'New password is required',
        value => value.length >= 8 || 'Password must be at least 8 characters long',
        value => /(?=.*[a-z])/.test(value) || 'Password must contain at least one lowercase letter',
        value => /(?=.*[A-Z])/.test(value) || 'Password must contain at least one uppercase letter',
        value => /(?=.*\d)/.test(value) || 'Password must contain at least one number',
        value => /(?=.*[@$!%*?&])/.test(value) || 'Password must contain at least one special character (@$!%*?&)',
        value => value !== oldPassword.value || 'New password must be different from current password'
    ]

    const confirmPasswordRules = [
        value => !!value || 'Please confirm your new password',
        value => value === newPassword.value || 'Passwords do not match'
    ]

    const resetPasswordChangeValidation = () => {
        oldPassword.value = ''
        newPassword.value = ''
        confirmPassword.value = ''
        showOldPassword.value = false
        showNewPassword.value = false
        showConfirmPassword.value = false
    }

    return {
        oldPassword,
        newPassword,
        confirmPassword,
        showOldPassword,
        showNewPassword,
        showConfirmPassword,
        oldPasswordRules,
        newPasswordRules,
        confirmPasswordRules,
        resetPasswordChangeValidation
    }
}
