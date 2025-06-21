<template>
    <!-- Глобальный SVG-градиент — НЕ видим, но доступен -->
  <svg width="0" height="0" style="position: absolute">
    <defs>
      <linearGradient id="xp-gradient" x1="0%" y1="0%" x2="100%" y2="100%">
        <stop offset="0%" stop-color="#ffe600" />
        <stop offset="50%" stop-color="#ffd000" />
        <stop offset="100%" stop-color="#ff9900" />
      </linearGradient>
    </defs>
  </svg>
  
  <div v-if="authReady" class="app-wrapper">
    <Header v-if="isAuthenticated" />
    
    <main class="main-content">
      <PlayerInfo v-if="isAuthenticated" />
      <router-view/>
      <GlobalChat v-if="isAuthenticated" />
    </main>

    <Footer v-if="isAuthenticated" />
  </div>

  <div v-else class="loader">Загрузка...</div>
  
  <ToastOutlet />
  <GlobalTooltip />
</template>

<script setup>
import { useAuthStore } from "@/store/auth";
import { ref, computed, onMounted, watch } from "vue";
import PlayerInfo from "@/components/PlayerInfo.vue";
import GlobalChat from "@/components/GlobalChat.vue";
import ToastOutlet from "@/components/ToastOutlet.vue";
import { io } from "socket.io-client";
import { useChatStore } from "@/store/chat";
import { usePlayerStore } from "@/store/player";
import GlobalTooltip from "@/components/GlobalTooltip.vue";
import Header from "@/components/Header.vue";
import Footer from "@/components/Footer.vue";

const authStore = useAuthStore();
const chatStore = useChatStore();
const playerStore = usePlayerStore();

const isAuthenticated = computed(() => authStore.isAuthenticated);
const authReady = computed(() => authStore.authReady);

let socket;

onMounted(async () => {
  await authStore.fetchUser();
  if (authStore.isAuthenticated) connectSocket();
});

watch(isAuthenticated, (logged) => {
  if (logged) connectSocket();
  else {
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

<style lang="scss">

.app-wrapper {
  background: transparent;
  position: relative;
  z-index: 0;
}

.main-content {
  flex: 1;
  width: 100%;
  max-width: 1400px;
  margin: 0 auto;
  padding: 20px;
  
}
</style>











