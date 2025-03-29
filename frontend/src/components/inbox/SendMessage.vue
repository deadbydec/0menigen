<script setup>
import { ref } from "vue";
import { useInboxStore } from "@/store/inbox";

const inboxStore = useInboxStore();
const recipient = ref("");
const message = ref("");
const subject = ref("");

const send = async () => {
  if (!recipient.value || !message.value.trim()) return alert("Введите данные!");
  const response = await inboxStore.sendMessage({
  recipient: recipient.value,
  subject: subject.value,
  content: message.value
})
  if (response.success) {
    recipient.value = "";
    message.value = "";
    alert("Сообщение отправлено!");
  }
};
</script>

<template>
  <div class="send-form">
    <h3>Написать сообщение:</h3>
    
    <input v-model="recipient" placeholder="Кому" class="input" />
    <input v-model="subject" placeholder="Тема" class="input" />
    
    <div class="message-box-wrapper">
    <textarea v-model="message" placeholder="Сообщение" class="textarea"></textarea>
    
    <button @click="send" class="send-btn">
        <i class="fa-solid fa-envelope"></i>
      </button>
  </div>
  </div>
</template>

<style lang="scss" scoped>

.message-box-wrapper {
  position: relative;
}

.message-box-wrapper textarea {
  width: 100%;
  height: 120px;
  resize: none;
  padding: 10px 90px 10px 10px; /* Добавляем паддинг справа под кнопку */
  border-radius: 5px;
}

.send-form {
  display: flex;
  flex-direction: column;
  gap: 10px;
}

.input {
  height: 32px;
  padding: 5px 10px;
  border: 1px solid #999;
  border-radius: 5px;
  background: #ffffffa2;
  font-size: 14px;
}

.textarea {
  width: 100%;
  height: 120px;
  resize: none;
  padding: 10px 40px 10px 10px; // сдвиг под мини кнопку
  border: 1px solid #999;
  border-radius: 5px;
  background: #ffffffa2;
  font-size: 14px;
  box-sizing: border-box;
}

/* Кнопка отправки сообщения */
.send-btn {
  all: unset; /* Убирает стандартные стили */
  position: absolute;
  bottom: 10px;
  right: 10px;
  font-size: 18px;
  cursor: pointer;
  color: #555;
  background: transparent;
  display: flex;
  align-items: center;
  justify-content: center;
  border-radius: 50%;
  padding: 6px;
  transition: background 0.2s ease, transform 0.1s ease;
}

/* Hover-эффект: фон меняется, кнопка немного увеличивается */
.send-btn:hover {
  background: rgba(85, 85, 85, 0.1);
  transform: scale(1.2);
}
</style>