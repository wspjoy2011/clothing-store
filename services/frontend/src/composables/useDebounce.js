import { ref, watch } from 'vue';

/**
 * Composable for debouncing reactive values
 * @param {import('vue').Ref} value - Reactive value to debounce
 * @param {number} delay - Delay in milliseconds (default: 300)
 * @returns {Object} - Object with debouncedValue ref and cancel function
 */
export function useDebounce(value, delay = 300) {
  const debouncedValue = ref(value.value);
  let timeoutId = null;

  const cancel = () => {
    if (timeoutId) {
      clearTimeout(timeoutId);
      timeoutId = null;
    }
  };

  watch(value, (newValue) => {
    cancel();

    timeoutId = setTimeout(() => {
      debouncedValue.value = newValue;
      timeoutId = null;
    }, delay);
  });

  return {
    debouncedValue,
    cancel
  };
}
