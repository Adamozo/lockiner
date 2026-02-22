import { useAuthStore } from '~/stores/auth'

export function useLanguage() {
  const { locale, setLocale } = useI18n()
  const authStore = useAuthStore()
  const languageCookie = useCookie<string>('scrooge_language', { default: () => 'en' })

  // Called on app init — if cookie missing but user logged in, apply language from DB
  const initLanguage = async () => {
    if (!languageCookie.value && authStore.user?.language) {
      await setLocale(authStore.user.language as 'en' | 'pl')
      languageCookie.value = authStore.user.language
    }
  }

  // Change language: set cookie + update DB if logged in
  const changeLanguage = async (lang: 'en' | 'pl') => {
    await setLocale(lang)
    languageCookie.value = lang
    if (authStore.isAuthenticated) {
      await authStore.updateProfile({ language: lang })
    }
  }

  return { locale, changeLanguage, initLanguage }
}
