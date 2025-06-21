<script setup>
import { useInboxStore } from "@/store/inbox";
import InboxMessage from "./InboxMessage.vue";
import SentMessage from "./SentMessage.vue";
import SendMessage from "./SendMessage.vue";

const isDark = ref(false); // 🌑 по умолчанию тёмная
const inboxStore = useInboxStore();
</script>

<template>
  <teleport to="body">
    <div v-if="inboxStore.isModalOpen" class="modal-m">
      
      <div :class="['modal', isDark ? 'dark' : 'light']">
        <!-- Кнопка закрытия -->
        
        <div class="modal-header">
        <!-- Заголовок -->
        <h1>Личные сообщения</h1>

        <!-- Переключатель темы -->
        <label class="theme-toggle">
          
          <input type="checkbox" v-model="isDark" />
          🌘
        </label>
<button @click="inboxStore.closeModal" class="close-btn"><i class="fa-solid fa-xmark"></i></button>
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
          <button @click="inboxStore.currentTab = 'send'" :class="{ active: inboxStore.currentTab === 'send' }"><i class="fa-solid fa-pencil"></i></button>
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
  padding: 0rem;
}

h1 {
  font-size: 22px;
  background: rgba(0, 0, 0, 0.4);
  border-radius: 12px;
  font-family: 'JetBrains Mono', monospace;
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
  background: rgba(0, 0, 0, 0.87);
}

.modal {
  width: 500px;
  height: 500px;
  border-radius: 10px;
  overflow: hidden;
  display: flex;
  flex-direction: column;
  position: relative;
  transition: background 0.3s ease, color 0.3s ease;
}

/* 🌑 ТЁМНЫЙ РЕЖИМ */
.modal.dark {
  background: #2a1c31ea;
  color: #f0f0f0;
  border: 2px solid #444;

  .modal-footer button {
    background: rgba(255, 255, 255, 0.05);
    border: 1px solid rgba(255, 255, 255, 0.1);
    color: #fff;

    &:hover {
      background: rgba(10, 121, 106, 0.76);
    }
  }

  .modal-footer button.active {
    background: rgba(10, 121, 106, 0.76);
  }
  h1 {
    background: rgba(69, 151, 140, 0.76);
  }
}

/* ☀️ СВЕТЛЫЙ РЕЖИМ */
.modal.light {
  background: #f4f4f4;
  color: #222;
  border: 2px solid #ccc;

  .modal-footer button {
    background: rgba(0, 0, 0, 0.05);
    border: 1px solid rgba(0, 0, 0, 0.1);
    color: #111;

    &:hover {
      background: rgba(10, 121, 106, 0.26);
    }
  }

  .modal-footer button.active {
    background: rgba(69, 151, 140, 0.76);
  }

  h1 {
    background: rgba(69, 151, 140, 0.76);
  }
}

i {
  font-size: 20px;
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
  font-family: 'JetBrains Mono', monospace;
}

.close-btn {
  margin-top: 2rem;
  background: transparent;
  position:fixed;
  border: none;
  color: #342d38;
  width: 10px;
  height: 10px;
  font-size: 26px;
  margin-left: 65px;
  margin-top: 12px;
  border-radius: 6px;
  cursor: pointer;
  
:hover {
  border-radius: 10px;
  transform: scale(1.2);
}
}

.modal-footer button {
  background: rgba(255, 255, 255, 0.1);
  border: 1px solid rgba(255, 255, 255, 0.2);
  color: #fff;
  padding: 0.5rem 1rem;
  cursor: pointer;
  width: 140px;
  border-radius: 8px;
  text-transform: uppercase;
  transition: background 0.2s ease, transform 0.1s ease;

  &:hover {
    background: rgba(10, 121, 106, 0.76);
  }

  &:active {
    transform: scale(0.98);
  }

  &:disabled {
    opacity: 0.4;
    cursor: not-allowed;
  }
}

.modal-footer button.active {
  background: rgba(10, 121, 106, 0.76);
  border: 1px solid rgba(255, 255, 255, 0.2);
  color: #fff;
  padding: 0.5rem 1rem;
  cursor: pointer;
  border-radius: 8px;
  text-transform: uppercase;
  transition: background 0.2s ease, transform 0.1s ease;

  &:hover {
    background: rgba(10, 121, 106, 0.76);
  }

  &:active {
    transform: scale(0.98);
  }

  &:disabled {
    opacity: 0.4;
    cursor: not-allowed;
  }

}

.theme-toggle {
  position: absolute;
  top: 10px;
  left: 10px;
}


.modal.dark {
  background: #323133ea;
  color: #f0f0f0;
  border: 2px solid #444;
}

</style>

