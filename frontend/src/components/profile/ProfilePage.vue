<script setup>
import { ref, onMounted } from "vue";
import { useRoute } from "vue-router";
import api from "@/utils/axios";

const route = useRoute();
const profile = ref(null);
const isLoading = ref(true);
const errorMessage = ref("");

function getAvatarUrl(avatarPath) {
  if (!avatarPath) {
    return "https://localhost:5002/api/profile/avatars/default_avatar.png";
  }
  return `https://localhost:5002${avatarPath}?t=${Date.now()}`;
}

async function fetchProfile() {
  isLoading.value = true;
  errorMessage.value = "";

  try {
    const response = await api.get(`/player/public/${route.params.id}`);
    profile.value = response.data;
  } catch (error) {
    console.error("❌ Ошибка загрузки профиля:", error);
    errorMessage.value = "Ошибка загрузки профиля.";
  } finally {
    isLoading.value = false;
  }
}
onMounted(fetchProfile);
</script>

<template>
  <div v-if="isLoading">🔄 Загрузка профиля...</div>
  <div v-else-if="errorMessage">{{ errorMessage }}</div>
  <div v-else>
    <h2>Профиль игрока: {{ profile.name }}</h2>
<p>Титул: {{ profile.usertype }}</p>
<img :src="getAvatarUrl(profile.avatar)" alt="Аватар" class="avatar" />
<p>О себе: {{ profile.bio || "Нет информации" }}</p>
<p>Уровень: {{ profile.level }}</p>
<p :class="{ online: profile.status === 'online', offline: profile.status === 'offline' }">
  Статус: {{ profile.status === 'online' ? '🟢 Онлайн' : '🔴 Оффлайн' }}
</p>
  </div>
</template>



<style scoped>
.online {
  color: green;
  font-weight: bold;
}

.offline {
  color: #999;
  font-weight: normal;
}

.profile-container {
  max-width: 500px;
  margin: auto;
  padding: 20px;
  background: #222;
  color: #fff;
  border-radius: 10px;
  text-align: center;
}
.profile-container img {
  width: 100px;
  height: 100px;
  border-radius: 50%;
  object-fit: cover;
}
button {
  background: #0084ff;
  color: white;
  padding: 10px;
  border: none;
  border-radius: 5px;
  cursor: pointer;
}
button:hover {
  background: #006fd6;
}
</style>
