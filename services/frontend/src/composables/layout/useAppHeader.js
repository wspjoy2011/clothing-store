import { ref, computed, watch, onMounted, nextTick } from 'vue'
import { useTheme } from 'vuetify'
import { useRouter, useRoute } from 'vue-router'
import { useCatalogStore } from '@/stores/catalog'
import { useCategoryStore } from '@/stores/categoryStore'
import { useAccountStore } from '@/stores/accounts'
import { useUserPreferencesStore } from '@/stores/userPreferences'
import { useNavigation } from '@/composables/accounts/useNavigation'
import { useCategoryMeta } from '@/composables/catalog/useCategoryMeta'

export function useAppHeader() {
  const activeTab = ref('home')
  const theme = useTheme()
  const router = useRouter()
  const route = useRoute()
  const catalogStore = useCatalogStore()
  const categoryStore = useCategoryStore()
  const accountStore = useAccountStore()
  const preferencesStore = useUserPreferencesStore()
  const showMobileSearch = ref(false)
  const mobileSearchQuery = ref('')
  const isSearchLoading = ref(false)
  const categoryPathVisible = ref(false)

  const navigation = useNavigation()

  const {
    masterCategoryId,
    subCategoryId,
    articleTypeId
  } = useCategoryMeta(route)

  const isAuthenticated = computed(() => accountStore.isAuthenticated)
  const currentUser = computed(() => accountStore.currentUser)
  const userEmail = computed(() => accountStore.userEmail)

  const userDisplayName = computed(() => {
    if (currentUser.value) {
      return currentUser.value.name || currentUser.value.first_name || 'User'
    }
    return userEmail.value || 'User'
  })

  const isDarkTheme = computed(() => theme.global.current.value.dark)

  const isCategoryRoute = computed(() => {
    return route.name === 'master-category' ||
        route.name === 'sub-category' ||
        route.name === 'article-type'
  })

  const currentCategoryPath = computed(() => {
    if (!isCategoryRoute.value) return []

    return categoryStore.getCategoryPath(
        masterCategoryId.value,
        subCategoryId.value,
        articleTypeId.value
    )
  })

  const showCategoryPath = computed(() => {
    return isCategoryRoute.value && currentCategoryPath.value.length > 0
  })

  const shortCategoryPathText = computed(() => {
    if (!currentCategoryPath.value.length) return ''

    if (currentCategoryPath.value.length === 1) {
      return currentCategoryPath.value[0].name
    }

    const lastCategory = currentCategoryPath.value[currentCategoryPath.value.length - 1]
    return `${lastCategory.name} (${currentCategoryPath.value.length} levels)`
  })

  const toggleCategoryPathVisible = () => {
    categoryPathVisible.value = !categoryPathVisible.value
  }

  const toggleTheme = () => {
    const newTheme = preferencesStore.theme === 'dark' ? 'light' : 'dark'
    preferencesStore.setTheme(newTheme)
    theme.global.name.value = newTheme
  }

  const toggleMobileDrawer = () => {
    categoryStore.mobileDrawerOpen = !categoryStore.mobileDrawerOpen
  }

  const clearMobileSearch = () => {
    mobileSearchQuery.value = ''
  }

  const closeMobileSearch = () => {
    showMobileSearch.value = false

    if (!mobileSearchQuery.value.trim() && catalogStore.searchQuery) {
      catalogStore.setSearchQuery('')
      if (route.name === 'catalog') {
        const query = {...route.query}
        delete query.q
        delete query.page

        setTimeout(() => {
          router.push({
            name: 'catalog',
            query
          })
        }, 50)
      }
    }
  }

  const handleMobileSearch = async () => {
    if (!mobileSearchQuery.value.trim() && !catalogStore.searchQuery) {
      closeMobileSearch()
      return
    }

    isSearchLoading.value = true
    const trimmedQuery = mobileSearchQuery.value.trim()

    catalogStore.setSearchQuery(trimmedQuery)

    const query = {...route.query}

    if (trimmedQuery) {
      query.q = trimmedQuery
      delete query.page
    } else {
      delete query.q
    }

    showMobileSearch.value = false
    await nextTick()

    setTimeout(() => {
      router.push({
        name: 'catalog',
        query
      }).then(() => {
        isSearchLoading.value = false

        if (route.name === 'catalog') {
          catalogStore.fetchProducts(1)
        }
      }).catch((error) => {
        console.error('Navigation error:', error)
        isSearchLoading.value = false
      })
    }, 50)
  }

  const navigateToPathCategory = async (category, index) => {
    if (!category || !category.type) return

    categoryPathVisible.value = false
    await nextTick()

    let routeName
    const params = {}

    if (category.type === 'master') {
      routeName = 'master-category'
      params.masterCategory = category.slug
    } else if (category.type === 'sub') {
      routeName = 'sub-category'
      const masterCategory = currentCategoryPath.value.find(c => c.type === 'master')
      if (!masterCategory) return

      params.masterCategory = masterCategory.slug
      params.subCategory = category.slug
    } else if (category.type === 'article') {
      routeName = 'article-type'
      const masterCategory = currentCategoryPath.value.find(c => c.type === 'master')
      const subCategory = currentCategoryPath.value.find(c => c.type === 'sub')
      if (!masterCategory || !subCategory) return

      params.masterCategory = masterCategory.slug
      params.subCategory = subCategory.slug
      params.articleType = category.slug
    } else {
      return
    }

    setTimeout(() => {
      router.push({
        name: routeName,
        params
      })
    }, 50)
  }

  // Watchers
  watch(() => catalogStore.searchQuery, (newValue) => {
    if (newValue !== mobileSearchQuery.value) {
      mobileSearchQuery.value = newValue
    }
  })

  watch(() => route.name, (newName) => {
    if (newName) {
      activeTab.value = newName

      if (newName === 'master-category' || newName === 'sub-category' || newName === 'article-type') {
        activeTab.value = 'categories'
        categoryPathVisible.value = false
      } else {
        categoryPathVisible.value = false
      }
    }
  })

  watch(() => route.params, () => {
    if (isCategoryRoute.value) {
      categoryPathVisible.value = false
    }
  }, {deep: true})

  onMounted(async () => {
    activeTab.value = route.name || 'home'

    if (route.query.q) {
      mobileSearchQuery.value = route.query.q
    }

    if (!categoryStore.hasCategories && !categoryStore.loading) {
      await categoryStore.fetchCategoryMenu()
    }

    if (isCategoryRoute.value) {
      activeTab.value = 'categories'
      categoryPathVisible.value = false
    }
  })

  return {
    // State
    activeTab,
    showMobileSearch,
    mobileSearchQuery,
    isSearchLoading,
    categoryPathVisible,

    // Computed
    isAuthenticated,
    currentUser,
    userEmail,
    userDisplayName,
    isDarkTheme,
    currentCategoryPath,
    showCategoryPath,
    shortCategoryPathText,

    // Store state
    categoryStore,

    // Methods
    toggleCategoryPathVisible,
    toggleTheme,
    toggleMobileDrawer,
    clearMobileSearch,
    closeMobileSearch,
    handleMobileSearch,
    navigateToPathCategory,

    // Navigation methods
    ...navigation
  }
}
