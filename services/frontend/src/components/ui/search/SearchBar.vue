<template>
  <div class="search-wrapper">
    <v-btn
      icon
      @click="toggleSearch"
      class="search-icon-btn"
    >
      <v-icon>mdi-magnify</v-icon>
    </v-btn>

    <v-dialog
      v-model="isExpanded"
      content-class="search-dialog"
      fullscreen
      transition="dialog-top-transition"
      scrim="false"
    >
      <v-card class="search-overlay" flat>
        <v-toolbar flat class="search-toolbar">
          <v-container>
            <div class="d-flex align-center">
              <v-text-field
                v-model="searchQuery"
                placeholder="Search products..."
                variant="solo"
                density="compact"
                hide-details
                :bg-color="isDarkTheme ? 'grey-darken-3' : 'grey-lighten-4'"
                class="search-input flex-grow-1"
                @keyup.enter="handleSearch"
                ref="searchInput"
                autofocus
              >
                <template v-slot:prepend>
                  <v-icon>mdi-magnify</v-icon>
                </template>
                <template v-slot:append>
                  <v-progress-circular
                    v-if="isLoading"
                    indeterminate
                    size="20"
                    width="2"
                    color="primary"
                    class="mr-2"
                  ></v-progress-circular>
                  <v-btn
                    v-else-if="searchQuery"
                    icon="mdi-close"
                    size="small"
                    variant="text"
                    @click="clearSearch"
                  ></v-btn>
                </template>
              </v-text-field>
              <v-btn
                icon
                class="ml-2"
                @click="isExpanded = false"
              >
                <v-icon>mdi-close</v-icon>
              </v-btn>
            </div>
          </v-container>
        </v-toolbar>

        <div class="search-backdrop" @click="isExpanded = false"></div>
      </v-card>
    </v-dialog>
  </div>
</template>

<script setup>
import { ref, nextTick, computed, watch, onMounted } from 'vue';
import { useTheme } from 'vuetify';
import { useCatalogStore } from '@/stores/catalog';
import { useRouter, useRoute } from 'vue-router';

const searchQuery = ref('');
const isExpanded = ref(false);
const isLoading = ref(false);
const searchInput = ref(null);
const catalogStore = useCatalogStore();
const theme = useTheme();
const router = useRouter();
const route = useRoute();

const isDarkTheme = computed(() => {
  return theme.global.current.value.dark;
});

watch(() => catalogStore.searchQuery, (newVal) => {
  if (newVal !== searchQuery.value) {
    searchQuery.value = newVal;
  }
}, { immediate: true });

onMounted(() => {
  if (route.query.q) {
    searchQuery.value = route.query.q;
  }
});

const toggleSearch = () => {
  isExpanded.value = !isExpanded.value;

  if (isExpanded.value) {
    nextTick(() => {
      searchInput.value?.focus();
    });
  } else if (!searchQuery.value.trim()) {
    clearSearch();
  }
};

const clearSearch = () => {
  searchQuery.value = '';

  if (route.name === 'catalog') {
    isLoading.value = true;

    const query = { ...route.query };
    delete query.q;
    delete query.page;

    catalogStore.clearSearch();

    router.push({
      name: 'catalog',
      query: query
    }).then(() => {
      catalogStore.fetchProducts(1);

      setTimeout(() => {
        isLoading.value = false;
      }, 300);
    });
  } else {
    catalogStore.clearSearch();
  }

  searchInput.value?.focus();
};

const handleSearch = () => {
  if (!searchQuery.value.trim() && !catalogStore.searchQuery) {
    isExpanded.value = false;
    return;
  }

  isLoading.value = true;
  const trimmedQuery = searchQuery.value.trim();

  const query = { ...route.query };

  if (trimmedQuery) {
    query.q = trimmedQuery;
    delete query.page;
  } else {
    delete query.q;
  }

  catalogStore.setSearchQuery(trimmedQuery);

  if (route.name === 'catalog') {
    catalogStore.fetchFilters().then(() => {
      router.push({
        name: 'catalog',
        query: query
      }).then(() => {
        catalogStore.fetchProducts(1);

        setTimeout(() => {
          isLoading.value = false;
          isExpanded.value = false;
        }, 500);
      });
    });
  } else {
    router.push({
      name: 'catalog',
      query: query
    }).then(() => {
      setTimeout(() => {
        isLoading.value = false;
        isExpanded.value = false;
      }, 500);
    });
  }
};
</script>

<style scoped>
.search-wrapper {
  position: relative;
  display: inline-block;
}

.search-dialog {
  box-shadow: none;
  background: transparent;
}

.search-overlay {
  box-shadow: none;
  background: transparent;
}

.search-toolbar {
  position: fixed;
  top: 0;
  left: 0;
  right: 0;
  z-index: 1000;
}

.search-backdrop {
  position: absolute;
  top: 0;
  left: 0;
  right: 0;
  bottom: 0;
  z-index: -1;
  cursor: pointer;
}

:deep(.v-theme--light) .search-toolbar {
  background: rgba(255, 255, 255, 0.98);
  border-bottom: 1px solid rgba(0, 0, 0, 0.08);
  backdrop-filter: blur(10px);
}

:deep(.v-theme--dark) .search-toolbar {
  background: rgba(30, 30, 30, 0.98);
  border-bottom: 1px solid rgba(255, 255, 255, 0.08);
  backdrop-filter: blur(10px);
}

:deep(.v-theme--light) .search-backdrop {
  background: rgba(255, 255, 255, 0.6);
  backdrop-filter: blur(5px);
}

:deep(.v-theme--dark) .search-backdrop {
  background: rgba(30, 30, 30, 0.6);
  backdrop-filter: blur(5px);
}

.search-input {
  border-radius: 4px;
}

:deep(.dialog-top-transition-enter-active),
:deep(.dialog-top-transition-leave-active) {
  transition: all 0.2s ease-in-out;
}

:deep(.dialog-top-transition-enter-from),
:deep(.dialog-top-transition-leave-to) {
  transform: translateY(-30px);
  opacity: 0;
}
</style>
