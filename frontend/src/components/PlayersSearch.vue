<script setup>
import { ref, onMounted, watch } from "vue";
import { useRouter } from "vue-router";
import { usePlayerStore } from "@/store/player";
import api from "@/utils/axios";

const router = useRouter();
const playerStore = usePlayerStore();

const players = ref([]);
const searchQuery = ref("");
const filter = ref("all");
const loading = ref(false);

// 🔄 Загрузка списка игроков
async function fetchPlayers() {
  loading.value = true;
  try {
    const response = await api.get(`/players/?filter=${filter.value}&search=${searchQuery.value}`);
    players.value = response.data;
  } catch (error) {
    console.error("❌ Ошибка загрузки списка игроков:", error);
  } finally {
    loading.value = false;
  }
}

// ⏳ Загружаем текущего игрока, если ещё не загружен
onMounted(async () => {
  if (!playerStore.player) {
    await playerStore.fetchPlayer();
  }
  await fetchPlayers();
});

// 📦 Получаем ссылку на аватар
function getAvatarUrl(avatarPath) {
  if (!avatarPath) {
    return "https://localhost:5002/api/profile/avatars/default_avatar.png";
  }
  return `https://localhost:5002${avatarPath}?t=${Date.now()}`;
}

// 🔁 Переход в профиль
function goToProfile(playerId) {
  if (playerStore.player?.id === playerId) {
    router.push("/profile");
  } else {
    router.push(`/profile/${playerId}`);
  }
}

// 🔍 Автопоиск
watch([searchQuery, filter], fetchPlayers);
</script>


<template>
  <div class="players-container">
    <h2>Поиск игроков</h2>

    <div class="search-bar">
      <input v-model="searchQuery" placeholder="Введите ник..." />
      <select v-model="filter">
        <option value="all">Все</option>
        <option value="online">Только онлайн</option>
      </select>
    </div>

    <div v-if="loading" class="loading">Загрузка...</div>

    <ul v-else class="players-list">
      <li
        v-for="player in players"
        :key="player.id"
        class="player-card"
        @click="goToProfile(player.id)"
      >
        <img :src="getAvatarUrl(player.avatar)" class="avatar" />
        <div class="card-content">
          <h3 class="username">{{ player.username }}</h3>
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

<style scoped lang="scss">
.players-container {
  border: 1px solid rgb(0, 0, 0);
  color: #fff;
  padding: 1rem;
  background-color: rgba(0, 0, 0, 0.4);  // полупрозрачный фон
  backdrop-filter: blur(6px);
  border-radius: 8px;
  max-width: 600px;
  margin: 0 auto;
  box-shadow: 0 0 15px rgba(0,0,0,0.4);

  h2 {
    margin-bottom: 1rem;
    font-size: 1.4rem;
    text-shadow: 0 1px 2px rgba(0,0,0,0.7);
  }

  .search-bar {
    display: flex;
    gap: 10px;
    margin-bottom: 15px;

    input, select {
      width: 100%;
      max-width: 200px;
      padding: 0.6rem;
      border: 1px solid rgba(255,255,255,0.2);
      background-color: rgba(255,255,255,0.1);
      color: #fff;
      border-radius: 4px;
      transition: border-color 0.2s ease;

      &:focus {
        outline: none;
        border-color: rgba(255,255,255,0.4);
        background-color: rgba(255,255,255,0.15);
      }
    }
  }

  .loading {
    text-align: center;
    margin-top: 20px;
  }

  .players-list {
    list-style: none;
    padding: 0;
    margin: 0;

    .player-card {
      display: flex;
      align-items: center;
      gap: 1rem;
      padding: 0.8rem;
      margin-bottom: 0.5rem;
      cursor: pointer;
      border: 1px solid rgba(255,255,255,0.3); // тонкий белый бордер
      border-radius: 6px;
      transition: background-color 0.2s ease, border-color 0.2s ease;

      &:hover {
        background-color: rgba(255,255,255,0.08);
        border-color: rgba(255,255,255,0.5);
      }

      .avatar {
        width: 60px;
        height: 60px;
        border-radius: 50%;
        object-fit: cover;
        border: 1px solid rgba(255,255,255,0.2);
        box-shadow: 0 0 4px rgba(0,0,0,0.5);
      }

      .card-content {
        display: flex;
        flex-direction: column;

        .username {
          font-size: 1rem;
          margin: 0 0 4px;
          white-space: nowrap;
        }
      }
    }
  }

  .online {
    color: #4fee4f;
  }

  .offline {
    color: rgb(88, 88, 88);
  }

  .no-results {
    text-align: center;
    margin-top: 20px;
    font-style: italic;
  }
}
</style>

