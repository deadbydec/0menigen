<template>
  <div class="shop-page">
    <h1>Магазин: {{ category }}</h1>
    <div class="shop-grid" v-if="shopItems && shopItems.length">
      <div v-for="item in filteredShopItems" :key="item.id" class="shop-slot">
        <img :src="`/static/goods/${item.image}`" :alt="item.name" />
        <div class="item-name">{{ item.name }}</div>
        <div class="item-rarity">{{ item.rarity }}</div>
        <div class="item-price">Цена: {{ item.price }} монет</div>
        <div class="item-stock">В наличии: {{ item.stock }}</div>
        <button @click="buyProduct(item.id)" class="buy-button" :disabled="item.stock <= 0">
          Купить
        </button>
        <!-- Тултип всегда отрисовывается, но его видимость контролируется CSS -->
        <div class="product-tooltip">
          {{ item.description }}
        </div>
      </div>
    </div>
    <div v-else>
      <p>Товаров нет или идет загрузка...</p>
    </div>
  </div>
</template>


<script setup>
import { computed, onMounted } from "vue";
import { useRoute } from "vue-router";
import { useShopStore } from "@/store/shop"; // Путь к твоему стору

const route = useRoute();
const category = route.params.category || "";

const shopStore = useShopStore();
const shopItems = shopStore.shopItems;
const fetchShopItems = shopStore.fetchShopItems;
const buyProduct = shopStore.buyProduct;

// Определяем набор допустимых типов для каждой категории
const allowedTypesMap = {
  "продуктовый": ["еда", "напитки", "сладости"],
  "одежда": ["clothes", "accessories"],
  // Добавь другие категории и соответствующие типы
};

// Вычисляемый массив отфильтрованных товаров
const filteredShopItems = computed(() => {
  const allowedTypes = allowedTypesMap[category];
  if (allowedTypes && allowedTypes.length) {
    return shopItems.value.filter(item => allowedTypes.includes(item.product_type));
  }
  // Если категория не описана – возвращаем всё
  return shopItems.value;
});

// Загружаем товары при монтировании
onMounted(() => {
  fetchShopItems(category);
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
  </style>
  
