import { useRouter } from 'vue-router'
import { useLegalStore } from '@/stores/legal'

export function useNavigation() {
  const router = useRouter()
  const legalStore = useLegalStore()

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

  return {
    goToLogin,
    handleGoogleRegister,
    handleFacebookRegister,
    openTerms,
    openPrivacy,
    handleTermsAccept,
    handlePrivacyAcknowledge
  }
}
