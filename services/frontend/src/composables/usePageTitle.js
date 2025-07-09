import {onMounted, onUnmounted} from 'vue';

export function usePageTitle(title, restoreTitle = true) {
    let originalTitle = '';

    onMounted(() => {
        if (restoreTitle) {
            originalTitle = document.title;
        }
        document.title = title;
    });

    onUnmounted(() => {
        if (restoreTitle && originalTitle) {
            document.title = originalTitle;
        }
    });

    const setTitle = (newTitle) => {
        document.title = newTitle;
    };

    return {
        setTitle
    };
}
