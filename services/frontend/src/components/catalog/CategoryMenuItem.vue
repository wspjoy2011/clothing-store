<template>
  <div class="category-menu-item" :class="'depth-' + depth">
    <v-menu
      v-if="hasChildren"
      location="end"
      :offset="[0, 5]"
      open-on-hover
      transition="slide-x-transition"
      content-class="category-submenu-container"
    >
      <template v-slot:activator="{ props }">
        <v-btn
          variant="elevated"
          v-bind="props"
          color="lightgrey"
          class="category-btn"
          @click="handleItemClick"
        >
          <span class="category-btn-text">{{ item.name }}</span>
          <v-icon end>mdi-chevron-right</v-icon>
        </v-btn>
      </template>

      <v-card class="category-submenu-card">
        <v-list class="category-submenu">
          <v-list-subheader>{{ item.name }}</v-list-subheader>
          <v-divider></v-divider>

          <v-list-item
            v-for="subItem in getChildItems"
            :key="`${childrenType}-${subItem.id}`"
            class="category-list-item"
          >
            <template v-if="hasNestedChildren(subItem)">
              <category-menu-item
                :item="subItem"
                :children-type="getNextChildrenType"
                :depth="depth + 1"
              />
            </template>
            <template v-else>
              <v-list-item-title
                @click="handleNestedItemClick(subItem)"
                class="nested-item-title"
              >
                {{ subItem.name }}
              </v-list-item-title>
            </template>
          </v-list-item>
        </v-list>
      </v-card>
    </v-menu>

    <v-btn
      v-else
      variant="elevated"
      color="lightgrey"
      class="category-btn"
      @click="handleItemClick"
    >
      {{ item.name }}
    </v-btn>
  </div>
</template>

<script>
export default {
  name: 'CategoryMenuItem',

  props: {
    item: {
      type: Object,
      required: true
    },
    childrenType: {
      type: String,
      default: 'sub_categories'
    },
    depth: {
      type: Number,
      default: 0
    }
  },

  computed: {
    hasChildren() {
      return this.item[this.childrenType] && this.item[this.childrenType].length > 0;
    },

    getChildItems() {
      return this.item[this.childrenType] || [];
    },

    getNextChildrenType() {
      return this.childrenType === 'sub_categories' ? 'article_types' : '';
    },

    getItemType() {
      if (this.childrenType === 'sub_categories') return 'master';
      if (this.childrenType === 'article_types') return 'sub';
      return 'article';
    }
  },

  methods: {
    hasNestedChildren(item) {
      const nextType = this.getNextChildrenType;
      return nextType && item[nextType] && item[nextType].length > 0;
    },

    handleItemClick() {
      this.$emit('item-click', {
        id: this.item.id,
        name: this.item.name,
        type: this.getItemType
      });
    },

    handleNestedItemClick(item) {
      this.$emit('item-click', {
        id: item.id,
        name: item.name,
        type: this.getNextChildrenType === '' ? 'article' : 'sub'
      });
    }
  }
}
</script>

<style scoped>
.category-menu-item {
  position: relative;
  width: 100%;
}

.category-btn {
  width: 100%;
  text-align: left;
  justify-content: space-between;
  padding: 12px 16px;
  font-weight: 500;
  letter-spacing: 0.5px;
  border-radius: 8px;
  text-transform: none;
  box-shadow: 0 2px 8px rgba(0, 0, 0, 0.1);
  transition: box-shadow 0.3s ease, transform 0.2s ease;
}

.category-btn:hover {
  box-shadow: 0 4px 12px rgba(0, 0, 0, 0.15);
  transform: translateY(-2px);
}

.category-btn-text {
  white-space: nowrap;
  overflow: hidden;
  text-overflow: ellipsis;
}

.category-submenu-container {
  border-radius: 12px;
  overflow: hidden;
  box-shadow: 0 5px 25px rgba(0, 0, 0, 0.1);
}

.category-submenu-card {
  border-radius: 12px;
  overflow: hidden;
}

.category-submenu {
  min-width: 220px;
  max-width: 320px;
  max-height: 400px;
  overflow-y: auto;
  padding: 8px 0;
}

.category-list-item {
  padding: 0 4px;
}

.nested-item-title {
  padding: 8px 16px;
  cursor: pointer;
  border-radius: 6px;
  transition: background-color 0.2s;
  font-size: 0.95rem;
}

.nested-item-title:hover {
  background-color: rgba(245, 245, 245, 0.7);
}

.depth-0 .category-btn {
  font-weight: 600;
  font-size: 1rem;
}

.depth-1 .category-btn {
  font-weight: 500;
  font-size: 0.95rem;
  padding: 10px 16px;
}

.depth-2 .category-btn {
  font-weight: 400;
  font-size: 0.9rem;
  padding: 8px 16px;
}
</style>
