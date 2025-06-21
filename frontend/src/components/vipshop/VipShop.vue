<template>
  <div class="vip-shop-container">
    <!-- Левая колонка с категориями -->
    <aside class="shop-sidebar">
      <div
        v-for="category in categories"
        :key="category"
        :class="['category', { active: selectedCategory === category }]"
        @click="selectCategory(category)"
      >
        {{ category }}
      </div>
    </aside>

    <!-- Правая колонка с товарами -->
    <section class="shop-main">
      <div class="products-grid">
        <div
          v-for="product in filteredProducts"
          :key="product.id"
          class="product-card"
        >
          <img
            :src="`${STATIC}/static/goods/${product.image}`"
            alt="product image"
          />
          <h3>{{ product.name }}</h3>
          <p class="price">{{ product.nulling_price }} 🧿</p>
        </div>
      </div>
    </section>
  </div>
</template>

<script setup>
import { ref, computed, onMounted } from 'vue'
import axios from '@/utils/axios'

const STATIC = import.meta.env.VITE_STATIC_URL || 'https://localhost:5002'
const selectedCategory = ref('всё')
const products = ref([])
const categories = ref(['всё', 'аура', 'фон', 'спутник', 'эссенция', 'аксессуар'])

const filteredProducts = computed(() => {
  if (selectedCategory.value === 'всё') return products.value
  return products.value.filter(
    (p) =>
      p.custom?.slot === selectedCategory.value ||
      p.slot === selectedCategory.value
  )
})

async function fetchVipProducts() {
  try {
    const { data } = await axios.get('/vip-shop', { withCredentials: true })
    products.value = data.products || []
  } catch (err) {
    console.error('❌ Ошибка загрузки VIP-магазина:', err)
  }
}

function selectCategory(cat) {
  selectedCategory.value = cat
}

onMounted(() => {
  fetchVipProducts()
})
</script>

<style scoped lang="scss">
.vip-shop-container {
  display: flex;
  gap: 20px;
  padding: 20px;
  font-family: 'Fira Code', monospace;
}

.shop-sidebar {
  flex: 0 0 200px;
  background-color: rgba(0, 0, 0, 0.35);
  border: 1px solid rgba(255, 255, 255, 0.08);
  border-radius: 12px;
  backdrop-filter: blur(6px);
  box-shadow: 0 0 15px rgba(0, 0, 0, 0.4);
  padding: 15px;

  .category {
    padding: 10px;
    margin-bottom: 8px;
    border-radius: 8px;
    cursor: pointer;
    transition: background 0.2s ease;

    &:hover {
      background: rgba(255, 255, 255, 0.06);
    }

    &.active {
      background: rgba(255, 255, 255, 0.1);
    }
  }
}

.shop-main {
  flex: 1;
  background-color: rgba(255, 255, 255, 0.04);
  border: 1px solid rgba(255, 255, 255, 0.08);
  border-radius: 12px;
  backdrop-filter: blur(6px);
  box-shadow: 0 0 15px rgba(0, 0, 0, 0.4);
  padding: 20px;

  .products-grid {
    display: grid;
    grid-template-columns: repeat(auto-fill, minmax(130px, 1fr));
    gap: 18px;

    .product-card {
      background: rgba(0, 0, 0, 0.25);
      border: 1px solid rgba(255, 255, 255, 0.06);
      border-radius: 10px;
      padding: 10px;
      text-align: center;
      transition: transform 0.2s;

      img {
        max-width: 100%;
        border-radius: 6px;
      }

      h3 {
        margin: 8px 0 4px;
        font-size: 14px;
      }

      .price {
        font-size: 12px;
        color: #95e5ff;
      }

      &:hover {
        transform: scale(1.03);
      }
    }
  }
}
</style>
