<template>
  <v-row justify="center">
    <v-col cols="12">
      <v-breadcrumbs
        :items="items"
        density="compact"
        class="px-0"
      >
        <template v-slot:divider>
          <v-icon icon="mdi-chevron-right" size="small" />
        </template>
      </v-breadcrumbs>
    </v-col>
  </v-row>
</template>

<script setup>
const props = defineProps({
  items: {
    type: Array,
    required: true
  }
});
</script>
