import {useRouter} from 'vue-router'

import {useLegalStore} from '@/stores/legal'

export function useNavigation() {
    const router = useRouter()
    const legalStore = useLegalStore()

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

    const handleGoogleAuth = (isLogin = true) => {
        const action = isLogin ? 'login' : 'register'
        console.log(`Google ${action} clicked`)
    }

    const handleFacebookAuth = (isLogin = true) => {
        const action = isLogin ? 'login' : 'register'
        console.log(`Facebook ${action} clicked`)
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

        // Backward compatibility
        handleGoogleRegister: () => handleGoogleAuth(false),
        handleFacebookRegister: () => handleFacebookAuth(false)
    }
}
