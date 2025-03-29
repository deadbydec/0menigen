<script setup>
import { useRouter } from "vue-router";

const router = useRouter();

// Список магазинов (можно потом заменить на API-запрос)
const shops = [
  { name: "Продуктовый", category: "food" },
  { name: "Товары для дома", category: "home" },
  { name: "Одежда и аксессуары", category: "clothes" },
  { name: "Техномагазин", category: "tech" },
  { name: "Магазин артефактов", category: "artifacts" },
  { name: "Коллекционер", category: "collectioner" }
];

const enterShop = (route) => {
  router.push(route);
};
</script>

<template>
  <div class="mall-container">
    <h1>Торговый центр</h1>
    <div class="shop-grid">
      <router-link v-for="shop in shops" 
                   :key="shop.category" 
                   :to="'/mall/' + shop.category" 
                   class="shop-card">
        <h2>{{ shop.name }}</h2>
      </router-link>
    </div>
  </div>
</template>
  
  <style scoped>
  .mall-container {
    text-align: center;
    padding: 20px;
  }
  
  .shop-grid {
    display: grid;
    grid-template-columns: repeat(2, 1fr); /* 2 магазина в ряду */
    gap: 20px;
    margin-top: 20px;
 /* Добавляем скролл */
    max-height: 80vh; /* Ограничиваем максимальную высоту для скролла */
  }
  
  .shop-card {
    background: #f5f5f5;
    padding: 15px;
    border-radius: 10px;
    cursor: pointer;
    transition: 0.3s;
    display: flex;
    flex-direction: column;
    align-items: center;
    box-shadow: 0 4px 8px rgba(0, 0, 0, 0.1);
  }
  
  .shop-card:hover {
    transform: scale(1.05);
  }
  
  .shop-card img {
    width: 100px;
    height: 100px;
    object-fit: cover;
    border-radius: 5px;
  }
  
  .shop-card h2 {
    margin-top: 10px;
    font-size: 1.2rem;
    color: #333;
  }
  </style>
