<template>
    <div class="custom-toast-container">
      <div
        v-for="toast in toastStore.toasts"
        :key="toast.id"
        class="custom-toast"
        :class="toast.type"
      >
        {{ toast.message }}
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
    background: rgba(0, 0, 0, 0.9);
    color: white;
    padding: 10px 15px;
    border-radius: 5px;
    box-shadow: 0 2px 8px rgba(0, 0, 0, 0.5);
    max-width: 400px;
    transition: none;
    animation: none;
  }
  </style>
  