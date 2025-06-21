<template>
    <pre>{{ JSON.stringify(filteredItems?.value, null, 2) }}</pre>
  <div v-if="visible" class="gift-modal">
    <div class="gift-modal-content">
      <h3>Приручить спутника</h3>
      <p style="margin-bottom: 10px">Выберите предмет-компаньон из инвентаря:</p>

      <div v-if="filteredItems.length" class="item-list">
        <div
          v-for="item in filteredItems"
          :key="item.id"
          class="inventory-item"
          @click="selectItem(item)"
        >
          <img :src="getItemIcon(item.image)" class="item-icon" />
          

          <span>{{ item.name }}</span>
        </div>
      </div>
      <p v-else style="margin-top: 10px">В инвентаре нет спутников 🥲</p>

      <div class="gift-modal-buttons" style="margin-top: 12px">
        <button @click="$emit('close')" class="destroy-button">Закрыть</button>
      </div>
    </div>
  </div>
</template>

<script setup>
import { computed, watch } from 'vue'
import { useInventoryStore } from '@/store/inventory'
import api from "@/utils/axios"

const props = defineProps({
  visible: Boolean,
  petId: Number
})
const emit = defineEmits(['close', 'updated'])

const inventoryStore = useInventoryStore()

// 🔎 отфильтрованные предметы-компаньоны
const filteredItems = computed(() =>
  Array.isArray(inventoryStore.inventory)
    ? inventoryStore.inventory.filter(i =>
        i.product?.types?.includes('companion')
      )
    : []
)

const getItemIcon = (filename) =>
  `${import.meta.env.VITE_STATIC_URL || 'https://localhost:5002'}/static/goods/${filename}`

async function selectItem(item) {
  try {
    await api.post(`/pets/${props.petId}/companion`, {
      product_id: item.product_id  // 🎯 именно это поле!
    })
    emit('updated')
  } catch (e) {
    console.warn('Не удалось приручить:', e)
  } finally {
    emit('close')
  }
}

watch(
  () => props.visible,
  async (visible) => {
    if (visible) {
      await inventoryStore.fetchInventory()
    }
  }
)
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

.item-list {
  max-height: 240px;
  overflow-y: auto;
  margin: 12px 0;
  display: flex;
  flex-direction: column;
  gap: 8px;
}

.inventory-item {
  display: flex;
  align-items: center;
  gap: 10px;
  padding: 6px 10px;
  background: rgba(255, 255, 255, 0.05);
  border-radius: 6px;
  cursor: pointer;
  transition: 0.2s ease;
}
.inventory-item:hover {
  background: rgba(255, 255, 255, 0.15);
}

.item-icon {
  width: 32px;
  height: 32px;
  object-fit: contain;
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
