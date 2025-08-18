<template>
  <div class="cart-item-card">
    <v-row no-gutters align="center" class="cart-item-content">
      <!-- Product Image -->
      <v-col cols="3" sm="2" md="2">
        <CartItemImage
            :item="item"
            @view-product="handleViewProduct"
        />
      </v-col>

      <!-- Product Details -->
      <v-col cols="9" sm="6" md="7" class="product-details">
        <div class="product-info">
          <h4 class="product-name" @click="handleViewProduct">
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
          <CartItemQuantityMobile
              class="d-sm-none"
              :item="item"
              :updating="updating"
              :removing="removing"
              :max-available="maxAvailable"
              :is-available="!!item.is_available"
              @increase="handleIncreaseQuantity"
              @decrease="handleDecreaseQuantity"
              @remove="handleRemove"
          />
        </div>
      </v-col>

      <!-- Desktop Quantity Controls -->
      <v-col cols="0" sm="2" md="2" class="d-none d-sm-flex quantity-section">
        <CartItemQuantityDesktop
            :item="item"
            :updating="updating"
            :max-available="maxAvailable"
            :is-available="!!item.is_available"
            @increase="handleIncreaseQuantity"
            @decrease="handleDecreaseQuantity"
        />
      </v-col>

      <!-- Total Price & Actions (Desktop) -->
      <v-col cols="0" sm="2" md="1" class="d-none d-sm-flex total-section">
        <CartItemTotalActions
            :has-discount="hasItemDiscount(item)"
            :sale-total="formatItemSaleTotal(item)"
            :regular-total="formatItemTotal(item)"
            :removing="removing"
            @remove="handleRemove"
        />
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
import {ref, computed} from 'vue'
import {useCartFormatting} from '@/composables/cart/useCartFormatting.js'
import CartItemImage from '@/components/cart/cart-item/CartItemImage.vue'
import CartItemQuantityMobile from '@/components/cart/cart-item/CartItemQuantityMobile.vue'
import CartItemQuantityDesktop from '@/components/cart/cart-item/CartItemQuantityDesktop.vue'
import CartItemTotalActions from '@/components/cart/cart-item/CartItemTotalActions.vue'

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
    emit('update:quantity', props.item.id, props.item.quantity + 1)
  } finally {
    updating.value = false
  }
}

const handleDecreaseQuantity = async () => {
  if (updating.value || props.item.quantity <= 1) return
  updating.value = true
  try {
    emit('update:quantity', props.item.id, props.item.quantity - 1)
  } finally {
    updating.value = false
  }
}

const handleRemove = async () => {
  if (removing.value) return
  removing.value = true
  try {
    emit('remove', props.item.id)
  } finally {
    removing.value = false
  }
}

const handleViewProduct = () => {
  emit('view-product', props.item.product_slug)
}
</script>

<style scoped>
/* Container styles */
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

/* Prices */
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

/* Sections alignment */
.quantity-section {
  justify-content: center;
}

.total-section {
  justify-content: center;
  align-items: center;
}

/* Mobile total */
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

/* Dark theme support for shared parts */
:deep(.v-theme--dark) {
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
}

/* Responsive */
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
