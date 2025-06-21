<template>
  
  <div v-if="player" class="avatar-block">
    
    <h1>{{ player.name || "Омежка" }}<span v-if="player.vip_subscription" class="vip-icon" :title="player.vip_subscription.label">✨</span></h1>
    
    
    <!-- ✅ Картинка аватара -->
    <div class="avatar-progress-container">
    <!-- SVG-кольцо -->
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

  <!-- ВОТ СЮДА кладём твою логику загрузки, ничего не ломая -->
  <label for="avatar-input" class="avatar-upload">
    <img :src="computedAvatar" alt="Аватар" class="avatar" />
    <i class="fa-solid fa-pencil edit-icon"></i>
  </label>
  <input id="avatar-input" type="file" accept="image/*" @change="uploadAvatar" hidden />
</div>

<h2 class="title" :class="roleColor">{{ titleToShow }}</h2>
    <div class="player-info">
  <div class="info-row"><span class="label">Уровень:</span><span>{{ player.level || 1 }}</span></div>
  <div class="info-row"><span class="label">Опыт:</span><span>{{ player.xp || 0 }} / {{ player.nextLevelXp || 100 }}</span></div>
  <div class="info-row"><span class="label">Звание:</span><span>{{ player.usertype || "Без титула" }}</span></div>
  <div class="info-row"><span class="label">Раса:</span><span>{{ player.race?.display_name || "Неизвестно" }}</span></div>
  <div class="info-row"><span class="label">Пол:</span><span>{{ player.gender_label }}</span></div>
  <div class="info-row"><span class="label">ДР:</span><span>{{ formatDate(player.birthdate, true) }}</span></div>
  <div class="info-row"><span class="label">В игре с:</span><span>{{ formatDate(player.registrationDate) }}</span></div>
</div>



    <p class="xp"></p>
  </div>
</template>
  
  <script setup>
import { computed, ref } from "vue";
import { usePlayerStore } from "@/store/player";
import axios from "axios";

const defaultAvatar = "https://localhost:5002/static/uploads/default_avatar.png";
const playerStore = usePlayerStore();
const player = computed(() => playerStore.player);
const isUploading = ref(false);

// ✅ Динамическое обновление аватарки
const computedAvatar = computed(() => {
  const avatar = player.value?.avatar;

  if (avatar?.startsWith("/api/profile/avatars")) {
    return `https://localhost:5002${avatar}?t=${Date.now()}`;
  }

  return "https://localhost:5002/api/profile/avatars/default_avatar.png"; // 🔥 безопасно
});

const radius = 64;
const circumference = 2 * Math.PI * radius;

const xpPercent = computed(() => {
  if (!player.value) return 0;
  return (player.value.xp / player.value.nextLevelXp) * 100;
});

const xpOffset = computed(() => {
  return circumference - (circumference * xpPercent.value) / 100;
});


function formatDate(isoString, withoutYear = false) {
  if (!isoString) return "Не указано";
  const date = new Date(isoString);
  return date.toLocaleDateString("ru-RU", {
    year: withoutYear ? undefined : "numeric",
    month: "long",
    day: "numeric",
  });
}

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

function genderLabel(gender) {
  switch (gender) {
    case "MALE":
      return "Мужской";
    case "FEMALE":
      return "Женский";
    case "UNKNOWN":
      return "Не указан";
    default:
      return gender || "Неизвестно";
  }
}


// ✅ Функция загрузки аватара
const uploadAvatar = async (event) => {
  const file = event.target.files[0];
  if (!file || isUploading.value) return;

  isUploading.value = true;
  const formData = new FormData();
  formData.append("avatar", file);

  try {
    const response = await axios.post("https://localhost:5002/api/profile/upload-avatar", formData, {
      withCredentials: true,
      headers: { "Content-Type": "multipart/form-data" },
    });

    if (response.data.avatarUrl) {
      playerStore.player.avatar = response.data.avatarUrl; // ✅ Обновляем в store
      playerStore.fetchPlayer(); // 🔥 Дополнительно загружаем обновлённые данные
    } else {
      console.error("Ошибка загрузки:", response.data.error);
    }
  } catch (error) {
    console.error("Ошибка загрузки аватара:", error);
  } finally {
    isUploading.value = false;
  }
};
</script>
  
  <style scoped>

.vip-icon {
  margin-left: 6px;
  font-size: 1.3rem;
  color: gold;
  filter: drop-shadow(0 0 6px #ffdf70);
  text-shadow: 0 0 6px #ffe448c9;
  vertical-align: middle;
  animation: sparkle 1s infinite ease-in-out;
}

.title {
  font-weight: bold;
  font-size: 1rem;
  gap: auto;
  margin-top: 20px;
}

/* 🎩 РОЛИ */
.admin-role {
  color: #f14f43; /* админ — как баг */
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

.avatar-progress-container {
  position: relative;
  width: 200px;
  height: 200px;
  margin: 0 auto 10px;
  display: flex;
  align-items: center;
  justify-content: center;
  z-index: 1;
}

.xp-ring {
  position: absolute;
  width: 230px;
  height: 230px;
  top: -15px;
  left: -15px;
  transform: rotate(-90deg);
  z-index: 50;
  overflow: visible !important;
}

.xp-ring .bg {
  fill: none;
  stroke: rgba(48, 40, 53, 0.356);
  stroke-width: 8;
  z-index: 5;
}

.xp-ring .fg {
  fill: none;
  stroke: #00ffc3;
  stroke-width: 8;
  stroke-linecap: round;
  transition: stroke-dashoffset 0.4s ease;
  z-index: 100;
}

.avatar-upload {
  position: relative;
  display: flex;
  align-items: center;
  justify-content: center;
  z-index: 100;
}

.avatar {
  width: 200px;
  height: 200px;
  border-radius: 50%;
  object-fit: cover;
  transition: opacity 0.2s ease-in-out;
  cursor: pointer;
}

 .avatar-block {
  max-width: 600px;
  flex-direction: column;
  backdrop-filter: blur(7px);
  background:rgba(38, 32, 39, 0.48);
  border: 1px solid #2e2c2c;
  border-radius: 8px;
  padding: 10px;
  font-size: 13px;
  gap: 10px;
  }

  .fa-pencil {
    position: absolute;
    bottom: 10px;
    right: 10px;
    background: rgba(0, 0, 0, 0.6); /* 🔥 Тёмный фон */
    color: white;
    font-size: 16px;
    padding: 5px;
    border-radius: 50%;
    opacity: 0;
    transition: opacity 0.1s ease-out; /* 🔥 Убираем задержку */
    pointer-events: none; /* 🔥 Исключаем из кликов */
  }

  /* 🔥 Теперь ховер работает ТОЛЬКО внутри самой картинки */
  .avatar:hover {
    opacity: 0.7; /* Затемняем */
  }

  .avatar:hover + .edit-icon {
    opacity: 1; /* Показываем карандаш */
  }

.avatar-block h1 {
  font-size: 1.7rem;
  padding-top: 1px;       /* Увеличенный размер шрифта */
  font-weight: bold;            /* Жирный шрифт */
  color: #ffffff;               /* Яркий золотой цвет */
  font-family: 'JetBrains Mono', monospace;
}

.player-info {
  display: flex;
  flex-direction: column;
  gap: 4px;
}

.info-row {
  display: flex;
  justify-content: space-between;
  color: white;
  font-size: 14px;
  line-height: 1.4;
}

.label {
  color: #00ffc3;
  font-weight: 600;
}

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
  </style>
  
  