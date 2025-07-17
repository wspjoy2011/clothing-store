<template>
  <div class="hidden-sm-and-down nav-center">
    <v-tabs
        :model-value="activeTab"
        @update:model-value="$emit('update:active-tab', $event)"
        centered
    >
      <v-tab :to="{ name: 'home' }" value="home">Home</v-tab>
      <v-tab :to="{ name: 'catalog' }" value="catalog">Catalog</v-tab>

      <v-tab value="categories">
        Categories
        <v-menu
            :model-value="categoryMenuOpen"
            @update:model-value="$emit('update:category-menu-open', $event)"
            location="bottom"
            :close-on-content-click="false"
            transition="slide-y-transition"
        >
          <template v-slot:activator="{ props }">
            <v-btn
                icon
                variant="text"
                v-bind="props"
                class="ml-1"
            >
              <v-icon>mdi-chevron-down</v-icon>
            </v-btn>
          </template>

          <div class="category-dropdown">
            <category-menu/>
          </div>
        </v-menu>
      </v-tab>
    </v-tabs>
  </div>
</template>

<script setup>
import CategoryMenu from '@/components/catalog/CategoryMenu.vue'

defineProps({
  activeTab: {
    type: String,
    default: 'home'
  },
  categoryMenuOpen: {
    type: Boolean,
    default: false
  }
})

defineEmits(['update:active-tab', 'update:category-menu-open'])
</script>

<style scoped>
.nav-center {
  position: absolute;
  left: 50%;
  transform: translateX(-50%);
}

.category-dropdown {
  min-width: 320px;
  max-width: 85vw;
  padding: 0;
  max-height: 75vh;
  overflow-y: auto;
  border-radius: 12px;
  box-shadow: 0 8px 30px rgba(0, 0, 0, 0.15);
  background-color: #f5f5f5;
}

:deep(.v-theme--dark .category-dropdown) {
  box-shadow: 0 8px 30px rgba(0, 0, 0, 0.3);
  background-color: #1E1E1E;
}
</style>
