<template>
  <div v-if="visible" class="gift-modal">
    <div class="gift-modal-content">
      <h3>{{ item?.name || 'Предмет' }}</h3>
      <p style="margin-bottom: 10px">Вы действительно хотите подобрать этот предмет?</p>


      <div class="gift-modal-buttons" style="margin-top: 12px">
        <button @click="confirmPickup" class="use-button">Подобрать</button>
        <button @click="$emit('close')" class="destroy-button">Отмена</button>
      </div>
    </div>
  </div>
</template>

<script setup>
import { useLandfillStore } from '@/store/landfill'
const landfill = useLandfillStore()

const props = defineProps({
  visible: Boolean,
  item: Object
})

const emit = defineEmits(['close'])

async function confirmPickup() {
  if (!props.item?.id) return

  try {
    await landfill.pickupItem(props.item)
  } finally {
    emit('close')
  }
}


</script>

<style scoped>
.gift-modal {
  position: fixed;
  inset: 0;
  display: flex;
  align-items: center;
  justify-content: center;
  z-index: 1000;
  animation: fadeInBg 0.3s ease forwards;
  background: rgba(0, 0, 0, 0.6);
}

.gift-modal-content {
  background: rgb(24, 24, 24);
  border-radius: 12px;
  color: #fff;
  padding: 20px 24px;
  min-width: 300px;
  max-width: 400px;
  box-shadow: 0 0 20px rgba(0, 0, 0, 0.5);
  animation: scaleIn 0.25s ease forwards;
  text-align: center;
  font-family: 'Fira Code', monospace;
}

@keyframes scaleIn {
  0%   { transform: scale(0.9); opacity: 0; }
  100% { transform: scale(1);   opacity: 1; }
}

.use-button {
  background: linear-gradient(135deg, #22ccb0, #034b3bbd);
  color: #fff;
  border: none;
  max-width: 150px;
  padding: 8px 12px;
  border-radius: 6px;
  margin: 0 6px;
  cursor: pointer;
}

.destroy-button {
  background: linear-gradient(135deg, #444, #000000ab);
  color: #fff;
  border: none;
  max-width: 150px;
  padding: 8px 12px;
  border-radius: 6px;
  margin: 0 6px;
  cursor: pointer;
}

.use-button:hover,
.destroy-button:hover {
  transform: scale(1.03);
}
</style>
