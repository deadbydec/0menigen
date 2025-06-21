<template>
  <div class="mall-container">
    <!-- Вертикальный список с прокруткой -->
    <div class="shop-list">
      <!-- Генерация карточек событий -->
      <router-link
        v-for="event in events"
        :key="event.category"
        :to="'/' + event.category"
        class="shop-card"
      >
        <img :src="event.img" :alt="event.name" class="card-img" />
        <div class="card-content">
          <h2 class="card-title">{{ event.name }}</h2>
          <p class="card-description">{{ event.description }}</p>
        </div>
      </router-link>
    </div>
  </div>
</template>

<script setup>
import { useRouter } from 'vue-router'

const events = [
  {
    name: 'Свалка',
    category: 'landfill',
    img: new URL('@/assets/Landfill.jpg', import.meta.url),
    description: 'Отходы жизни и выброшенные мечты – здесь хаос правит балом.'
  },
  {
    name: 'Чёрный рынок',
    category: 'black-market',
    img: new URL('@/assets/BlackMarket.jpg', import.meta.url),
    description: 'Тайные сделки и тёмные фишки для тех, кто идёт против системы.'
  },
  {
    name: 'Портал в бездну',
    category: 'void-gate',
    img: new URL('@/assets/VoidPortal.jpg', import.meta.url),
    description: 'Погрузись в бездну, где логика отдыхает, а хаос витает в воздухе.'
  }
]

const router = useRouter()

const enterEvent = (route) => {
  router.push(route)
}
</script>

<style scoped>
.mall-container {
  text-align: center;
  padding: 20px;
}

/* Вертикальный список событий */
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

/* Картинка */
.card-img {
  width: 100%;
  height: 180px;  /* Высота изображения */
  object-fit: cover;
  display: block;
  border-radius: 0.5rem;
}

/* Контейнер под текст */
.card-content {
  margin-top: 1rem;
}

.card-title {
  font-size: 1.25rem;
  font-weight: bold;
  margin-bottom: 0.5rem;
}

.card-description {
  color: #cfcfcf;
}
</style>

  
  
  