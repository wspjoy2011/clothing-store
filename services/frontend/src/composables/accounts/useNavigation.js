import {useRouter} from 'vue-router'
import {googleTokenLogin} from 'vue3-google-login'

import {useLegalStore} from '@/stores/legal'
import {useAccountStore} from '@/stores/accounts'

export function useNavigation() {
    const router = useRouter()
    const legalStore = useLegalStore()
    const accountStore = useAccountStore()

    const goToLogin = () => {
        router.push({name: 'login'})
    }

    const goToRegister = () => {
        router.push({name: 'register'})
    }

    const goToActivation = (email = null) => {
        const query = email ? {email} : {}
        router.push({
            name: 'activate',
            query
        })
    }

    const goToResendActivation = (email = null) => {
        const query = email ? {email} : {}
        router.push({
            name: 'resend-activation',
            query
        })
    }

    const goToLogout = () => {
        router.push({name: 'logout'})
    }

    const goToAccountSettings = () => {
        console.log('Navigate to account settings')
    }

    const goToWishlist = () => {
        console.log('Navigate to wishlist')
    }

    const goToProfile = () => {
        console.log('Navigate to profile')
    }

    const goToOrderHistory = () => {
        console.log('Navigate to order history')
    }

    const goToCart = () => {
        console.log('Navigate to cart')
    }

    const handleLogout = () => {
        goToLogout()
    }

    const handleGoogleAuth = async (isLogin = true) => {
        try {
            const response = await googleTokenLogin()

            if (!response.access_token) {
                throw new Error('No access_token received from Google')
            }

            const authResult = await accountStore.authenticateWithGoogle(response.access_token)

            return authResult

        } catch (error) {
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
                        errorMessage = 'Google service temporarily unavailable'
                        break
                    default:
                        errorMessage = error.message || 'Server error'
                }
            } else if (error.error === 'popup_closed_by_user') {
                errorMessage = 'Authentication was cancelled by user'
            } else if (error.error === 'access_denied') {
                errorMessage = 'Access denied by Google'
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

    const handleFacebookAuth = (isLogin = true) => {
        const action = isLogin ? 'login' : 'register'
        console.log(`Facebook ${action} clicked`)
        alert(`Facebook ${action} is not implemented yet`)
    }

    const openTerms = () => {
        legalStore.openTermsDialog()
    }

    const openPrivacy = () => {
        legalStore.openPrivacyDialog()
    }

    const handleTermsAccept = () => {
        console.log('Terms accepted and tracked')
    }

    const handlePrivacyAcknowledge = () => {
        console.log('Privacy policy acknowledged and tracked')
    }

    const goToHome = () => {
        router.push({name: 'home'})
    }

    const goToCatalog = () => {
        router.push({name: 'catalog'})
    }

    return {
        // Auth navigation
        goToLogin,
        goToRegister,
        goToActivation,
        goToResendActivation,
        goToLogout,

        // Authenticated user navigation
        goToAccountSettings,
        goToWishlist,
        goToProfile,
        goToOrderHistory,
        goToCart,
        handleLogout,

        // Social auth
        handleGoogleAuth,
        handleFacebookAuth,

        // Legal
        openTerms,
        openPrivacy,
        handleTermsAccept,
        handlePrivacyAcknowledge,

        // General navigation
        goToHome,
        goToCatalog,

    }
}
