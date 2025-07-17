<template>
  <v-dialog
      :model-value="showMobileSearch"
      @update:model-value="$emit('update:show-mobile-search', $event)"
      fullscreen
      transition="dialog-bottom-transition"
  >
    <v-card>
      <v-toolbar density="compact" color="primary">
        <v-btn icon @click="$emit('close-mobile-search')">
          <v-icon>mdi-close</v-icon>
        </v-btn>
        <v-toolbar-title>Search</v-toolbar-title>
      </v-toolbar>
      <v-card-text class="pt-4">
        <v-text-field
            :model-value="mobileSearchQuery"
            @update:model-value="$emit('update:mobile-search-query', $event)"
            placeholder="Search products..."
            variant="outlined"
            prepend-inner-icon="mdi-magnify"
            clearable
            autofocus
            @keyup.enter="$emit('handle-mobile-search')"
        >
          <template v-slot:append>
            <v-progress-circular
                v-if="isSearchLoading"
                indeterminate
                size="20"
                width="2"
                color="primary"
                class="mr-2"
            ></v-progress-circular>
            <v-btn
                v-else-if="mobileSearchQuery"
                icon="mdi-close"
                size="small"
                variant="text"
                @click="$emit('clear-mobile-search')"
            ></v-btn>
          </template>
        </v-text-field>
      </v-card-text>
    </v-card>
  </v-dialog>
</template>

<script setup>
defineProps({
  showMobileSearch: {
    type: Boolean,
    default: false
  },
  mobileSearchQuery: {
    type: String,
    default: ''
  },
  isSearchLoading: {
    type: Boolean,
    default: false
  }
})

defineEmits([
  'update:show-mobile-search',
  'update:mobile-search-query',
  'close-mobile-search',
  'handle-mobile-search',
  'clear-mobile-search'
])
</script>
