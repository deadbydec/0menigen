<script setup>
import { useAuthStore } from "@/store/auth";
import { onMounted, computed } from "vue";
import PlayerInfo from "@/components/PlayerInfo.vue";
import GlobalChat from "@/components/GlobalChat.vue";
import { io } from "socket.io-client";
import { useChatStore } from "@/store/chat";

const authStore = useAuthStore();
const isAuthenticated = computed(() => authStore.isAuthenticated);
const authReady = computed(() => authStore.authReady); // ← вот это тоже важно!

let socket = null;

onMounted(async () => {
  const chatStore = useChatStore();

  // 🧠 Сначала грузим пользователя
  await authStore.fetchUser(); // это подгружает токен, проверяет куки и т.д.

  // 📡 Подключаем WebSocket чат
  chatStore.connectSocket();
});

onMounted(async () => {
  await authStore.fetchUser(); // ⚠️ ВСЕГДА явно запрашиваем юзера при запуске приложения

  socket = io("https://localhost:5002", { transports: ["websocket"] });
  socket.on("connect", () => console.log("✅ WebSocket подключен!"));
  socket.on("disconnect", () => console.log("❌ WebSocket отключён."));
});

// ✅ Перезагружаем состояние при каждом логауте

</script>

<template>
  <div v-if="authReady">
    <PlayerInfo v-if="isAuthenticated" />
    <router-view />
    <GlobalChat v-if="isAuthenticated" />
  </div>
  <div v-else>
    <div class="loader">Загрузка...</div>
  </div>
</template>








<style scoped>
/* Можно добавить глобальные стили, если нужно */
</style>



