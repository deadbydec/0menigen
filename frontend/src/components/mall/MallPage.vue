<script setup>
import { useRouter } from 'vue-router'

// Можешь хранить пути к локальным картинкам в папке assets,
// тогда добавляй их так: new URL('@/assets/food-shop.jpg', import.meta.url)
const shops = [
  {
    name: 'Продуктовый',
    category: 'food',
    img: new URL('@/assets/FoodShop.jpg', import.meta.url),
    description: 'Свежие продукты, без просрочки (наверное).'
  },
  {
    name: 'Книжник',
    category: 'books',
    img: new URL('@/assets/BookShop.jpg', import.meta.url),
    description: 'Книги, свитки и древние фолианты для любителей знаний.'
  },
  {
    name: 'Слив',
    category: 'toilet',
    img: new URL('@/assets/toiletshop.jpg', import.meta.url),
    description: 'От рулонов с философскими цитатами до артефактов для личного туалетного дзена.'
  },
  {
    name: 'Технолайт',
    category: 'tech',
    img: new URL('@/assets/techshop.jpg', import.meta.url),
    description: 'Гаджеты, механизмы и прочие железки для любителей прогресса.'
  },
  {
    name: 'Аптека',
    category: 'drugs',
    img: new URL('@/assets/drugsshop.jpg', import.meta.url),
    description: 'Таблетки, мази, шприцы, пилюли — всё, чтобы сбалансировать химозу твоей реальности.'
  },
  {
    name: 'Коллекционер',
    category: 'collectioner',
    img: new URL('@/assets/collectioner.jpg', import.meta.url),
    description: 'Для тех, кто собирает редкости и ценит уникальные экземпляры.'
  }
]

const router = useRouter()

// Функция, если нужно программно переходить в магазин (не обязательно)
const enterShop = (route) => {
  router.push(route)
}
</script>

<template>
  <div class="mall-container">
    <h1></h1>

    <div class="shop-grid">
      <!-- Генерируем карточки магазинов -->
      <router-link
        v-for="shop in shops"
        :key="shop.category"
        :to="'/mall/' + shop.category"
        class="shop-card"
      >
        <!-- Картинка магазина -->
        <img :src="shop.img" :alt="shop.name" class="card-img" />

        <!-- Контент карточки: заголовок + описание -->
        <div class="card-content">
          <h2 class="card-title">{{ shop.name }}</h2>
          <p class="card-description">{{ shop.description }}</p>
        </div>
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
  grid-template-columns: repeat(2, 1fr); /* 2 магазина в ряд */
  gap: 20px;
  margin-top: 20px;
  /* Скролл по желанию */

  overflow-y: auto;
}

/* Карточка в стиле EventsPage */
.shop-card {
  border: 1px solid rgb(0, 0, 0);
  display: block;
  background: #00000093;
  padding: 1.5rem;
  border-radius: 0.75rem;
  text-align: center;
  transition: transform 0.2s ease, box-shadow 0.2s ease;
  text-decoration: none;
  color: #fff; /* текст на тёмном фоне */
}

.shop-card:hover {
  transform: translateY(-5px);
  box-shadow: 0 10px 20px rgba(0, 0, 0, 0.5);
}

.card-img {
  width: 100%;
  height: 140px;
  object-fit: cover;
  border-radius: 0.5rem;
}

.card-content {
  margin-top: 1rem;
}

.card-title {
  font-size: 1.25rem;
  font-weight: bold;
  margin-bottom: 0.5rem;
}

.card-description {
  font-size: 0.9rem;
  color: #cfcfcf;
}
</style>

