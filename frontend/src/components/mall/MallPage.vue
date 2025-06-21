<template>
  <div class="mall-container">
    <!-- Убираем ограничение по высоте на shop-list, прокрутка будет по всей странице -->
    <div class="shop-list">
      <!-- Генерируем карточки магазинов -->
      <router-link
        v-for="shop in shops"
        :key="shop.category"
        :to="'/mall/' + shop.category"
        class="shop-card"
      >
        <img :src="shop.img" :alt="shop.name" class="card-img" />
        <div class="card-content">
          <h2 class="card-title">{{ shop.name }}</h2>
          <p class="card-description">{{ shop.description }}</p>
        </div>
      </router-link>
    </div>
  </div>
</template>

<script setup>
import { useRouter } from 'vue-router'

const shops = [
  {
    name: 'Продуктовый',
    category: 'food',
    img: new URL('@/assets/FoodShop.jpg', import.meta.url),
    description: 'Свежие продукты, без просрочки (наверное).'
  },
  {
    name: '✨Ко$мошоп™',
    category: 'cosmetic',
    img: new URL('@/assets/CosmoShop.jpg', import.meta.url),
    description: 'Стиль вне координат. Надень баг — почувствуй космос.'
  },
  {
    name: 'Книжник',
    category: 'books',
    img: new URL('@/assets/BookShop.jpg', import.meta.url),
    description: 'Книги, свитки и древние фолианты для любителей знаний.'
  },
  {
    name: 'Вивариум',
    category: 'zoo',
    img: new URL('@/assets/ZooShop.jpg', import.meta.url),
    description: 'Твоя плоть не в безопасности. Она уже заинтересовала кое-кого. Выбери себе нового спутника. Он выберет тебя раньше.'
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

const enterShop = (route) => {
  router.push(route)
}
</script>

<style lang="scss">
.mall-container {
  text-align: center;
  padding: 20px;
}

/* Вертикальный список магазинов */
.shop-list {
  display: flex;
  flex-direction: column;   /* Карточки идут в столбик */
  gap: 20px;
  margin-top: 100px;
  padding-right: 15px;  /* Для прокрутки с правой стороны */
  padding-bottom: 50px; /* Чтобы нижние карточки не скрывались */
}

/* Оформление карточек */
.shop-card {
  width: 100%;
  border: 1px solid rgb(196, 196, 196);
  background: #181818e7;
  padding: 1.5rem;
  border-radius: 20px;
  text-align: center;
  transition: transform 0.2s ease, box-shadow 0.2s ease;
  text-decoration: none;
  color: #fff;
  height: 290px; /* Зафиксированная высота карточки */
  max-width: 500px;
  margin: 0 auto;
}

.shop-card:hover {
  transform: translateY(-5px);
}

.card-img {
  width: 100%;
  height: 180px;  /* Высота изображения */
  object-fit: cover;
  display: block;
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






