<template>
  <div class="cart-item-card">
    <v-row no-gutters align="center" class="cart-item-content">
      <!-- Product Image -->
      <v-col cols="3" sm="2" md="2">
        <div class="product-image-container">
          <v-img
              :src="item.product_image_url"
              :alt="item.product_name"
              height="80"
              width="80"
              cover
              class="product-image"
              @click="handleViewProduct"
          >
            <template #placeholder>
              <div class="image-placeholder">
                <v-icon icon="mdi-image" size="24" color="grey-lighten-2"/>
              </div>
            </template>
          </v-img>

          <!-- Availability Badge -->
          <div v-if="!item.is_available" class="availability-badge">
            <v-chip
                color="error"
                size="x-small"
                variant="elevated"
            >
              Out of Stock
            </v-chip>
          </div>
        </div>
      </v-col>

      <!-- Product Details -->
      <v-col cols="9" sm="6" md="7" class="product-details">
        <div class="product-info">
          <h4
              class="product-name"
              @click="handleViewProduct"
          >
            {{ item.product_name }}
          </h4>

          <!-- Price Information -->
          <div class="price-info">
            <div v-if="hasItemDiscount(item)" class="price-with-sale">
              <span class="sale-price">${{ formatItemPrice(item.sale_price) }}</span>
              <span class="original-price">${{ formatItemPrice(item.unit_price) }}</span>
              <span class="discount-badge">Save ${{ getItemDiscount(item) }}</span>
            </div>
            <div v-else class="regular-price">
              <span class="unit-price">${{ formatItemPrice(item.unit_price) }}</span>
            </div>
          </div>

          <!-- Mobile Quantity Controls -->
          <div class="mobile-controls d-sm-none">
            <div class="quantity-controls">
              <v-btn
                  icon
                  size="x-small"
                  variant="outlined"
                  color="primary"
                  :disabled="item.quantity <= 1 || updating"
                  @click="handleDecreaseQuantity"
              >
                <v-icon size="12">mdi-minus</v-icon>
              </v-btn>

              <span class="quantity-display">{{ item.quantity }}</span>

              <v-btn
                  icon
                  size="x-small"
                  variant="outlined"
                  color="primary"
                  :disabled="!item.is_available || updating || (props.maxAvailable !== null && item.quantity >= props.maxAvailable)"
                  @click="handleIncreaseQuantity"
                  :title="props.maxAvailable !== null && item.quantity >= props.maxAvailable ? 'Maximum available reached' : ''"
              >
                <v-icon size="12">mdi-plus</v-icon>
              </v-btn>
            </div>

            <div class="item-actions">
              <v-btn
                  icon
                  size="small"
                  variant="text"
                  color="error"
                  @click="handleRemove"
                  :loading="removing"
              >
                <v-icon size="16">mdi-delete</v-icon>
              </v-btn>
            </div>
          </div>
        </div>
      </v-col>

      <!-- Desktop Quantity Controls -->
      <v-col cols="0" sm="2" md="2" class="d-none d-sm-flex quantity-section">
        <div class="quantity-controls-desktop">
          <v-btn
              icon
              size="small"
              variant="outlined"
              color="primary"
              :disabled="item.quantity <= 1 || updating"
              @click="handleDecreaseQuantity"
          >
            <v-icon size="14">mdi-minus</v-icon>
          </v-btn>

          <span class="quantity-display-desktop">{{ item.quantity }}</span>

          <v-btn
              icon
              size="small"
              variant="outlined"
              color="primary"
              :disabled="!item.is_available || updating || (props.maxAvailable !== null && item.quantity >= props.maxAvailable)"
              @click="handleIncreaseQuantity"
              :title="props.maxAvailable !== null && item.quantity >= props.maxAvailable ? 'Maximum available reached' : ''"
          >
            <v-icon size="14">mdi-plus</v-icon>
          </v-btn>
        </div>
      </v-col>

      <!-- Total Price & Actions -->
      <v-col cols="0" sm="2" md="1" class="d-none d-sm-flex total-section">
        <div class="item-total">
          <div class="total-price">
            <div v-if="hasItemDiscount(item)" class="sale-total">
              ${{ formatItemSaleTotal(item) }}
            </div>
            <div v-else class="regular-total">
              ${{ formatItemTotal(item) }}
            </div>
          </div>

          <v-btn
              icon
              size="small"
              variant="text"
              color="error"
              @click="handleRemove"
              :loading="removing"
              class="remove-btn"
          >
            <v-icon size="18">mdi-delete</v-icon>
          </v-btn>
        </div>
      </v-col>
    </v-row>

    <!-- Mobile Total Price -->
    <div class="mobile-total d-sm-none">
      <div class="total-price-mobile">
        <span>Total: </span>
        <span v-if="hasItemDiscount(item)" class="sale-total">
          ${{ formatItemSaleTotal(item) }}
        </span>
        <span v-else class="regular-total">
          ${{ formatItemTotal(item) }}
        </span>
      </div>
    </div>

  </div>
</template>

<script setup>
import { ref, computed } from 'vue'
import { useCartFormatting } from '@/composables/cart/useCartFormatting.js'

const props = defineProps({
  item: {
    type: Object,
    required: true
  },
   maxAvailable: {
    type: Number,
    required: false,
    default: null
  }
})

const emit = defineEmits(['update:quantity', 'remove', 'view-product'])

const updating = ref(false)
const removing = ref(false)

const itemCart = computed(() => ({
  value: {
    items: [props.item]
  }
}))

const {
  formatItemPrice,
  formatItemTotal,
  formatItemSaleTotal,
  getItemDiscount,
  hasItemDiscount
} = useCartFormatting(itemCart)

const handleIncreaseQuantity = async () => {
  if (updating.value) return

  updating.value = true
  try {
    await emit('update:quantity', props.item.id, props.item.quantity + 1)
  } catch (error) {
    console.error('Failed to increase quantity:', error)
  } finally {
    updating.value = false
  }
}

const handleDecreaseQuantity = async () => {
  if (updating.value || props.item.quantity <= 1) return

  updating.value = true
  try {
    await emit('update:quantity', props.item.id, props.item.quantity - 1)
  } catch (error) {
    console.error('Failed to decrease quantity:', error)
  } finally {
    updating.value = false
  }
}

const handleRemove = async () => {
  if (removing.value) return

  removing.value = true
  try {
    await emit('remove', props.item.id)
  } catch (error) {
    console.error('Failed to remove item:', error)
  } finally {
    removing.value = false
  }
}

const handleViewProduct = () => {
  emit('view-product', props.item.product_slug)
}
</script>

<style scoped>
/* Light theme styles */
.cart-item-card {
  position: relative;
  padding: 20px;
  transition: background-color 0.2s ease;
  border-radius: 8px;
}

.cart-item-card:hover {
  background-color: rgba(0, 0, 0, 0.02);
}

.cart-item-content {
  align-items: center;
}

.product-image-container {
  position: relative;
  cursor: pointer;
  border-radius: 8px;
  overflow: hidden;
}

.product-image {
  border-radius: 8px;
  transition: transform 0.2s ease;
}

.product-image:hover {
  transform: scale(1.05);
}

.image-placeholder {
  display: flex;
  align-items: center;
  justify-content: center;
  height: 100%;
  background-color: #f5f5f5;
}

.availability-badge {
  position: absolute;
  top: -4px;
  right: -4px;
  z-index: 1;
}

.product-details {
  padding-left: 16px;
}

.product-info {
  height: 100%;
  display: flex;
  flex-direction: column;
  justify-content: space-between;
}

.product-name {
  font-size: 1rem;
  font-weight: 600;
  color: #1a1a1a;
  margin-bottom: 8px;
  cursor: pointer;
  transition: color 0.2s ease;
  line-height: 1.3;
}

.product-name:hover {
  color: #1976d2;
}

.price-info {
  margin-bottom: 12px;
}

.price-with-sale {
  display: flex;
  align-items: center;
  flex-wrap: wrap;
  gap: 8px;
}

.sale-price {
  font-size: 1rem;
  font-weight: 700;
  color: #d32f2f;
}

.original-price {
  font-size: 0.9rem;
  color: #666;
  text-decoration: line-through;
}

.discount-badge {
  font-size: 0.75rem;
  color: #2e7d32;
  background-color: rgba(46, 125, 50, 0.1);
  padding: 2px 6px;
  border-radius: 4px;
  font-weight: 600;
}

.regular-price .unit-price {
  font-size: 1rem;
  font-weight: 600;
  color: #1976d2;
}

.mobile-controls {
  display: flex;
  justify-content: space-between;
  align-items: center;
  margin-top: 8px;
}

.quantity-controls {
  display: flex;
  align-items: center;
  gap: 12px;
}

.quantity-display {
  min-width: 20px;
  text-align: center;
  font-weight: 600;
  font-size: 0.9rem;
  color: #1a1a1a;
}

.quantity-section {
  justify-content: center;
}

.quantity-controls-desktop {
  display: flex;
  flex-direction: column;
  align-items: center;
  gap: 8px;
}

.quantity-display-desktop {
  min-width: 24px;
  text-align: center;
  font-weight: 600;
  font-size: 1rem;
  color: #1a1a1a;
}

.total-section {
  justify-content: center;
  align-items: center;
}

.item-total {
  text-align: center;
}

.total-price {
  margin-bottom: 8px;
}

.sale-total,
.regular-total {
  font-size: 1.1rem;
  font-weight: 700;
  color: #1976d2;
}

.sale-total {
  color: #d32f2f;
}

.remove-btn {
  transition: all 0.2s ease;
}

.remove-btn:hover {
  background-color: rgba(244, 67, 54, 0.1);
}

.mobile-total {
  margin-top: 12px;
  padding-top: 12px;
  border-top: 1px solid rgba(0, 0, 0, 0.06);
}

.total-price-mobile {
  font-size: 1rem;
  font-weight: 700;
  text-align: right;
  display: flex;
  justify-content: flex-end;
  align-items: center;
  gap: 4px;
  color: #1a1a1a;
}

.total-price-mobile .sale-total {
  color: #d32f2f;
}

.total-price-mobile .regular-total {
  color: #1976d2;
}

/* Dark theme support */
:deep(.v-theme--dark) {
  .cart-item-card {
    background-color: rgba(255, 255, 255, 0.02);
  }

  .cart-item-card:hover {
    background-color: rgba(255, 255, 255, 0.08);
  }

  .image-placeholder {
    background-color: rgba(255, 255, 255, 0.05);
  }

  .product-name {
    color: #e8eaed;
  }

  .product-name:hover {
    color: #90caf9;
  }

  .sale-price {
    color: #ff6b6b;
  }

  .original-price {
    color: #9aa0a6;
  }

  .discount-badge {
    color: #4caf50;
    background-color: rgba(76, 175, 80, 0.15);
  }

  .regular-price .unit-price {
    color: #90caf9;
  }

  .quantity-display {
    color: #e8eaed;
  }

  .quantity-display-desktop {
    color: #e8eaed;
  }

  .sale-total {
    color: #ff6b6b;
  }

  .regular-total {
    color: #90caf9;
  }

  .total-price-mobile {
    color: #e8eaed;
  }

  .total-price-mobile .sale-total {
    color: #ff6b6b;
  }

  .total-price-mobile .regular-total {
    color: #90caf9;
  }

  .mobile-total {
    border-top: 1px solid rgba(255, 255, 255, 0.12);
  }

  .updating-overlay {
    background-color: rgba(18, 18, 18, 0.8);
  }

  .remove-btn:hover {
    background-color: rgba(244, 67, 54, 0.15);
  }
}

/* Responsive adjustments */
@media (max-width: 600px) {
  .cart-item-card {
    padding: 16px;
  }

  .product-details {
    padding-left: 12px;
  }

  .product-name {
    font-size: 0.9rem;
  }

  .price-with-sale {
    flex-direction: column;
    align-items: flex-start;
    gap: 4px;
  }
}
</style>
