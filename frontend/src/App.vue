<template>
  <div v-if="authReady">
    <PlayerInfo v-if="isAuthenticated" />

    <router-view /> <!-- страницы -->

    <GlobalChat v-if="isAuthenticated" />
  </div>
  <div v-else class="loader">Загрузка...</div>

  <ToastOutlet />
</template>

<script setup>
import { useAuthStore } from "@/store/auth";
import { ref, computed, onMounted, watch } from "vue";
import PlayerInfo  from "@/components/PlayerInfo.vue";
import GlobalChat  from "@/components/GlobalChat.vue";
import ToastOutlet from "@/components/ToastOutlet.vue";
import { io }      from "socket.io-client";
import { useChatStore } from "@/store/chat";
import { usePlayerStore } from "@/store/player";

const authStore   = useAuthStore();
const chatStore   = useChatStore();
const playerStore = usePlayerStore();

const isAuthenticated = computed(() => authStore.isAuthenticated);
const authReady       = computed(() => authStore.authReady);

let socket;

// первичная проверка
onMounted(async () => {
  await authStore.fetchUser();          // тут authReady = true

  if (authStore.isAuthenticated) {
    connectSocket();
  }
});

// реагируем на смену статуса
watch(isAuthenticated, (logged) => {
  if (logged) {
    connectSocket();
  } else {
    disconnectSocket();
    playerStore.player = null;
  }
});

function connectSocket() {
  if (socket) return;
  socket = io("https://localhost:5002", { transports: ["websocket"] });
  chatStore.bindSocket?.(socket);
}

function disconnectSocket() {
  if (!socket) return;
  socket.disconnect();
  socket = null;
}
</script>










