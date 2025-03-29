<script setup>
import { onMounted } from "vue";
import { useNewsStore } from "@/store/news";

const newsStore = useNewsStore();

onMounted(() => {
  newsStore.fetchNews(); // ✅ Загружаем новости при загрузке страницы
});
</script>

<template>
  <div class="news">
    

    <!-- 🔍 Фильтр категорий -->
    <div class="news-filter">
      <button v-for="category in newsStore.categories" 
              :key="category"
              :class="{ active: category === newsStore.selectedCategory }"
              @click="newsStore.fetchNews(category)">
        {{ category }}
      </button>
    </div>

    <!-- 📜 Лента новостей -->
    <div class="news-feed">
      <div v-if="newsStore.filteredNews.length === 0" class="no-news">
        😢 Новостей в этой категории пока нет...
      </div>

      <div class="news-item" v-for="news in newsStore.sortedNews" :key="news.id">
        <h3>{{ news.title }}</h3>
        <p>{{ news.content }}</p>
        <span class="date">{{ news.date }}</span>

        <!-- 🔥 Лайки, обсуждения -->
        <div class="news-actions">
          <button @click="newsStore.likeNews(news.id)">🔥 {{ news.likes }}</button>
          <button @click="newsStore.toggleComments(news.id)">💬 {{ news.comments.length }}</button>
        </div>

        <!-- 💬 Блок комментариев -->
        <div v-if="newsStore.activeComments === news.id" class="comments">
          <div v-for="(comment, index) in news.comments" :key="index" class="comment">
            <strong>{{ comment.author }}</strong>: {{ comment.text }}
          </div>
          <input v-model="newsStore.newComment" placeholder="Оставить комментарий..." 
                 @keyup.enter="newsStore.addComment(news.id)" />
        </div>
      </div>
    </div>
  </div>
</template>


  
<style lang="scss">
@import url('https://fonts.googleapis.com/css2?family=Orbitron:wght@400;700&display=swap');

.news {
  text-align: center;
  padding: 50px;
  background: transparent;
  border-radius: 10px;

  min-height: 100vh;
  display: flex;
  flex-direction: column;
  justify-content: flex-start;
}

/* 🔍 Категории */
.news-filter {
  display: flex;
  flex-wrap: nowrap;
  justify-content: center;
  gap: 10px;

  position: fixed; /* ✅ Теперь всегда поверх */
  top: 50px;
  left: 51.7%;
  transform: translateX(-50%);
  z-index: 200; /* ✅ Чтобы оставалось ПОВЕРХ новостей */
  padding: 25px;
  border-radius: 10px;
  width: 45%; /* ✅ Чтобы не раздувалось на весь экран */

  button {
    padding: 10px 15px;
    border: none;
    border-radius: 5px;
    cursor: pointer;
    background: rgba(0, 0, 0, 0.575);
    color: white;
    transition: 0.3s;
    box-shadow: 0 4px 6px rgba(0, 0, 0, 0.651);

    &:hover {
      background: transparent;
    }
  }

  .active {
    background: rgb(153, 12, 235);
    color: white;
  }
}

/* 📜 Лента новостей */
.news-feed {
  width: 800px; /* ✅ Теперь фиксированная ширина, не будет сжиматься */
  margin: auto;
  padding-top: 550px;
  padding-bottom: 150px; /* 🔥 Даем запас снизу, чтобы комменты влезали */
   /* 🔥 Если контейнер переполнен, пусть нормально скроллится */
}

/* 🔥 Новости */
.news-item {
  background: rgba(0, 0, 0, 0.555);
  padding: 20px;
  border-radius: 10px;
  margin-bottom: 20px;
  box-shadow: 0 4px 6px rgba(0, 0, 0, 0.651);
  color: white;
  text-align: left;
  width: 100%; /* ✅ Фиксируем ширину */
  min-height: 150px; /* ✅ Фиксируем высоту */
  display: flex;
  flex-direction: column;
  justify-content: space-between;
}

/* 🔥 Дата */
.date {
  font-size: 12px;
  color: rgba(200, 200, 200, 0.6);
}

/* 🔥 Лайки и комменты */
.news-actions {
  display: flex;
  gap: 10px;
  margin-top: 10px;

  button {
    background: transparent;
    border: none;
    cursor: pointer;
    font-size: 14px;
    color: white;

    &:hover {
      color: rgb(153, 0, 255);
    }
  }
}

/* 💬 Комментарии */
.comments {
  background: rgba(0, 0, 0, 0.486);
  padding: 10px;
  border-radius: 5px;
  margin-top: 10px;
  color: white;
  max-height: 300px; /* 🔥 Ограничиваем высоту */
  overflow-y: auto; /* 🔥 Включаем вертикальный скролл только внутри */
  scrollbar-color: rgba(200, 200, 200, 0.5) transparent; /* 🔥 Скрываем скроллбар, но оставляем его */
  overflow-x: hidden;
}

.comment {
  font-size: 14px;
  margin-bottom: 5px;
  padding: 8px;
  background: rgba(255, 255, 255, 0.1);
  border-radius: 5px;
}

/* 🔥 Стилизация скроллбара */
.comments::-webkit-scrollbar {
  width: 6px;
}

.comments::-webkit-scrollbar-thumb {
  background: rgba(200, 200, 200, 0.5);
  border-radius: 3px;
}

.comments::-webkit-scrollbar-track {
  background: transparent;
}
.comments input {
  width: 100%;
  padding: 5px;
  border-radius: 5px;
  background: rgba(0, 0, 0, 0.8);
  color: white;
  border: 1px solid rgba(200, 200, 200, 0.3);
}


</style>
  
  
  