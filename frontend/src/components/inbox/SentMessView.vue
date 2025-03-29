<template>
  <teleport to="body">
    <div class="modal-overlay" @click.self="closeModal">
      <div class="modal">
        <h2>📤 Отправлено: {{ formatDate(message.timestamp) }}</h2>
        <p class="recipient">👤 Кому: {{ recipientUsername }}</p>
        <hr />
        <p class="subject"><strong>Тема:</strong> {{ message.subject || 'Без темы' }}</p>
        <div class="content">
          {{ message.content }}
        </div>
        <button class="close-button" @click="closeModal">Закрыть</button>
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
  background: rgba(0,0,0,0.6);
  display: flex;
  justify-content: center;
  align-items: center;
  z-index: 9999; /* Обеспечим, что оверлей выше всего */
}

.modal {
  background: #fff;
  border-radius: 8px;
  padding: 1rem;
  max-width: 500px;
  box-shadow: 0 0 20px rgba(0, 0, 0, 0.3);
}

.subject {
  margin: 1rem 0;
}

.recipient {
  color: #333;
}

.content {
  margin-top: 0.5rem;
  white-space: pre-wrap;
}

.close-button {
  margin-top: 1rem;
  background-color: #000000;
  border: none;
  padding: 0.4rem 0.8rem;
  border-radius: 6px;
  cursor: pointer;
}
</style>
