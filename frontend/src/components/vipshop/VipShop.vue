<template>
  <div class="wrap">
  <div class="vip-shop-layout">
    <!-- Левая панель с баннером -->
    <div class="vip-sidebar">
      <img :src="bannerLeft" alt="баннер" class="sidebar-banner" />
    </div>

    <!-- Контент магазина -->
    <div class="vip-main">
      <!-- Верхний баннер -->
      <div class="top-banner">
        <img :src="bannerTop" alt="баннер" class="top-banner-img" />

      </div>

      <!-- Вкладки -->
      <div class="tab-bar">
        <div
          v-for="tab in tabs"
          :key="tab"
          :class="['tab', { active: selectedTab === tab }]"
          @click="selectedTab = tab"
        >
          {{ tab }}
        </div>
      </div>

      <!-- Сетка с товарами -->
      <div class="product-grid">
        <div
          v-for="product in filteredProducts"
          :key="product.id"
          class="product-card"
        >
          <img :src="`${STATIC}/static/goods/${product.image}`" alt="product" />
          <h4>{{ product.name }}</h4>
          <p class="price">{{ product.nulling_price }} 🧿</p>
        </div>
      </div>
    </div>
  </div></div>
</template>

<script setup>
import { ref, computed, onMounted } from 'vue'
import bannerLeft from '@/assets/vip-bar.jpg'
import bannerTop from '@/assets/vip-shop.jpg'
import { useVipShopStore } from "@/store/vipshop"

const STATIC = import.meta.env.VITE_STATIC_URL || 'https://localhost:5002'

const tabs = ['наборы', 'артефакты', 'спутники', 'фоны', 'привилегии', 'прочее']
const selectedTab = ref(tabs[0])

const vipStore = useVipShopStore()
const products = computed(() => vipStore.vipItems)

onMounted(() => {
  vipStore.fetchVipItems()
})

// 💎 маппинг вкладок на типы
const tabToTypes = {
  "наборы": ["bundle"],
  "артефакты": ["artifact"],
  "спутники": ["companion"],
  "фоны": ["background", "cosmetic"],
  "привилегии": ["privilege"],
  "прочее": ["book", "toy", "souvenir", "coupon", "misc", "unknown"]
}

const filteredProducts = computed(() => {
  const tab = selectedTab.value
  const allowedTypes = tabToTypes[tab] || []
  return products.value.filter(p => {
    const mainType = p.product_type
    const altTypes = p.types || []
    return allowedTypes.includes(mainType) || altTypes.some(t => allowedTypes.includes(t))
  })
})
</script>


<style scoped>
.wrap {
  margin-top: 150px;
}

.vip-shop-layout {
  
  display: flex;
  background: #181818e7;
  gap: 20px;
  padding: 20px;
  font-family: 'Fira Code', monospace;
  max-width: 1200px;
  margin: 0 auto;
}

.vip-sidebar {
  width: 300px;
}

.sidebar-banner {
  width: 300px;
  height: 700px;
  border-radius: 30px;
  object-fit: cover;
}

.vip-main {
  flex: 1;
  display: flex;
  flex-direction: column;
}

.top-banner {
  margin-bottom: 12px;
}

.top-banner {
  width: 800px;
  height: 250px;
  border-radius: 30px;
  
}

.top-banner-img {
  width: 100%;
  height: 100%;
  object-fit: cover; /* растягиваем красиво без сплющивания */
  border-radius: 30px; /* дублируем для верности, но можно убрать */
}

.tab-bar {
  display: flex;
  margin-bottom: 20px;
  border-bottom: 2px solid rgba(255,255,255,0.1);
}

.tab {
  padding: 10px 18px;
  margin-right: 4px;
  border-top-left-radius: 6px;
  border-top-right-radius: 6px;
  background: #202020;
  cursor: pointer;
  border: 1px solid rgba(255,255,255,0.08);
  border-bottom: none;
  transition: 0.2s ease;
  font-weight: 600;
  user-select: none;
}

.tab.active {
  background: #2c2c2c;
  border-bottom: 2px solid #2c2c2c;
  color: #95e5ff;
}

.product-grid {
  background: #181818e7;
  display: grid;
  grid-template-columns: repeat(auto-fill, minmax(140px, 1fr));
  gap: 16px;
}

.product-card {
  background: #1b1b1b;
  border: 1px solid rgba(255,255,255,0.08);
  border-radius: 8px;
  padding: 10px;
  text-align: center;
  transition: 0.2s ease;
}

.product-card:hover {
  transform: scale(1.03);
  box-shadow: 0 0 10px rgba(0,0,0,0.4);
}

.product-card img {
  max-width: 100%;
  border-radius: 6px;
}

.product-card h4 {
  margin: 6px 0 4px;
  font-size: 14px;
}

.price {
  font-size: 12px;
  color: #95e5ff;
}
</style>


