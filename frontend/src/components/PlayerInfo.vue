<template>
  <div v-if="player && $route.path !== '/profile'" class="player-info">
    <div class="level-border">
      <div class="progress" :style="{ width: `${xpPercent}%` }"></div>
    </div>
    <div class="content">
      <img :src="computedAvatar" alt="Avatar" class="avatar" />
      <div class="info">
        <h3 class="username">{{ player.name || 'Омежка' }}</h3>
        <p class="title">{{ player.usertype || 'Омежка' }}</p>
        <p class="coins">💰 {{ player.coins || 0 }} монет</p>
        <p class="nullings">🕳 {{ player.nullings !== undefined ? player.nullings : 0.0 }} нуллингов</p>
        <p class="level">Уровень {{ player.level || 1 }} ({{ player.xp || 0 }}/{{ player.nextLevelXp || 100 }})</p>
      </div>
    </div>
  </div>
</template>
  
  
  
<script setup>
import { computed, onMounted, watchEffect } from "vue";
import { usePlayerStore } from "@/store/player";
import { useAuthStore } from "@/store/auth";


const defaultAvatar = "https://localhost:5002/api/profile/avatars/default_avatar.png";
const playerStore = usePlayerStore();
const authStore = useAuthStore();

const isAuthenticated = computed(() => authStore.isAuthenticated);
const player = computed(() => playerStore.player);
const xpPercent = computed(() => playerStore.xpPercent);

// ✅ Динамическое обновление аватарки (избегаем кэша)
const computedAvatar = computed(() => {
  if (player.value?.avatar?.startsWith("/api/profile/avatars")) {
    return `https://localhost:5002${player.value.avatar}?t=${Date.now()}`;
  }
  return player.value?.avatar || defaultAvatar;
});


// 🔥 Убираем бесконечный ререндер
watchEffect(() => {
  if (isAuthenticated.value && !player.value) {
    playerStore.fetchPlayer();
  }
});

onMounted(() => {
  if (isAuthenticated.value) {
    playerStore.fetchPlayer();
  }
});
</script>


  
  <style lang="scss">
.player-info {
    position: fixed;
  ;
    top: 120px;
    right: 120px;
    width: 240px;
    background: rgba(0, 0, 0, 0.603);
    border-radius: 12px;
    padding: 15px;
    display: flex;
    flex-direction: column;
    align-items: center;
    box-shadow: 0 4px 10px rgba(0, 0, 0, 0.3);
    border: 0px solid rgba(255, 255, 255, 0.15);
    overflow: hidden; /* Чтобы прогресс-бар не выходил за границы */
    border-radius: 14px;
  }
  

  
  .progress {
    height: 100%;
    background: linear-gradient(90deg, #ffcc00, #ff8800);
    transition: width 0.3s ease-in-out;
  }
  
  .content {
    display: flex;
    align-items: center;
    width: 100%;
    padding-top: 10px;
  }
  
  .avatar {
    width: 110px;
    height: 110px;
    border-radius: 50%;
    margin-right: 12px;
    border: 2px solid rgba(255, 255, 255, 0.3);
  }
  
  .info {
    color: #fff;
    font-size: 17px;
  }
  
  .username {
    font-size: 18px;
    font-weight: bold;
    margin-bottom: 4px;
  }
  
  .title {
    font-size: 15px;
    color: rgba(204, 129, 247, 0.7);
  }
  
  .coins {
    font-size: 15px;
    margin-top: 5px;
  }
</style>
  