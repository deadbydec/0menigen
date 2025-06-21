<template>
  <div class="custom-toast-container">
    <div
      v-for="toast in toastStore.toasts"
      :key="toast.id"
      class="custom-toast"
      :class="toast.type"
    >
      <span class="toast-message">{{ toast.message }}</span>
      <button class="close-btn" @click="toastStore.removeToast(toast.id)">×</button>
    </div>
  </div>
</template>

<script setup>
import { useToastStore } from '@/store/toast'
const toastStore = useToastStore()
</script>

<style scoped>
.custom-toast-container {
  position: fixed;
  top: 70px;
  left: 50%;
  transform: translateX(-50%);
  z-index: 9999;
  display: flex;
  flex-direction: column;
  gap: 8px;
}

.custom-toast {
  display: flex;
  justify-content: space-between;
  align-items: center;
  background: rgba(0, 0, 0, 0.9);
  color: white;
  padding: 10px 15px;
  border-radius: 6px;
  box-shadow: 0 2px 8px rgba(0, 0, 0, 0.5);
  max-width: 400px;
  animation: fadeIn 0.25s ease-out;
  font-family: 'Fira Code', monospace;
  position: relative;
}

.toast-message {
  flex: 1;
  padding-right: 10px;
  word-break: break-word;
}

.close-btn {
  background: none;
  border: none;
  color: #aaa;
  font-size: 18px;
  cursor: pointer;
  transition: color 0.2s ease;
}

.close-btn:hover {
  color: white;
}

.custom-toast.success {
  background: linear-gradient(90deg, #0cb17c, #055e4d);
}
.custom-toast.error {
  background: linear-gradient(90deg, #ae1c1c, #6c0d0d);
}

@keyframes fadeIn {
  from { opacity: 0; transform: translateY(-10px); }
  to   { opacity: 1; transform: translateY(0); }
}
</style>
