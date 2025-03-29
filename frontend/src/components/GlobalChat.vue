<template>
  <!-- Кнопка открытия/закрытия чата -->
  <button @click="isOpen = !isOpen" :class="['chat-toggle', { open: isOpen }]">
    <font-awesome-icon :icon="isOpen ? ['fas', 'times'] : ['fas', 'comment-dots']" />
  </button>

  <!-- Левый сайдбар чата -->
  <div :class="['chat-sidebar', { open: isOpen }]">
    <!-- Верхняя панель с онлайн-статусом -->
    <div class="chat-header">
      <span class="chat-title">Чат</span>
      <span class="chat-online">🟢 Онлайн: {{ onlineUsers }}</span>
    </div>

    <div class="chat-messages" ref="messagesContainer">
      <div v-for="(message, index) in messages" :key="index" class="chat-message">
        <span v-if="message && message.username" class="chat-username">
          {{ message.username }}:
        </span>
        <span v-if="message && message.text">{{ message.text }}</span>
      </div>
    </div>

    <div class="chat-input">
      <button class="emoji-btn" @click="toggleEmojiMenu">😊</button>
      <!-- Выпадающее меню смайлов -->
      <div v-if="showEmojiMenu" class="emoji-menu">
        <span v-for="emoji in emojis" :key="emoji" @click="addEmoji(emoji)">
          {{ emoji }}
        </span>
      </div>

      <input
        v-model="newMessage"
        type="text"
        class="chat-textbox"
        placeholder="Введите сообщение..."
        @keydown.enter="handleSendMessage"
      />
      <button @click="handleSendMessage" class="chat-send" :disabled="isMuted">➤</button>
    </div>
  </div>
</template>

<script setup>
import { ref, computed, watch, onMounted, nextTick } from "vue";
import { useChatStore } from "@/store/chat"; // Убедись, что путь соответствует твоей структуре проекта

const chatStore = useChatStore();
const isOpen = ref(localStorage.getItem("chat_open") === "true");
const newMessage = ref("");
const messages = computed(() => chatStore.messages);
const onlineUsers = computed(() => chatStore.onlineUsers);
const showEmojiMenu = ref(false);
const emojis = ["😆", "🔥", "💀", "👀", "🤡", "🎃", "😎"];
// Предположим, что isMuted определено, если нужно – иначе можно убрать
const isMuted = ref(false);

function handleSendMessage() {
  if (newMessage.value.trim()) {
    chatStore.sendMessage(newMessage.value.trim());
    newMessage.value = "";
  }
}

// При монтировании подключаем сокет
onMounted(() => {
  chatStore.connectSocket();
});

// Функция открытия/закрытия меню смайлов
const toggleEmojiMenu = () => {
  showEmojiMenu.value = !showEmojiMenu.value;
};

// Функция добавления смайлика
const addEmoji = (emoji) => {
  newMessage.value += emoji;
  showEmojiMenu.value = false;
};

// Автоскролл при новых сообщениях
watch(messages, () => {
  nextTick(() => {
    const chatMessages = document.querySelector(".chat-messages");
    if (chatMessages) {
      chatMessages.scrollTop = chatMessages.scrollHeight;
    }
  });
});
</script>

<style scoped>
.chat-toggle {
  position: fixed;
  top: 50%;
  left: 10px;
  transform: translateY(-50%);
  background: rgba(0, 0, 0, 0.8);
  color: white;
  border: none;
  width: 40px;
  height: 40px;
  display: flex;
  align-items: center;
  justify-content: center;
  cursor: pointer;
  border-radius: 8px;
  font-size: 18px;
  transition: all 0.3s ease-in-out;
  box-shadow: 2px 2px 10px rgba(0, 0, 0, 0.3);
}

.chat-toggle.open {
  left: 320px;
}

.chat-sidebar {
  position: fixed;
  top: 50%;
  left: -320px;
  transform: translateY(-50%);
  width: 320px;
  height: 70vh;
  background: rgba(0, 0, 0, 0.603);
  color: white;
  display: flex;
  flex-direction: column;
  box-shadow: 5px 0 10px rgba(0, 0, 0, 0.2);
  transition: left 0.3s ease-in-out;
  border-radius: 14px;
  overflow: hidden;
}

.chat-sidebar.open {
  left: 0;
}

.chat-header {
  background: rgba(0, 0, 0, 0.8);
  padding: 10px;
  display: flex;
  justify-content: space-between;
  font-weight: bold;
  border-bottom: 1px solid #444;
  border-radius: 13px;
}

.chat-messages {
  flex-grow: 1;
  overflow-y: auto;
  display: flex;
  flex-direction: column;
  gap: 5px;
  padding: 10px;
  padding-bottom: 80px;
  min-height: 100px;
  scrollbar-width: none;
  font-family: "Inter", sans-serif;
  font-size: 14px;
  line-height: 1.4;
  color: #ddd;
}

.chat-messages::-webkit-scrollbar {
  display: none;
}

.chat-username {
  padding: 2px 6px;
  border-radius: 5px;
  font-weight: bold;
  color: rgba(24, 204, 174, 0.85);
  text-shadow: 0px 0px 8px rgba(250, 246, 255, 0.52);
}

.chat-input {
  position: absolute;
  bottom: 0;
  left: 0;
  width: 100%;
  display: flex;
  padding: 10px;
  background: rgba(0, 0, 0, 0.8);
  border-radius: 0 0 14px 14px;
  z-index: 10;
}

.chat-textbox {
  flex-grow: 1;
  background: rgba(0, 0, 0, 0.384);
  border: 1px solid #444;
  color: white;
  padding: 8px;
  border-radius: 14px;
  scroll-behavior: smooth;
}

.emoji-btn,
.chat-send {
  background: none;
  border: none;
  font-size: 18px;
  cursor: pointer;
  color: white;
  padding: 5px;
}

.emoji-btn:hover,
.chat-send:hover {
  opacity: 0.8;
}

.emoji-menu {
  position: absolute;
  bottom: 40px;
  left: 0;
  background: #222;
  border-radius: 19px;
  padding: 5px 10px;
  display: flex;
  gap: 5px;
  font-size: 20px;
  cursor: pointer;
  box-shadow: 0px 4px 10px rgba(0, 0, 0, 0.2);
}

.emoji-menu span {
  padding: 5px;
  cursor: pointer;
}

.emoji-menu span:hover {
  transform: scale(1.2);
}
</style>

