<template>
  <div class="breadcrumbs-container mb-5">
    <nav aria-label="breadcrumb">
      <ul class="breadcrumbs">
        <li class="breadcrumb-item">
          <router-link to="/" class="breadcrumb-link">
            <v-icon icon="mdi-home" size="small" class="breadcrumb-icon"/>
            <span>Home</span>
          </router-link>
        </li>

        <li class="breadcrumb-divider">
          <v-icon icon="mdi-chevron-right" size="small" class="chevron-icon"/>
        </li>

        <li class="breadcrumb-item">
          <router-link to="/catalog" class="breadcrumb-link">
            <v-icon icon="mdi-shopping" size="small" class="breadcrumb-icon"/>
            <span>Catalog</span>
          </router-link>
        </li>

        <template v-if="masterCategory">
          <li class="breadcrumb-divider">
            <v-icon icon="mdi-chevron-right" size="small" class="chevron-icon"/>
          </li>
          <li class="breadcrumb-item" :class="{ 'active': isCurrentRoute('master-category') }">
            <router-link
                v-if="!isCurrentRoute('master-category')"
                :to="{ name: 'master-category', params: { masterCategory: masterCategorySlug } }"
                class="breadcrumb-link"
            >
              <v-icon icon="mdi-shape" size="small" class="breadcrumb-icon"/>
              <span>{{ masterCategory.name }}</span>
            </router-link>
            <span v-else class="breadcrumb-text">
              <v-icon icon="mdi-shape" size="small" class="breadcrumb-icon"/>
              {{ masterCategory.name }}
            </span>
          </li>
        </template>

        <template v-if="subCategory">
          <li class="breadcrumb-divider">
            <v-icon icon="mdi-chevron-right" size="small" class="chevron-icon"/>
          </li>
          <li class="breadcrumb-item" :class="{ 'active': isCurrentRoute('sub-category') }">
            <router-link
                v-if="subCategorySlug && !isCurrentRoute('sub-category')"
                :to="{ name: 'sub-category', params: { masterCategory: masterCategorySlug, subCategory: subCategorySlug } }"
                class="breadcrumb-link"
            >
              <v-icon icon="mdi-tag" size="small" class="breadcrumb-icon"/>
              <span>{{ subCategory.name }}</span>
            </router-link>
            <span v-else class="breadcrumb-text">
              <v-icon icon="mdi-tag" size="small" class="breadcrumb-icon"/>
              {{ subCategory.name }}
            </span>
          </li>
        </template>

        <template v-if="articleType">
          <li class="breadcrumb-divider">
            <v-icon icon="mdi-chevron-right" size="small" class="chevron-icon"/>
          </li>
          <li class="breadcrumb-item active">
            <span class="breadcrumb-text">
              <v-icon icon="mdi-tshirt-crew" size="small" class="breadcrumb-icon"/>
              {{ articleType.name }}
            </span>
          </li>
        </template>
      </ul>
    </nav>
  </div>
</template>

<script setup>
import {useRoute} from 'vue-router';

const route = useRoute();

defineProps({
  masterCategory: {
    type: Object,
    default: null
  },
  subCategory: {
    type: Object,
    default: null
  },
  articleType: {
    type: Object,
    default: null
  },
  masterCategorySlug: {
    type: String,
    default: null
  },
  subCategorySlug: {
    type: String,
    default: null
  }
});

const isCurrentRoute = (routeName) => {
  return route.name === routeName;
};
</script>

<style scoped>
.breadcrumbs-container {
  border-radius: 8px;
  padding: 12px 16px;
  transition: all 0.3s ease;
}

.theme--light .breadcrumbs-container {
  background-color: #f8f9fa;
  box-shadow: 0 2px 5px rgba(0, 0, 0, 0.05);
}

.theme--dark .breadcrumbs-container {
  background-color: rgba(30, 30, 30, 0.7);
  box-shadow: 0 2px 5px rgba(0, 0, 0, 0.2);
}

.breadcrumbs {
  display: flex;
  flex-wrap: wrap;
  padding: 0;
  margin: 0;
  list-style: none;
  align-items: center;
}

.breadcrumb-item {
  display: flex;
  align-items: center;
  font-size: 14px;
  white-space: nowrap;
}

.breadcrumb-link {
  display: flex;
  align-items: center;
  text-decoration: none;
  transition: all 0.2s ease;
  font-weight: 500;
  padding: 4px 8px;
  border-radius: 4px;
}

.theme--light .breadcrumb-link {
  color: #5c6bc0;
}

.theme--dark .breadcrumb-link {
  color: #7986cb;
}

.theme--light .breadcrumb-link:hover {
  color: #3f51b5;
  background-color: rgba(63, 81, 181, 0.08);
}

.theme--dark .breadcrumb-link:hover {
  color: #9fa8da;
  background-color: rgba(121, 134, 203, 0.15);
}

.breadcrumb-text {
  display: flex;
  align-items: center;
  font-weight: 600;
  padding: 4px 8px;
}

.theme--light .breadcrumb-text {
  color: #424242;
}

.theme--dark .breadcrumb-text {
  color: #e0e0e0;
}

.breadcrumb-icon {
  margin-right: 6px;
}

.breadcrumb-divider {
  display: flex;
  align-items: center;
  margin: 0 2px;
}

.theme--light .breadcrumb-divider {
  color: #bdbdbd;
}

.theme--dark .breadcrumb-divider {
  color: #616161;
}

.chevron-icon {
  font-size: 18px;
}

.theme--light .chevron-icon {
  color: #9e9e9e;
}

.theme--dark .chevron-icon {
  color: #757575;
}

.active .breadcrumb-link {
  font-weight: 600;
}

.theme--light .active .breadcrumb-link,
.theme--light .active .breadcrumb-text {
  color: #424242;
}

.theme--dark .active .breadcrumb-link,
.theme--dark .active .breadcrumb-text {
  color: #e0e0e0;
}

.theme--light .active .breadcrumb-text {
  background-color: rgba(0, 0, 0, 0.03);
  border-radius: 4px;
}

.theme--dark .active .breadcrumb-text {
  background-color: rgba(255, 255, 255, 0.05);
  border-radius: 4px;
}

@media (max-width: 768px) {
  .breadcrumbs-container {
    padding: 8px 12px;
  }

  .breadcrumb-item {
    font-size: 13px;
  }
}

@media (max-width: 600px) {
  .breadcrumb-icon {
    margin-right: 4px;
  }

  .breadcrumb-divider {
    margin: 0;
  }

  .breadcrumb-link,
  .breadcrumb-text {
    padding: 3px 4px;
  }
}
</style>
