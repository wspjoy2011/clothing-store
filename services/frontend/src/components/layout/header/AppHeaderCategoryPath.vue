<template>
  <div
      v-if="showCategoryPath && categoryPathVisible"
      class="category-path-dropdown"
      :class="{ 'theme-dark': isDarkTheme }"
  >
    <v-container>
      <div class="d-flex align-center justify-space-between">
        <div class="category-breadcrumbs">
          <v-chip-group>
            <v-chip
                v-for="(category, index) in currentCategoryPath"
                :key="index"
                :color="getCategoryChipColor(category.type)"
                variant="elevated"
                size="small"
                :class="['mr-1', `text-${getCategoryChipColor(category.type)}`]"
                @click="$emit('navigate-to-category', category, index)"
            >
              <v-icon
                  start
                  :icon="getCategoryIcon(category.type)"
                  size="small"
              ></v-icon>
              {{ category.name }}
            </v-chip>
          </v-chip-group>
        </div>
        <v-btn
            icon
            variant="text"
            @click="$emit('close-category-path')"
            size="small"
        >
          <v-icon>mdi-close</v-icon>
        </v-btn>
      </div>
    </v-container>
  </div>
</template>

<script setup>
defineProps({
  showCategoryPath: {
    type: Boolean,
    default: false
  },
  categoryPathVisible: {
    type: Boolean,
    default: false
  },
  isDarkTheme: {
    type: Boolean,
    default: false
  },
  currentCategoryPath: {
    type: Array,
    default: () => []
  }
})

defineEmits(['navigate-to-category', 'close-category-path'])

function getCategoryChipColor(type) {
  switch (type) {
    case 'master':
      return 'primary'
    case 'sub':
      return 'secondary'
    case 'article':
      return 'success'
    default:
      return 'grey'
  }
}

function getCategoryIcon(type) {
  switch (type) {
    case 'master':
      return 'mdi-tag'
    case 'sub':
      return 'mdi-tag-outline'
    case 'article':
      return 'mdi-tshirt-crew-outline'
    default:
      return 'mdi-shape-outline'
  }
}
</script>

<style scoped>
.category-path-dropdown {
  position: fixed;
  top: 64px;
  left: 0;
  right: 0;
  z-index: 99;
  background-color: #f5f5f5;
  box-shadow: 0 4px 15px rgba(0, 0, 0, 0.1);
  padding: 16px 0;
  border-bottom-left-radius: 12px;
  border-bottom-right-radius: 12px;
  animation: slideDown 0.3s ease-out;
  font-size: 1.05rem;
}

@keyframes slideDown {
  from {
    opacity: 0;
    transform: translateY(-20px);
  }
  to {
    opacity: 1;
    transform: translateY(0);
  }
}

.category-path-dropdown.theme-dark {
  background-color: #1E1E1E;
  box-shadow: 0 4px 15px rgba(0, 0, 0, 0.3);
  border-top: 1px solid rgba(255, 255, 255, 0.1);
}

.category-breadcrumbs {
  overflow-x: auto;
  white-space: nowrap;
  -ms-overflow-style: none;
  scrollbar-width: none;
}

.category-breadcrumbs::-webkit-scrollbar {
  display: none;
}

.v-chip {
  background-color: #e0e0e0;
  color: rgba(0, 0, 0, 0.87);
  font-size: 0.95rem;
  font-weight: 500;
}

.v-chip.v-chip--elevated {
  box-shadow: 0 2px 5px rgba(0, 0, 0, 0.08);
}

.theme-dark .v-chip {
  background-color: #2A2A2A;
  color: rgba(255, 255, 255, 0.87);
}

.theme-dark .v-chip.v-chip--elevated {
  box-shadow: 0 2px 8px rgba(0, 0, 0, 0.5);
}

.theme-dark .v-chip.text-primary {
  background-color: rgba(144, 202, 249, 0.15);
  color: #90CAF9;
}

.theme-dark .v-chip.text-secondary {
  background-color: rgba(97, 97, 97, 0.15);
  color: #616161;
}

.theme-dark .v-chip.text-success {
  background-color: rgba(129, 199, 132, 0.15);
  color: #81C784;
}

@media (max-width: 960px) {
  .category-path-dropdown {
    top: 56px;
  }
}
</style>
