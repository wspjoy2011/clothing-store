import { useRouter } from 'vue-router'

export function useNavigation() {
  const router = useRouter()

  const goToLogin = () => {
    router.push({ name: 'home' })
  }

  const handleGoogleRegister = () => {
    console.log('Google registration')
  }

  const handleFacebookRegister = () => {
    console.log('Facebook registration')
  }

  const openTerms = () => {
    console.log('Open terms of service')
  }

  const openPrivacy = () => {
    console.log('Open privacy policy')
  }

  return {
    goToLogin,
    handleGoogleRegister,
    handleFacebookRegister,
    openTerms,
    openPrivacy
  }
}
