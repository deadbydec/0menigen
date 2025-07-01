<template>
  <div class="modal-overlay">
    <div class="modal-body">
    
      <component :is="gameComponent" @close="$emit('close')" />
    </div>
  </div>
</template>

<script setup>
defineProps({
  gameComponent: Object
})
</script>

<style scoped>
.modal-overlay {
  position: fixed;
  inset: 0;
  background: rgba(0, 0, 0, 0.85);
  display: flex;
  justify-content: center;
  align-items: center;
  z-index: 9999;
}
.modal-body {
  background: #111;
  border: 1px solid rgb(196, 196, 196);
  padding: 20px;
  border-radius: 16px;
  position: relative;
  max-width: 95vw;
  height: 700px;
  overflow: auto;
}
.close-button {
  position: absolute;
  top: 10px;
  right: 14px;
  background: none;
  color: white;
  font-size: 24px;
  border: none;
  cursor: pointer;
}
</style>
