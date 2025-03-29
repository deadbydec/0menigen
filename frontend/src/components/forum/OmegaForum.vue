<template>
    <div class="forum-container">
      <h1>⚡ ОмегаФорум</h1>
  
      <!-- Главные темы -->
      <section class="main-topics">
        <h2>📢 Главные темы</h2>
        <div class="topic-list">
          <ForumThreadCard
            v-for="thread in mainThreads"
            :key="thread.id"
            :thread="thread"
            class="important-thread"
          />
        </div>
      </section>
  
      <!-- Популярные обсуждения -->
      <section class="popular-topics">
        <h2>🔥 Популярные обсуждения</h2>
        <div class="topic-list">
          <ForumThreadCard
            v-for="thread in popularThreads"
            :key="thread.id"
            :thread="thread"
          />
        </div>
      </section>
  
      <!-- Статистика форума -->
      <section class="forum-stats">
        <h2>📊 Статистика форума</h2>
        <p>Сообщений всего: <strong>{{ totalMessages }}</strong></p>
        <p>Активные участники: <strong>{{ activeUsers }}</strong></p>
      </section>
    </div>
  </template>
  
  <script setup>
  import { computed, onMounted } from "vue";
  import { useForumStore } from "@/store/forum.js";
  
  const forumStore = useForumStore();
  
  onMounted(() => {
    forumStore.fetchThreads();
  });
  
  // Фильтруем темы по категориям
  const mainThreads = computed(() => forumStore.threads.filter(t => t.category === "main"));
  const popularThreads = computed(() => forumStore.threads.filter(t => t.category === "popular"));
  
  const totalMessages = computed(() => forumStore.threads.reduce((acc, t) => acc + t.posts_count, 0));
  const activeUsers = computed(() => Math.floor(totalMessages.value / 5)); // Пример расчета
  </script>
  
  <style lang="scss" scoped>
.forum-container {
  max-width: 1100px;
  margin: auto;
  padding: 20px;
  background: rgba(0, 0, 0, 0.603);
  border-radius: 12px;
  box-shadow: 0 0 15px rgba(255, 0, 128, 0.2);

  h1, h2 {
    text-align: center;
    margin-bottom: 15px;
  }
}

// 🔹 Блоки тем
.topic-list {
  display: flex;
  flex-direction: column;
  gap: 10px;
  padding: 10px;
  background: #202020;
  border-radius: 8px;
  box-shadow: 0 0 10px rgba(0, 255, 255, 0.1);
}

// 🔹 Карточки тем
.thread-card {
  display: flex;
  flex-direction: column;
  padding: 15px;
  border-radius: 10px;
  background: #252525;
  color: #fff;
  text-decoration: none;
  transition: 0.2s;
  border: 1px solid rgba(255, 255, 255, 0.1);

  &:hover {
    background: #292929;
    transform: scale(1.02);
  }
}

// 🔹 Главные темы (яркий стиль)
.important-thread {
  background: linear-gradient(135deg, #ff007f, #ff6800);
  color: white;
  font-weight: bold;
  border: none;
}

// 🔹 Блок статистики
.forum-stats {
  margin-top: 20px;
  padding: 15px;
  background: #222;
  border-radius: 8px;
  box-shadow: 0 0 10px rgba(0, 255, 255, 0.15);
  text-align: center;

  p {
    font-size: 16px;
    color: #ddd;
    margin: 5px 0;
  }

  strong {
    color: #ff007f;
  }
}
</style>
  
  