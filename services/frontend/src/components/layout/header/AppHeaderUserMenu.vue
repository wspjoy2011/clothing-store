<template>
  <v-menu location="bottom end" transition="slide-y-transition">
    <template v-slot:activator="{ props }">
      <v-btn icon class="mr-2" v-bind="props">
        <v-icon
            v-if="isAuthenticated"
            icon="mdi-account-check"
            color="success"
        ></v-icon>
        <v-icon v-else icon="mdi-account-outline"></v-icon>
      </v-btn>
    </template>

    <v-card min-width="200">
      <v-list>
        <!-- Authenticated User Menu -->
        <template v-if="isAuthenticated">
          <v-list-item
              v-if="currentUser"
              class="user-info-item"
          >
            <template v-slot:prepend>
              <v-avatar size="32" color="primary">
                <v-icon icon="mdi-account" size="18"></v-icon>
              </v-avatar>
            </template>
            <v-list-item-title class="text-subtitle-2 font-weight-medium">
              {{ userDisplayName }}
            </v-list-item-title>
            <v-list-item-subtitle class="text-caption">
              {{ userEmail }}
            </v-list-item-subtitle>
          </v-list-item>

          <v-divider></v-divider>

          <v-list-item
              prepend-icon="mdi-account-cog"
              title="Account Settings"
              subtitle="Manage your account"
              @click="$emit('go-to-account-settings')"
          ></v-list-item>

          <v-list-item
              prepend-icon="mdi-account"
              title="Profile"
              subtitle="View your profile"
              @click="$emit('go-to-profile')"
          ></v-list-item>

          <v-list-item
              prepend-icon="mdi-lock-reset"
              title="Change Password"
              subtitle="Update your password"
              @click="$emit('go-to-change-password')"
          ></v-list-item>

          <v-list-item
              prepend-icon="mdi-heart"
              title="Wishlist"
              subtitle="Your saved items"
              @click="$emit('go-to-wishlist')"
          ></v-list-item>

          <v-list-item
              prepend-icon="mdi-history"
              title="Order History"
              subtitle="View past orders"
              @click="$emit('go-to-order-history')"
          ></v-list-item>

          <v-divider></v-divider>

          <v-list-item
              prepend-icon="mdi-logout"
              title="Sign Out"
              subtitle="Logout from account"
              @click="$emit('handle-logout')"
              class="logout-item"
          ></v-list-item>
        </template>

        <!-- Guest User Menu -->
        <template v-else>
          <v-list-item
              :to="{ name: 'register' }"
              prepend-icon="mdi-account-plus"
              title="Register"
              subtitle="Create new account"
          ></v-list-item>

          <v-list-item
              prepend-icon="mdi-login"
              title="Sign In"
              subtitle="Access your account"
              @click="$emit('go-to-login')"
          ></v-list-item>
        </template>
      </v-list>
    </v-card>
  </v-menu>
</template>

<script setup>
defineProps({
  isAuthenticated: {
    type: Boolean,
    default: false
  },
  currentUser: {
    type: Object,
    default: null
  },
  userDisplayName: {
    type: String,
    default: ''
  },
  userEmail: {
    type: String,
    default: ''
  }
})

defineEmits([
  'go-to-login',
  'go-to-account-settings',
  'go-to-profile',
  'go-to-change-password',
  'go-to-wishlist',
  'go-to-order-history',
  'handle-logout'
])
</script>

<style scoped>
.user-info-item {
  background-color: rgb(from rgb(25, 118, 210) r g b / 0.1);
  margin-bottom: 4px;
}

.logout-item {
  color: #FF5252;
}

.logout-item:hover {
  background-color: rgb(from rgb(255, 82, 82) r g b / 0.1);
}

:deep(.v-theme--dark) .user-info-item {
  background-color: rgb(from rgb(144, 202, 249) r g b / 0.1);
}

:deep(.v-theme--dark) .logout-item {
  color: #EF5350;
}

:deep(.v-theme--dark) .logout-item:hover {
  background-color: rgb(from rgb(239, 83, 80) r g b / 0.1);
}
</style>
