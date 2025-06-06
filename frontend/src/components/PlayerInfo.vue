<template>
  <div v-if="player && !['/profile', '/wardrobe'].includes($route.path)" class="player-info">
    
    
    
    
    <div class="content">
      <!-- Контейнер с кольцом опыта и аватаркой -->
      <div class="avatar-progress-container">
        <svg class="xp-ring" viewBox="0 0 140 140">
          <circle class="bg" cx="70" cy="70" r="64" />
          <circle
            class="fg"
            cx="70" cy="70" r="64"
            :stroke-dasharray="circumference"
            :stroke-dashoffset="xpOffset"
          />
        </svg>
      
      
      
      
      
      <img :src="computedAvatar" alt="Avatar" class="avatar" />
      </div>
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

// Параметры кольца опыта
const radius = 64;
const circumference = 2 * Math.PI * radius;

const xpPercent = computed(() => {
  if (!player.value) return 0;
  return (player.value.xp / player.value.nextLevelXp) * 100;
});

const xpOffset = computed(() => {
  return circumference - (circumference * xpPercent.value) / 100;
});





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


  
<style lang="scss" scoped>
.player-info {
  position: fixed;
  top: 120px;
  right: 130px;
  width: 240px;
  background:rgba(38, 32, 39, 0.842);
  border-radius: 14px;
  border: 1px solid rgb(0, 0, 0);
  padding: 15px;
  display: flex;
  flex-direction: column;
  align-items: center;
  box-shadow: 0 4px 10px rgba(0, 0, 0, 0.3);
  overflow: hidden;
  font-family: 'JetBrains Mono', monospace;
}

.content {
  display: flex;
  align-items: center;
  width: 100%;
  padding-top: 10px;
}

/* Контейнер под кольцо и аватар */
.avatar-progress-container {
  position: relative;
  width: 110px;
  height: 110px;
  margin: 0 auto 11px;
  flex-shrink: 0; /* чтобы не сжимался */
}

/* Кольцо */
.xp-ring {
  position: absolute;
  top: -26px;
  left: -26px;
  /* Масштабируем с 140×140 до 110×110 => ~0.7857 */
  width: 161px;
  height: 161px;
  transform: rotate(-90deg) scale(0.79);
  transform-origin: center;
  z-index: 2;
  
}

.xp-ring .bg {
  fill: none;
  stroke: rgba(48, 40, 53, 0.644);
  stroke-width: 8;
}

.xp-ring .fg {
  fill: none;
  stroke: rgba(18, 230, 184, 0.61);
  stroke-width: 8;
  stroke-linecap: round;
  transition: stroke-dashoffset 0.4s ease;
}

/* Аватарка */
.avatar {
  position: absolute;
  top: 0;
  left: 0;
  width: 110px;
  height: 110px;
  border-radius: 50%;
  object-fit: cover;
  z-index: 1;

}

/* Инфа справа от аватарки */
.info {
  color: #fff;
  font-size: 17px;
  margin-left: 12px;
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
  