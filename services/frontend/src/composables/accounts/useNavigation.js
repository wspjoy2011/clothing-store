import {useRouter} from 'vue-router'
import {googleTokenLogin} from 'vue3-google-login'

import {useLegalStore} from '@/stores/legal'
import socialAuthService from '@/services/socialAuthService.js'

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

    const handleGoogleAuth = async (isLogin = true) => {
        const action = isLogin ? 'login' : 'register'
        console.log(`Google ${action} started...`)

        try {
            console.log('Opening Google authentication popup...')

            const response = await googleTokenLogin()
            console.log('🔍 Full Google response:', response)

            if (!response.access_token) {
                throw new Error('No access_token received from Google')
            }

            console.log('🔑 Access Token received:', response.access_token.substring(0, 20) + '...')

            console.log('🚀 Sending access_token to backend...')
            
            const authResult = await socialAuthService.authenticateWithGoogle(response.access_token)
            
            console.log('✅ Backend authentication successful!', authResult)

            const message = `🎉 Google ${action} successful!\n\n` +
                `👤 Name: ${authResult.user_profile?.name || 'N/A'}\n` +
                `📧 Email: ${authResult.user_profile?.email || 'N/A'}\n` +
                `🆕 New User: ${authResult.is_new_user ? 'Yes' : 'No'}\n` +
                `🎯 Provider: ${authResult.provider}\n` +
                `🔑 Access Token: ${authResult.tokens?.access_token ? 'Received' : 'Not received'}\n` +
                `🔄 Refresh Token: ${authResult.tokens?.refresh_token ? 'Received' : 'Not received'}\n\n` +
                `${authResult.message || 'Authentication completed successfully!'}`

            alert(message)

            // accountStore.setTokens(authResult.tokens)
            // if (authResult.is_new_user) {
            //     goToWelcome()
            // } else {
            //     goToHome()
            // }

            setTimeout(() => {
                goToHome()
            }, 3000)

        } catch (error) {
            console.error(`❌ Google ${action} failed:`, error)

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

            alert(`❌ Google ${action} failed!\n\nError: ${errorMessage}`)
        }
    }

    const handleFacebookAuth = (isLogin = true) => {
        const action = isLogin ? 'login' : 'register'
        console.log(`Facebook ${action} clicked`)
        alert(`Facebook ${action} is not implemented yet`)
    }

    const testSocialAuthService = async () => {
        console.log('🧪 Testing social auth service...')
        
        try {
            const testResult = await socialAuthService.testConnection()
            
            const message = testResult.success ? 
                `✅ Social Auth Service Test Successful!\n\n` +
                `📡 Service Status: Available\n` +
                `🔧 Supported Providers: ${testResult.providers?.join(', ') || 'None'}\n` +
                `📊 Total Providers: ${testResult.total_providers || 0}\n\n` +
                `Ready for authentication!`
                :
                `❌ Social Auth Service Test Failed!\n\n` +
                `📡 Service Status: Unavailable\n` +
                `💬 Error: ${testResult.error}\n\n` +
                `Please check backend connection.`

            alert(message)
            console.log('🧪 Test result:', testResult)
            
        } catch (error) {
            console.error('🧪 Test failed:', error)
            alert(`❌ Service test failed!\n\nError: ${error.message}`)
        }
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
        testSocialAuthService,

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
