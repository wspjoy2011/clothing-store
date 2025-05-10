<template>
  <v-container>
    <v-card class="mx-auto my-12" max-width="800" elevation="2">
      <v-img
        height="300"
        src="https://images.unsplash.com/photo-1607083206968-13611e3d76db?q=80&w=2215&auto=format&fit=crop"
        cover
        class="align-end"
      >
        <v-card-title class="text-white text-h4 font-weight-bold bg-black bg-opacity-30 pa-4">
          Browse Catalog
        </v-card-title>
      </v-img>

      <v-card-text class="py-6">
        <p class="text-h6 text-center">
          Welcome to StyleShop, your ultimate fashion destination.
        </p>
        <p class="text-body-1 mt-4">
          Discover the latest trends, find your perfect outfit, and express your unique style.
          Our carefully curated collections feature premium quality clothing for every occasion.
        </p>
      </v-card-text>

      <v-card-actions class="justify-center pb-6">
        <v-btn color="primary" size="large" variant="flat">
          Explore Collection
        </v-btn>
      </v-card-actions>
    </v-card>
  </v-container>
</template>

<script setup>
</script>