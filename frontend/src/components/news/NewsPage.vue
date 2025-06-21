<script setup>
import { onMounted } from "vue";
import { useNewsStore } from "@/store/news";

const newsStore = useNewsStore();

onMounted(() => {
  newsStore.fetchNews(); // ✅ Загружаем новости при загрузке страницы
});
</script>

<template>
  <div class="news-wrapper">
    <!-- 🔍 Боковая панель — СБОРКА СБОКУ -->
    <div class="news-filter">
      <button v-for="category in newsStore.categories" 
              :key="category"
              :class="{ active: category === newsStore.selectedCategory }"
              @click="newsStore.fetchNews(category)">
        {{ category }}
      </button>
    </div>

    <!-- 📜 Лента новостей — СТРОГО ПО ЦЕНТРУ ЭКРАНА -->
    <div class="news-feed">
      <div v-if="newsStore.filteredNews.length === 0" class="no-news">
        😢 Новостей в этой категории пока нет...
      </div>

      <div class="news-item" v-for="news in newsStore.sortedNews" :key="news.id">
        <h3>{{ news.title }}</h3>
        <span class="date">{{ news.date }}</span>
        <div class="news-content">
  <p v-for="line in news.content.split('\n')" :key="line">{{ line }}</p>
</div>

        

        <div class="news-actions">
          <button @click="newsStore.likeNews(news.id)">🔥 {{ news.likes }}</button>
          <button @click="newsStore.toggleComments(news.id)">💬 {{ news.comments.length }}</button>
        </div>

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

html, body {
  scroll-behavior: smooth;
  margin: 0;
  padding: 0;
  background: #000; // если надо
  overflow-x: hidden;
}

.news-layout {
  display: flex;
  gap: 40px;
  max-width: 1280px;
  width: 100%;
  align-items: flex-start;
}

.news-wrapper {
  display: flex;
  justify-content: center;
  padding: 150px 20px 80px;
}

/* 📜 Центрированная лента новостей */
.news-feed {
  width: 800px;
  padding-bottom: 150px;
  z-index: 1;
}

/* 🔍 Фильтры сбоку слева от новостей */
.news-filter {
  position: absolute;
  left: calc(50% - 800px / 2 - 220px); // ← левее центра на ширину новостей + отступ
  display: flex;
  flex-direction: column;
  position: fixed;
  top: 150px;
  z-index: 1000;
  gap: 10px;
  width: 350px;
  border-radius: 18px;

  button {
    padding: 10px 15px;
    border: 1px solid rgb(187, 187, 187);
    border-radius: 11px;
    cursor: pointer;
    background: #181818e0;
    color: white;
    transition: 0.3s;
  }

  .active {
    background:linear-gradient(50deg, rgb(24, 24, 24), rgb(2, 85, 81),rgb(5, 235, 196));
    color: white;
  }
}

/* 🧱 Элементы новостей */
.news-item {
  background: #181818e7;
  padding: 20px;
  border-radius: 18px;
  border: 1px solid rgb(196, 196, 196);
  margin-bottom: 20px;
  color: white;
  text-align: left;
  width: 100%;
  min-height: 150px;
  display: flex;
  flex-direction: column;
  justify-content: space-between;
}

.date {
  font-size: 12px;
  color: rgba(200, 200, 200, 0.6);
}

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

.comments {
  background: rgba(0, 0, 0, 0.486);
  padding: 10px;
  border-radius: 5px;
  margin-top: 10px;
  color: white;
  max-height: 300px;
  overflow-y: auto;
  overflow-x: hidden;
  scrollbar-color: rgba(200, 200, 200, 0.5) transparent;
}

.comment {
  font-size: 14px;
  margin-bottom: 5px;
  padding: 8px;
  background: rgba(255, 255, 255, 0.1);
  border-radius: 5px;
}

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
  
  
  