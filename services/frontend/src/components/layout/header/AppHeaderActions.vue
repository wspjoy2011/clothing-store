<template>
  <div class="d-flex align-center">
    <theme-toggle class="mr-2"/>
    <search-bar class="mr-2"/>

    <slot name="user-menu"></slot>

    <v-btn icon @click="$emit('go-to-cart')">
      <v-badge
          color="error"
          content="2"
          dot
      >
        <v-icon>mdi-cart</v-icon>
      </v-badge>
    </v-btn>

    <!-- Category Path Indicator for Mobile -->
    <v-btn
        v-if="showCategoryPath"
        icon
        class="ml-2 hidden-lg-and-up"
        @click="$emit('toggle-category-path')"
    >
      <v-badge
          color="primary"
          dot
      >
        <v-icon>mdi-tag-multiple</v-icon>
      </v-badge>
    </v-btn>

    <!-- Mobile Menu Button -->
    <v-btn
        icon
        class="ml-2 hidden-md-and-up"
        @click="$emit('toggle-mobile-drawer')"
    >
      <v-icon>mdi-menu</v-icon>
    </v-btn>
  </div>
</template>

<script setup>
import ThemeToggle from '@/components/ui/theme/ThemeToggle.vue'
import SearchBar from '@/components/ui/search/SearchBar.vue'

defineProps({
  showCategoryPath: {
    type: Boolean,
    default: false
  }
})

defineEmits(['go-to-cart', 'toggle-category-path', 'toggle-mobile-drawer'])
</script>
