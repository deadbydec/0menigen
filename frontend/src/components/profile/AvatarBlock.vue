<template>
  <div v-if="player" class="avatar-block">
    <!-- ✅ Картинка аватара -->
    <div class="avatar-progress-container">
    <!-- SVG-кольцо -->
    <svg class="xp-ring" viewBox="0 0 140 140">
      <circle class="bg" cx="70" cy="70" r="64" />
      <circle
        class="fg"
        cx="70" cy="70" r="64"
        :stroke-dasharray="circumference"
        :stroke-dashoffset="xpOffset"
      />
    </svg>

  <!-- ВОТ СЮДА кладём твою логику загрузки, ничего не ломая -->
  <label for="avatar-input" class="avatar-upload">
    <img :src="computedAvatar" alt="Аватар" class="avatar" />
    <i class="fa-solid fa-pencil edit-icon"></i>
  </label>
  <input id="avatar-input" type="file" accept="image/*" @change="uploadAvatar" hidden />
</div>

    <div class="player-info">
    <p class="level">Уровень: {{ player.level || 1 }}</p>
    Опыт: {{ player.xp || 0 }} / {{ player.nextLevelXp || 100 }}
    <h2>{{ player.name || "Омежка" }}</h2>
    <p>{{ player.usertype || "Без титула" }} — {{ player.race && player.race.display_name || "Неизвестно" }}</p>
    <p class="coins">💰 {{ player.coins || 0,0 }} монет</p>
    <p>🧿 {{ player.nullings ?? 0 }} нуллингов</p>
    <p>🎂 ДР: {{ formatDate(player.birthdate) }}</p>
    <p>🧬 Пол: {{ player.gender_label }}</p>
    <p>🕰️ В игре с {{ formatDate(player.registrationDate) }}</p>
    <p class="xp"></p>
  </div>
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


function formatDate(isoString) {
  if (!isoString) return "Не указано";
  const date = new Date(isoString);
  return date.toLocaleDateString("ru-RU", {
    year: "numeric",
    month: "long",
    day: "numeric",
  });
}

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

.avatar-progress-container {
  position: relative;
  width: 200px;
  height: 200px;
  margin: 0 auto 11px;
  display: flex;
  align-items: center;
  justify-content: center;
  z-index: 50;
}

.xp-ring {
  position: absolute;
  width: 230px;
  height: 230px;
  top: -16px;
  left: -16px;
  transform: rotate(-90deg);
  z-index: 50;
}

.xp-ring .bg {
  fill: none;
  stroke: rgba(48, 40, 53, 0.356);
  stroke-width: 8;
  z-index: 50;
}

.xp-ring .fg {
  fill: none;
  stroke: #00ffc3;
  stroke-width: 8;
  stroke-linecap: round;
  transition: stroke-dashoffset 0.4s ease;
  z-index: 50;
}

.avatar-upload {
  position: relative;
  display: flex;
  align-items: center;
  justify-content: center;
}

.avatar {
  width: 200px;
  height: 200px;
  border-radius: 50%;
  object-fit: cover;
  transition: opacity 0.2s ease-in-out;
}

  

 .avatar-block {
    text-align: center;
    max-height: 500px;
    background: rgba(0, 0, 0, 0.582);
    border: 2px solid rgba(0, 0, 0, 0.692);
    padding: 15px;
    border-radius: 10px;
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

  

  /* Секция с инфой под аватаром */
.player-info {
  /* Если хочешь задать фиксированную ширину – раскомментируй следующую строку */
  /* width: 100%; */
  text-align: left;
}

.player-info h2 {
  font-size: 1.5rem;            /* Увеличенный размер шрифта */
  font-weight: bold;            /* Жирный шрифт */
  color: #8329ce;               /* Яркий золотой цвет */
  text-shadow: 1px 1px 3px rgba(0, 0, 0, 0.5); /* Легкая тень для объема */
  margin-bottom: 5px;           /* Немного отступа снизу для читаемости */
  padding: auto;
}

/* Обнуляем стандартные отступы и задаем стабильный line-height */
.player-info p,
.player-info h2 {
  margin: 2px 0;
  padding: 0;
  line-height: 1.2;
}
  </style>
  
  