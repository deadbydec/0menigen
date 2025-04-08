<template>
  <div class="shop-page">
    <h1>Магазин: {{ category }}</h1>

    <div class="shop-grid" :class="{ pulse: wasUpdated }">
      <template v-if="filteredShopItems.length">
        <div
          v-for="item in filteredShopItems"
          :key="item.id"
          class="shop-slot"
        >
          <img
            :src="`https://localhost:5002/static/goods/${item.image}`"
            :alt="item.name"
          />
          <div class="item-name">{{ item.name }}</div>
          <div class="item-rarity">{{ item.rarity }}</div>
          <div class="item-price">Цена: {{ item.price }} монет</div>
          <div class="item-stock">В наличии: {{ item.stock }}</div>
          <button
            @click="handleBuy(item.id, item.name, category)"
            class="buy-button"
            :disabled="item.stock <= 0"
          >
            Купить
          </button>

          <!-- Тултип всегда отрисовывается, но видимость через CSS -->
          <div class="product-tooltip">
            {{ item.description }}
          </div>
        </div>
      </template>

      <template v-else>
        <p>Товаров нет или идёт загрузка...</p>
      </template>
    </div>
  </div>
</template>



<script setup>
import { useRoute } from "vue-router";
import { ref, computed, onMounted, watch } from "vue";
import { useShopStore } from "@/store/shop";

const route = useRoute();
const category = route.params.category || "";

const shopStore = useShopStore();
const shopItems = computed(() => shopStore.shopItems);
const fetchShopItems = shopStore.fetchShopItems;
const wasUpdated = computed(() => shopStore.wasUpdated);

// ✅ Не переопределяй buyProduct, а вызывай напрямую из стора:
const handleBuy = (id, name, category) => {
  shopStore.buyProduct(id, name, category); // передаём id и текущую категорию
};

// Фильтрация
const allowedTypesMap = {
  food: ["еда", "напиток", "сладость"],
  books: ["книга"],
  collectioner: ["коллекционный", "сувенир", "игрушка", "наклейка"],
  drugs: ["аптека"],
  tech: ["гаджет"],
  toilet: ["туалет"]
};

const filteredShopItems = computed(() => {
  const allowedTypes = allowedTypesMap[category];
  if (allowedTypes?.length) {
    return shopItems.value.filter(item => allowedTypes.includes(item.product_type));
  }
  return shopItems.value;
});

onMounted(() => {
  fetchShopItems(category);
});

watch(shopItems, () => {
  console.log("📦 Товары изменились, возможно обновление!");
});
</script>



  
  <style scoped>
  /* Глобальные стили */
  html,
  body {
    height: 100%;
    display: flex;
    flex-direction: column;
  }
  
  .container {
    flex-grow: 1;
  }
  
  /* Сетка товаров */
  .shop-grid {
  display: grid;
  grid-template-columns: repeat(auto-fill, minmax(200px, 1fr));
  gap: 1rem;
  max-width: 1000px; /* например, чтобы максимум умещалось 5 */
}

  /* Ячейки магазина */
  .shop-slot {
  position: relative;
  display: flex;
  flex-direction: column;
  align-items: center;
  justify-content: space-between;
  width: 180px;
  height: 230px;
  padding: 10px;
  border: 1px solid #ccc;
  border-radius: 8px;
  background-color: #f9f9f9;
  transition: transform 0.2s, box-shadow 0.2s;
  text-align: center;
  overflow: hidden;
}
  
.shop-slot:hover {
  transform: scale(1.05);
  box-shadow: 0 4px 12px rgba(0, 0, 0, 0.2);
}
  
  /* Изображения товаров */
.shop-slot img {
  width: 80px;
  height: 80px;
  object-fit: contain;
}
  
  /* Название товара */
.item-name {
  word-wrap: break-word; /* Перенос слов */
  overflow-wrap: break-word;
  white-space: normal; /* Разрешаем многострочность */
  text-align: center; /* Центрируем текст */
  display: block;
  color: #333;
  font-weight: bold;
  font-size: 14px;
  max-width: 160px;
}
  
  /* Редкость товара */
  .item-rarity {
    font-size: 12px;
    color: #666;
  }
  
  /* Цена и количество */
  .item-price,
  .item-stock {
    font-size: 12px;
    color: #333;
  }
  
  /* Кнопка покупки */
  .buy-button {
    padding: 5px 12px;
    background-color: #28a745;
    color: white;
    border: none;
    border-radius: 20px;
    cursor: pointer;
    font-size: 14px;
    transition: background-color 0.3s ease;
    width: 100%;
  }
  
  .buy-button:hover {
    background-color: #218838;
  }
  
  .buy-button:disabled {
    background-color: #ccc;
    cursor: not-allowed;
  }
  
  /* Анимация fade-in/fade-out, если нужна */
  .fade-out {
    animation: fadeOut 0.5s;
  }
  .fade-in {
    animation: fadeIn 0.5s;
  }

  /* Тултип – скрыт по умолчанию, показывается при наведении */
.product-tooltip {
  position: absolute;
  bottom: 110%;
  left: 50%;
  transform: translateX(-50%);
  width: 200px;
  background: rgba(0, 0, 0, 0.8);
  color: white;
  padding: 10px;
  border-radius: 8px;
  text-align: center;
  font-size: 14px;
  opacity: 0;
  transition: opacity 0.3s ease-in-out;
  pointer-events: none;
  z-index: 10;
}

.shop-slot:hover .product-tooltip {
  opacity: 1;
}
  
  @keyframes fadeOut {
    from {
      opacity: 1;
    }
    to {
      opacity: 0;
    }
  }
  
  @keyframes fadeIn {
    from {
      opacity: 0;
    }
    to {
      opacity: 1;
    }
  }

  .pulse {
  animation: pulse 0.6s ease-in-out;
}

@keyframes pulse {
  0% { transform: scale(1); }
  50% { transform: scale(1.02); }
  100% { transform: scale(1); }
}
  </style>
  
