import {computed} from 'vue';
import {useTheme} from 'vuetify';

export function useThemeState() {
    const theme = useTheme();

    const isDarkTheme = computed(() => theme.global.current.value.dark);

    return {
        isDarkTheme
    };
}
