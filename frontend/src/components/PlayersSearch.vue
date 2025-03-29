<script setup>
import { ref, onMounted, watch } from "vue";
import api from "@/utils/axios";

const players = ref([]);
const searchQuery = ref("");
const filter = ref("all"); // "all" или "online"
const loading = ref(false); // ✅ ФИКС: Добавили `loading`

async function fetchPlayers() {
  loading.value = true; // ✅ Включаем индикатор загрузки
  try {
    console.log("🔄 Запрос списка игроков...");
    const response = await api.get(`/players/?filter=${filter.value}&search=${searchQuery.value}`);
    players.value = response.data;
    console.log("✅ Полученные игроки:", players.value);
  } catch (error) {
    console.error("❌ Ошибка загрузки списка игроков:", error);
  } finally {
    loading.value = false; // ✅ Выключаем загрузку
  }
}

onMounted(fetchPlayers); // ✅ Загружаем при открытии

function getAvatarUrl(avatarPath) {
  if (!avatarPath) {
    return "https://localhost:5002/api/profile/avatars/default_avatar.png";
  }
  return `https://localhost:5002${avatarPath}?t=${Date.now()}`;
}

// ✅ Обновляем список при изменении фильтра или строки поиска
watch([searchQuery, filter], fetchPlayers);
</script>

<template>
  <div class="players-container">
    <h2>🔍 Поиск игроков</h2>

    <div class="search-bar">
      <input v-model="searchQuery" placeholder="Введите ник..." />
      <select v-model="filter">
        <option value="all">Все</option>
        <option value="online">Только онлайн</option>
      </select>
    </div>

    <div v-if="loading" class="loading">Загрузка...</div>

    <ul v-else class="players-list">
      <li v-for="player in players" :key="player.id" class="player-card">
        <img :src="getAvatarUrl(player.avatar)" class="avatar" />
        <div>
          <h3 class="username"><router-link :to="`/profile/${player.id}`">{{ player.username }}</router-link></h3>
          <span :class="{ online: player.status === 'online', offline: player.status === 'offline' }">
            {{ player.status === "online" ? "🟢 Онлайн" : "🔴 Офлайн" }}
          </span>
        </div>
      </li>
    </ul>

    <div v-if="players.length === 0 && !loading" class="no-results">
      Никого не найдено...
    </div>
  </div>
</template>

<style scoped>


.players-container {
  background: rgba(0, 0, 0, 0.623);
  padding: 15px;
  border-radius: 10px;
  box-shadow: 0 2px 5px rgba(0, 0, 0, 0.1);
}

.search-bar {
  display: flex;
  gap: 10px;
  margin-bottom: 15px;
}

.search-bar input, .search-bar select {
  padding: 8px;
  font-size: 16px;
  border-radius: 5px;
  border: none;
}

.players-list {
  list-style: none;
  padding: 0;
}

.player-card {
  display: flex;
  align-items: center;
  gap: 10px;
  padding: 10px;

  border-radius: 5px;
  margin-bottom: 10px;
}

.player-card img {
  width: 90px;
  height: 90px;
  border-radius: 50%;
  object-fit: cover;
}

.username {
  color: bisque;

}

.online {
  color: rgb(79, 238, 79);
}

.offline {
  color: rgb(88, 88, 88);
}

.loading, .no-results {
  text-align: center;
  margin-top: 20px;
}
</style>
