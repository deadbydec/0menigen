<script setup>
import { useInboxStore } from "@/store/inbox";
import InboxMessage from "./InboxMessage.vue";
import SentMessage from "./SentMessage.vue";
import SendMessage from "./SendMessage.vue";

const isDark = ref(true); // 🌑 по умолчанию тёмная
const inboxStore = useInboxStore();
</script>

<template>
  <teleport to="body">
    <div v-if="inboxStore.isModalOpen" class="modal-m" @click.self="inboxStore.closeModal">
      <div :class="['modal', { dark: isDark }]">
        <!-- Кнопка закрытия -->
        <!--<button @click="inboxStore.closeModal" class="close-btn">✖️</button>-->
        <div class="modal-header">
        <!-- Заголовок -->
        <h2>📩 Почтовый ящик</h2>

        <!-- Переключатель темы -->
        <label class="theme-toggle">
          <input type="checkbox" v-model="isDark" />
          🌘
        </label>
        </div>
        <!-- Основной контент с фиксированным размером и внутренним скроллом -->
        <div class="modal-body">
          <div v-if="inboxStore.currentTab === 'inbox'">
            <InboxMessage v-if="inboxStore.inboxMessages" />
          </div>
          <div v-if="inboxStore.currentTab === 'sent'">
            <SentMessage v-if="inboxStore.sentMessages" />
          </div>
          <div v-if="inboxStore.currentTab === 'send'">
            <SendMessage />
          </div>
        </div>

        <!-- Фиксированные вкладки внизу -->
        <div class="modal-footer">
          <button @click="inboxStore.currentTab = 'inbox'" :class="{ active: inboxStore.currentTab === 'inbox' }">Входящие</button>
          <button @click="inboxStore.currentTab = 'sent'" :class="{ active: inboxStore.currentTab === 'sent' }">Исходящие</button>
          <button @click="inboxStore.currentTab = 'send'" :class="{ active: inboxStore.currentTab === 'send' }">📨 Написать</button>
        </div>
      </div>
    </div>
  </teleport>
</template>


<style scoped>
.modal-header h2 {
  margin: 0;
}


  .modal-header {
  position: relative;
  text-align: center;
  padding: 1rem;
}


.modal-m {
  position: fixed;
  top: 0;
  left: 0;
  width: 100%;
  height: 100%;
  z-index: 10;
  display: flex;
  align-items: center;
  justify-content: center;
  background: rgba(0,0,0,0.5);
}

.modal {
  width: 500px;
  height: 500px;
  background: #fff;
  border-radius: 10px;
  overflow: hidden;
  display: flex;
  flex-direction: column;
  position: relative;
}

.modal-body {
  flex: 1;
  overflow-y: auto;
  padding: 1rem;
}

.modal-footer {
  display: flex;
  justify-content: space-around;
  padding: 1.0rem;
}

.modal-footer button {
  border: none;
  cursor: pointer;
  background: transparent;
}

.modal-footer button.active {
  font-weight: bold;

}

.theme-toggle {
  position: absolute;
  top: 10px;
  left: 10px;
}

/* ❌ закрытие */
.close-btn {
  position: absolute;
  top: 10px;
  right: 10px;
  font-size: 22px;
  border: none;
  background: transparent;
  color: inherit;
  cursor: pointer;
  transition: transform 0.2s ease;
}


.modal.dark {
  background: #1e1e1eea;
  color: #f0f0f0;
  border: 2px solid #444;
}

.modal.dark .modal-footer button {
  background: #444;
}

.modal.dark .modal-footer button.active {
  background: #600794;
}
</style>

