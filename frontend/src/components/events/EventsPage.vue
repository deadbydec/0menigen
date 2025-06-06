<template>
  <div class="mall-container">
    <h1></h1>

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
  transform: scale(0.9);
  text-align: center;
  padding: 20px;
  height: 100vh; /* Устанавливаем 100% высоты экрана */
  overflow-y: scroll; /* Прокрутка по всей высоте экрана */
}

.mall-container::-webkit-scrollbar {
  width: 0px;  /* Прячем полосу прокрутки */
}

.mall-container::-webkit-scrollbar-thumb {
  background: transparent;  /* Оставляем полосу прокрутки полностью прозрачной */
}

/* Вертикальный список событий */
.shop-list {
  display: flex;
  flex-direction: column;   /* Карточки идут в столбик */
  gap: 20px;
  margin-top: 20px;
  padding-right: 15px;  /* Для прокрутки с правой стороны */
  padding-bottom: 20px; /* Чтобы нижние карточки не скрывались */
}

/* Оформление карточек */
.shop-card {
  width: 100%;
  border: 1px solid #000;
  background: #00000093;
  padding: 1.5rem;
  border-radius: 0.75rem;
  text-align: center;
  transition: transform 0.2s ease, box-shadow 0.2s ease;
  text-decoration: none;
  color: #fff;
  height: 290px; /* Зафиксированная высота карточки */
  max-width: 90%;
  margin: 0 auto;
}

.shop-card:hover {
  transform: translateY(-5px);
  box-shadow: 0 10px 20px rgba(0, 0, 0, 0.5);
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
  padding: 0rem 1.5rem 1.8rem;
  height: calc(100% - 180px); /* Учитываем высоту изображения */
  box-sizing: border-box;
}

.card-title {
  font-size: 1.75rem;
  font-weight: 500;
  margin-bottom: 0.9rem;
  color: #ffffff;
}

.card-description {
  color: #cfcfcf;
}
</style>

  
  
  