<template>
  <div v-if="player && !['/profile', '/wardrobe'].includes($route.path)" class="player-info">
    <div class="content">
      <!-- Аватар с кольцом -->
      <div class="avatar-container">
        <svg :class="['xp-ring', { 'vip-ring': !!player.vip_subscription }]" viewBox="0 0 140 140">
          <defs>
            <linearGradient id="xp-gradient" x1="0%" y1="0%" x2="100%" y2="100%">
              <stop offset="0%" stop-color="#ffe600"/>
              <stop offset="50%" stop-color="#ffd000"/>
              <stop offset="100%" stop-color="#ff9900"/>
            </linearGradient>
          </defs>
          <circle class="bg" cx="70" cy="70" r="64" />
          <circle
            class="fg"
            cx="70" cy="70"
            r="64"
            :stroke-dasharray="circumference"
            :stroke-dashoffset="xpOffset"
            stroke="url(#xp-gradient)"
          />
        </svg>
        <img :src="computedAvatar" alt="Avatar" class="avatar" />
      </div>

      <!-- Инфа справа -->
      <div class="info">
        <div class="username">
          {{ player.name || 'Омежка' }}
          
          <span v-if="player.vip_subscription" class="vip-icon" :title="player.vip_subscription.label">✨</span>
          
        </div>
        <div class="title" :class="roleColor">{{ titleToShow }}</div>
        <div class="race">{{ player.race?.display_name || "Неизвестно" }}</div>
        
        <div class="money"><img :src="coinIcon" alt="💎" class="emoji-icon" /> {{ player.coins || 0 }}</div>
        <div class="money"><img :src="nullingIcon" alt="💎" class="emoji-icon" /> {{ (player.nullings ?? 0).toFixed(1) }}</div>
        <div class="money"><img :src="specialIcon" alt="💎" class="emoji-icon" /> {{ player.specialk || 0 }}</div>
        <div class="level">Уровень: {{ player.level }}</div>
        <div class="xp">({{ player.xp }}/{{ player.nextLevelXp }})</div>
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
import nullingIcon from "@/assets/icons/nulling1.png"; // второй кристалл
import coinIcon from "@/assets/icons/coin.png";
import specialIcon from "@/assets/icons/specialk.png";
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

const titleToShow = computed(() => {
  const role = player.value?.role
  if (role?.name === "ADMIN") return "Администратор"
  if (role?.name === "MODERATOR") return "Модератор"
  if (role?.name === "TESTER") return "Тестер"
  if (role?.name === "AI") return "ИИ"
  if (role?.name === "USER") return "Пользователь"

  const type = player.value?.usertype
  if (type === "OMEZKA") return "Омежка"
  if (type === "OMEGAKRUT") return "Омегакрут"
  if (type === "OMEGAN") return "Омеган"
  return ""
})

const roleColor = computed(() => {
  const role = player.value?.role?.name

  if (role === "ADMIN") return "admin-role"
  if (role === "MODERATOR") return "moderator-role"
  if (role === "TESTER") return "tester-role"
  if (role === "AI") return "ai-role"
  if (role === "USER") return "user-role"

  const type = player.value?.usertype
  if (type === "OMEGAKRUT") return "omegakrut-role"
  if (type === "OMEGAN") return "omegan-role"
  if (type === "OMEZKA") return "omezka-role"

  return ""
})


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

.emoji-icon {
  width: 1.6em;
  height: 1.6em;
  vertical-align: -0.2em;
  margin-right: 4px;
  display: inline-block;
}


.player-info {
  position: fixed;
  top: 120px;
  right: 50px;
  width: 320px;
  height: 250px;
  background: #181818e7;
  border-radius: 18px;
  border: 1px solid #d1d1d1cc;
  padding: 15px;
  box-shadow: 0 4px 10px rgba(0, 0, 0, 0.3);
  font-family: 'JetBrains Mono', monospace;
  z-index: 1000;
}

.content {
  position: fixed;
  display: flex;
  flex-direction: row;
  align-items:center;
  justify-content: flex-start;
  gap: 80px;
}

.avatar-container {
  position: relative;
  width: 80px;
  height: 120px;
}

.xp-ring {
  position: absolute;
  top: -26px;
  left: -26px;
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

.vip-ring .fg {
  stroke: gold;
  filter: drop-shadow(0 0 6px #ffdf70);
  animation: sparkle 2s infinite ease-in-out;
}

@keyframes sparkle {
  0%, 100% { stroke-width: 8; opacity: 1; }
  50% { stroke-width: 9.5; opacity: 0.9; }
}

.avatar {
  width: 130px;
  height: 130px;
  border-radius: 100%;
  object-fit: cover;
  position: relative;
  z-index: 1;
}

.info {
  display: flex;
  flex-direction: column;
  align-items: flex-start;
  flex: 100;
  color: #fff;
  font-size: 18px;
  min-width: 2;
}

.username {
  font-size: 24px;
  font-weight: 700;
  display: flex;
  align-items: center;
  gap: 6px;
}

.money,
.level {
  margin-top: 9px;
}


.race {
  font-size: 15px;
  font-weight: 100;
  display: flex;
  align-items: center;
  gap: 6px;
}

.title {
  font-size: 15px;
  font-weight: 700;
  display: flex;
  align-items: center;
  gap: 6px;
}

.level {
  font-size: 18px;
}

/* 🎩 РОЛИ */
.admin-role {
  color: #ff5555; /* админ — как баг */
}
.moderator-role {
  color: #ffaa00; /* жёлтый как знак "внимание" */
}
.tester-role {
  color: #55ffff; /* тестер — не от мира сего */
}
.ai-role {
  color: #c58fff; /* как багнутый нейронный лёд */
}
.user-role {
  color: #eeeeee; text-shadow: 0 0 3px #00f6ff; /* бледный фантом с подсветкой */
}

/* 🧬 user_type */
.omegakrut-role {
  color: #9c42f5; text-shadow: 0 0 4px #d0bfff; /* сияет, но не палится */
}
.omegan-role {
  color: #57c273; /* просто норм чел */
}
.omezka-role {
  color: #aaa; font-style: italic; /* серый мечтатель */
}
/* Контейнер под кольцо и аватар */


.vip-icon {
  margin-left: 6px;
  font-size: 1.2rem;
  color: gold;
  filter: drop-shadow(0 0 6px #ffdf70);
  text-shadow: 0 0 6px #ffe448c9;
  vertical-align: middle;
  animation: sparkle 1s infinite ease-in-out;
}

.vip-ring .fg {
  stroke: gold !important;
  filter: drop-shadow(0 0 6px #ffdf70);
  animation: sparkle 3s infinite ease-in-out;
}

@keyframes sparkle {
  0%, 100% { stroke-width: 8; opacity: 1; }
  50% { stroke-width: 9.5; opacity: 0.9; }
}

/* Кольцо */
.xp-ring {
  position: absolute;
  top: -30px;
  left: -30px;
  /* Масштабируем с 140×140 до 110×110 => ~0.7857 */
  width: 190px;
  height: 190px;
  transform: rotate(-90deg) scale(0.79);
  transform-origin: center;
  z-index: 100;
  overflow: visible !important;
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
</style>
  