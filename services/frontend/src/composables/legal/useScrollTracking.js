import { ref } from 'vue'

export function useScrollTracking() {
    const hasScrolledToBottom = ref(false)
    const scrollContainer = ref(null)

    const checkScrollPosition = () => {
        if (!scrollContainer.value) {
            return
        }

        const element = scrollContainer.value
        let domElement = element
        if (element.$el) {
            domElement = element.$el
        }

        const scrollTop = domElement.scrollTop
        const scrollHeight = domElement.scrollHeight
        const clientHeight = domElement.clientHeight

        if (scrollTop === undefined || scrollHeight === undefined || clientHeight === undefined) {
            return
        }

        const scrollThreshold = 0.95
        const scrollPercentage = (scrollTop + clientHeight) / scrollHeight

        if (scrollPercentage >= scrollThreshold && !hasScrolledToBottom.value) {
            hasScrolledToBottom.value = true
        }
    }

    const startTracking = () => {
        hasScrolledToBottom.value = false
    }

    const setScrollContainer = (element) => {
        scrollContainer.value = element
    }

    return {
        hasScrolledToBottom,
        scrollContainer,
        checkScrollPosition,
        startTracking,
        setScrollContainer
    }
}
