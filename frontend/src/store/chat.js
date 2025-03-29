import { defineStore } from "pinia";
import { ref } from "vue";
import { io } from "socket.io-client";
import api from "@/utils/axios";

export const useChatStore = defineStore("chat", () => {
  const messages = ref([]);
  const onlineUsers = ref(0);
  // НЕ реактивный сокет:
  let socket = null;
  // Только isConnected — реактивная переменная
  const isConnected = ref(false);
  let listenersAttached = false;

  function connectSocket() {
    if (!import.meta.env.VITE_WS_URL) {
      console.error("❌ [ERROR] VITE_WS_URL не задан! WebSocket не подключится.");
      return;
    }
    // Если сокет уже создан и подключен, ничего не делаем
    if (socket && socket.connected) {
      console.log("🔄 WebSocket уже активен.");
      return;
    }
    console.log("🔄 Подключаем WebSocket...");
    socket = io(import.meta.env.VITE_WS_URL, {
      transports: ["websocket"],
      withCredentials: true,
    });

    socket.on("connect", () => {
      console.log("✅ WebSocket подключён!");
      isConnected.value = true;
      loadInitialMessages();
      updateOnlineUsers();
    });

    socket.on("disconnect", () => {
      console.log("❌ WebSocket отключён.");
      isConnected.value = false;
    });
  if (!listenersAttached) {
    socket.on("chat_message", (message) => {
      console.log("📩 Новое сообщение:", message);
      messages.value.push(message);
    });

    socket.on("online_users", (count) => {
      console.log("👥 Онлайн:", count);
      onlineUsers.value = count;
    });
    listenersAttached = true;
  }

    setInterval(updateOnlineUsers, 30000); // каждые 30 секунд
  }

  async function updateOnlineUsers() {
    try {
      const { data } = await api.get("/chat/online"); // если базовый URL содержит /api, путь может быть "/chat/online"
      if (data && data.online !== undefined) {
        onlineUsers.value = data.online;
      }
    } catch (error) {
      console.error("⚠️ Ошибка получения онлайн-статуса:", error);
    }
  }

  async function loadInitialMessages() {
    try {
      const { data } = await api.get("/chat/messages");
      messages.value = data;
    } catch (error) {
      console.error("⚠️ Ошибка загрузки сообщений:", error);
    }
  }

  function sendMessage(text) {
    if (!socket || !socket.connected) {
      console.warn("⚠️ WebSocket не подключён, сообщение не отправлено.");
      return;
    }
    console.log("🚀 Отправляем сообщение:", { text });
    socket.emit("send_message", { text });
  }

  return {
    messages,
    onlineUsers,
    isConnected,
    loadInitialMessages,
    sendMessage,
    connectSocket,
  };
});

















