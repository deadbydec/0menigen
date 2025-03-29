<script setup>
import { ref } from 'vue'
import { useInboxStore } from "@/store/inbox"
import MessView from "./MessView.vue" // отдельная модалка для просмотра сообщения

const inboxStore = useInboxStore()
const openedMessage = ref(null)


function openDetailedMessage(msg) {
  openedMessage.value = msg
}


function deleteMessage(id) {
  if (!id) {
    console.warn("Попытка удалить сообщение без id")
    return
  }
  inboxStore.deleteMessage(id)
}

function formatDate(timestamp) {
  return new Date(timestamp).toLocaleString("ru-RU")
}

// 💥 Исправление вот тут:
function acceptGift(giftId) {
  inboxStore.acceptGift(giftId)
}

function rejectGift(giftId) {
  inboxStore.rejectGift(giftId)
}

// 💥 Новое:

</script>

<template>
  <div class="messages-scroll">
    <h3>📥 Входящие</h3>
    <ul v-if="inboxStore.inboxMessages && inboxStore.inboxMessages.length">
      <li 
        v-for="msg in inboxStore.inboxMessages" 
        :key="msg.id" 
        class="message-container"
        @click="openDetailedMessage(msg)"
      >
        <div class="message-header">
          <strong>От: {{ msg.sender }}</strong>
          <button @click.stop="deleteMessage(msg.id)" class="delete-button">
            <i class="fa-solid fa-trash"></i>
          </button>
        </div>
        
        <div class="message-info">
          <span class="subject"><strong>Тема:</strong> {{ msg.subject || '-' }}</span>
          <span class="timestamp">{{ formatDate(msg.timestamp) }}</span>          
        </div>

        <div class="message-body">
  {{ msg.content }}
  <div 
  v-if="msg.message_type === 'gift'" 
  class="gift-actions"
>
  <button @click.stop="acceptGift(msg.related_id)">🎁 Принять</button>
  <button @click.stop="rejectGift(msg.related_id)">🚫 Отклонить</button>
</div>
</div>

      </li>
    </ul>
    <p v-else>Нет входящих сообщений.</p>

    <!-- Подробный просмотр сообщения в отдельном модальном окне -->
    <MessView 
      v-if="openedMessage" 
      :message="openedMessage" 
      @close="openedMessage = null" 
    />
  </div>
</template>

<style scoped>
.subject {
  font-weight: bold;
  color: #cfcfcf;
  margin-bottom: 5px;
}


.message-info {
  margin-top: 0.5rem;
  display: flex;
  justify-content: space-between;
  font-size: 0.9rem;
  color: #666;
}

ul {
  list-style-type: none;
  margin: 0;
  padding: 0;
}

.messages-scroll {
  position: relative;
  overflow: hidden;
}

.message-container {
  color: black;
  border: 1px solid #ddd;
  background: #ffffffa2;
  border-radius: 6px;
  padding: 0.75rem;
  margin-bottom: 0.5rem;
  cursor: pointer;
  transition: background 0.3s ease;
}

.message-container:hover {
  background: #f9f9f9;
}

.message-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
}

.message-body {
  margin-top: 0.5rem;
  padding-top: 0.5rem;
  border-top: 1px dashed #ccc;
}

/* Кнопка удаления */
/* Кнопка удаления теперь в заголовке, её область минимальна */
/* Кнопка удаления: абсолютное позиционирование справа */
.delete-button {
  position: relative;
  right: 0.5rem;
  top: 50%;
  transform: translateY(-50%);
  background: transparent;
  border: none;
  color: #000;
  font-size: 1rem;
  cursor: pointer;
  opacity: 0;
  transition: opacity 0.2s;
  padding: 0;         /* убираем лишние отступы */
  width: 24px;        /* фиксированная ширина */
  height: 24px;       /* фиксированная высота */
  display: flex;
  align-items: center;
  justify-content: center;
}

.gift-actions {
  position: relative;
}

.message-container:hover .delete-button {
  opacity: 1;
}
</style>

