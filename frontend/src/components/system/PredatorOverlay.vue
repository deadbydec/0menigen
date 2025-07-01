<template>
  <div v-if="visible" class="predator-overlay" @click="close">
    <img src="/vova_predator.png" alt="Вова Предатор" class="vova-image" />
    <p class="vova-text">ВОТ И ВСЁ, ДРУЖОК... СТАВКА НЕ ПРОШЛА.</p>
  </div>
</template>

<script setup>
import { ref } from 'vue'
const visible = ref(false)

function show() {
  visible.value = true
  setTimeout(() => visible.value = false, 5000)
}
defineExpose({ show }) // 💡 даст доступ к вызову show() снаружи
function close() {
  visible.value = false
}
</script>

<style scoped>
.predator-overlay {
  position: fixed;
  top: 0;
  left: 0;
  z-index: 9999;
  background: rgba(0, 0, 0, 0.85);
  width: 100vw;
  height: 100vh;
  display: flex;
  flex-direction: column;
  justify-content: center;
  align-items: center;
  animation: fadeIn 0.3s ease;
}
.vova-image {
  max-height: 60vh;
  animation: shake 0.4s infinite alternate;
}
.vova-text {
  color: white;
  font-size: 1.8rem;
  margin-top: 20px;
  text-align: center;
}
@keyframes shake {
  0% { transform: translateX(-5px) rotate(-1deg); }
  100% { transform: translateX(5px) rotate(1deg); }
}
@keyframes fadeIn {
  from { opacity: 0; }
  to { opacity: 1; }
}
</style>
