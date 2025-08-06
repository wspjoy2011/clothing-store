import { ref, computed } from 'vue'

export function useCardQuantity(product) {
  const quantity = ref(1)
  const imageLoading = ref(true)

  const availableQuantity = computed(() => {
    return product.inventory?.available_quantity || 0
  })

  function imageLoaded() {
    imageLoading.value = false
  }

  function increaseQuantity() {
    if (quantity.value < availableQuantity.value) {
      quantity.value++
    }
  }

  function decreaseQuantity() {
    if (quantity.value > 1) {
      quantity.value--
    }
  }

  return {
    quantity,
    availableQuantity,
    imageLoading,
    imageLoaded,
    increaseQuantity,
    decreaseQuantity
  }
}
