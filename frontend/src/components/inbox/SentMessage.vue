<script setup>
import { ref } from 'vue'
import { useInboxStore } from "@/store/inbox"
import SentMessView from "./SentMessView.vue" // отдельная модалка для просмотра сообщения

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
</script>

<template>
  <div class="messages-scroll">
    
    
    <ul v-if="inboxStore.sentMessages && inboxStore.sentMessages.length">
      
      
      <li 
        v-for="msg in inboxStore.sentMessages" 
        :key="msg.id" 
        class="message-container"
        @click="openDetailedMessage(msg)"
      >
        
      
        <div class="message-header">
          <p><strong>Кому:</strong> {{ msg.recipient }}</p>
          <button @click.stop="deleteMessage(msg.id)" class="delete-button">
            <i class="fa-solid fa-trash"></i>
          </button>
        </div>
        

        <div class="message-info">
          <span class="subject"><strong>Тема:</strong> {{ msg.subject || '-' }}</span>
          <span class="timestamp">{{ formatDate(msg.timestamp) }}</span>
          
        </div>
        <hr />
        
        
        <div class="message-body">
          {{ msg.content }}
        </div>
      
      
      </li>
    </ul>
    <p v-else>Нет исходящих сообщений.</p>

    <!-- Подробный просмотр сообщения в отдельном модальном окне -->
    <SentMessView 
      v-if="openedMessage" 
      :message="openedMessage" 
      @close="openedMessage = null" 
    />
  </div>
</template>

<style scoped>

.subject {
  color: rgba(0, 0, 0, 0.925);
  margin-bottom: 5px;
  font-size: 14px;
}

p {
  margin: 0px;
  font-size: 14px;}

.message-info {
  margin-top: 0.5rem;
  display: flex;
  justify-content: space-between;
  font-size: 0.7rem;
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
  color: rgba(0, 0, 0, 0.925);
  border: 1px solid #ddd;
  background: #ffffffa2;
  border-radius: 6px;
  font-family: 'JetBrains Mono', monospace;
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
}

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
  padding: 1;         /* убираем лишние отступы */
  width: 15px;        /* фиксированная ширина */
  height: 15px;       /* фиксированная высота */
  display: flex;
  align-items: center;
  justify-content: center;
}


.message-container:hover .delete-button {
  opacity: 1;
}
</style>


