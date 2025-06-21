<template>
    <div v-if="visible" class="gift-modal">
      <div class="gift-modal-content">
        <h3>Кому подарить "{{ itemName }}"?</h3>
        <input v-model="username" placeholder="Введите ник получателя" />
        <div class="gift-modal-buttons">
          <button @click="confirmGift" class="use-button">Отправить</button>
          <button @click="$emit('close')" class="destroy-button">Отмена</button>
        </div>
      </div>
    </div>
  </template>
  
  <script setup>
  import { ref, watch } from 'vue'
  import api from "@/utils/axios";
  
  const props = defineProps({
    visible: Boolean,
    itemId: Number,
    itemName: String
  })
  
  const emit = defineEmits(['close'])
  
  const username = ref('')
  
  async function confirmGift() {
    if (!username.value || !props.itemId) return
  
    try {
      const res = await api.post(`/gift/${props.itemId}`, {
        recipient_username: username.value
      })
      alert(res.data.message)
      emit('close')
      username.value = ''
    } catch (err) {
      alert(err.response?.data?.detail || 'Ошибка при отправке подарка')
    }
  }
  </script>
  
  <style scoped>
  /* Обёртка подложки */
  .gift-modal {
    position: fixed;
    inset: 0; /* top:0, left:0, right:0, bottom:0 */
    display: flex;
    align-items: center;
    justify-content: center;
    z-index: 1000;
    animation: fadeInBg 0.3s ease forwards;
  }
  

  
  /* Контент самой модалки */
  .gift-modal-content {
    position: relative;
    background: rgb(24, 24, 24);
    border-radius: 12px;
    padding: 20px 24px;
    min-width: 300px;
    max-width: 400px;
    box-shadow: 0 0 20px rgba(0, 0, 0, 0.5);
    animation: scaleIn 0.25s ease forwards;
    text-align: center;
    font-family: 'Fira Code', monospace;
  }
  
  /* Анимация появления контента (легкое масштабирование) */
  @keyframes scaleIn {
    0%   { transform: scale(0.9); opacity: 0; }
    100% { transform: scale(1);   opacity: 1; }
  }
  
  /* Поле ввода */
  .gift-modal-content input {
    display: block;
    width: 90%;
    margin: 15px auto;
    padding: 10px;
    font-family: inherit;
    font-size: 14px;
    background: #1e1e1e;
    border: 1px solid #444;
    border-radius: 6px;
    color: #ccc;
  }
  

  
  /* Кнопка "Отправить" */
  .use-button {
    background: linear-gradient(135deg, #22ccb0, #034b3bbd);
    color: #fff;
    border: none;
    max-width: 150px;
  }
  
  
  /* Кнопка "Отмена" */
  .destroy-button {
    background: linear-gradient(135deg, #444, #000000ab);
    color: #fff;
    border: none;
    max-width: 150px;
  }
  
  .use-button:hover {
    transition: transform 0.2;

  }
  
  .destroy-button:hover {
    transition: transform 0.2;

  }
  
  /* Кнопка закрытия (иконка в углу, если захочешь) */
  .close-modal-btn {
    position: absolute;
    top: 12px;
    right: 14px;
    background: transparent;
    color: #aaa;
    border: none;
    font-size: 18px;
    cursor: pointer;
    transition: color 0.2s;
  }
  .close-modal-btn:hover {
    color: #fff;
  }


.gift-modal-buttons:focus,
.gift-modal-buttons:active {
  outline: none !important;
  box-shadow: none !important;
}
  </style>
  
  