<template>
  <teleport to="body">
    <div class="modal-overlay" @click.self="closeModal">
      
      <div class="modal">
        <button class="close-button" @click="closeModal"><i class="fa-solid fa-xmark"></i></button>
        <p class="timestamp">{{ formatDate(message.timestamp) }}</p>
        
        <p class="recipient"><strong>Кому:</strong> {{ message.recipient }}</p>
        
        <p class="subject"><strong>Тема:</strong> {{ message.subject || '-' }}</p>
        <hr />
        <div class="content">
          {{ message.content }}
        </div>
        
      </div>
    </div>
  </teleport>
</template>

<script setup>
const props = defineProps({
  message: Object,
  recipientUsername: String,
});

const emit = defineEmits(['close']);

function closeModal() {
  emit('close');
}

function formatDate(timestamp) {
  return new Date(timestamp).toLocaleString("ru-RU");
}
</script>

<style scoped>
.modal-overlay {
  position: fixed;
  top: 0;
  left: 0;
  width: 100%;
  height: 100%;
  display: flex;
  justify-content: center;
  align-items: center;
  z-index: 9999; /* Обеспечим, что оверлей выше всего */
}

  .modal {
  background: #fff;
  border-radius: 8px;
  padding: 1rem;
  color: #333;
  width: 400px;
  max-height: 600px;
  min-height: 300px;
  box-shadow: 0 0 30px rgba(0, 0, 0, 0.3);
}

.subject {
  color: #333;
  margin: 1rem 0;
}

.recipient {
  color: #333;
}

.content {
  margin-top: 0.5rem;
  white-space: pre-wrap;
  color: #333;
}

.close-button {
  margin-top: 1rem;
  background: transparent;
  position:fixed;
  border: none;
  color: #342d38;
  width: 0px;
  font-size: 22px;
  height: 0px;
  margin-left: 360px;
  margin-top: 0px;
  border-radius: 6px;
  cursor: pointer;
  :hover {
  border-radius: 10px;
  transform: scale(1.2);
}
}

  .timestamp {
    color: #666;
    font-size: 0.8rem;
  }
</style>
