import {useAccountStore} from '@/stores/accounts'

import {HFaceBookLogin} from '@healerlab/vue3-facebook-login'

export function useFacebookAuth() {
    const accountStore = useAccountStore()

    const handleFacebookSuccess = async (response) => {
        try {
            if (!response.authResponse?.accessToken) {
                throw new Error('No access_token received from Facebook')
            }

            const authResult = await accountStore.socialAuthenticate('facebook', response.authResponse.accessToken)

            return authResult

        } catch (error) {
            console.error('Facebook auth error:', error)

            let errorMessage = 'Unknown error occurred'

            if (error.status) {
                switch (error.status) {
                    case 400:
                        errorMessage = 'Invalid request data'
                        break
                    case 401:
                        errorMessage = 'Invalid access token'
                        break
                    case 422:
                        errorMessage = 'Validation error'
                        break
                    case 503:
                        errorMessage = 'Facebook service temporarily unavailable'
                        break
                    default:
                        errorMessage = error.message || 'Server error'
                }
            } else if (error.message) {
                errorMessage = error.message
            }

            return {
                success: false,
                error: {message: errorMessage},
                message: errorMessage
            }
        }
    }

    const handleFacebookError = (error) => {
        console.error('Facebook login error:', error)

        let errorMessage = 'Facebook login failed'

        if (error.error === 'popup_closed_by_user') {
            errorMessage = 'Facebook login was cancelled by user'
        } else if (error.error === 'access_denied') {
            errorMessage = 'Access denied by Facebook'
        } else if (error.message) {
            errorMessage = error.message
        }

        return {
            success: false,
            error: {message: errorMessage},
            message: errorMessage
        }
    }

    return {
        handleFacebookSuccess,
        handleFacebookError,
        HFaceBookLogin,
    }
}
