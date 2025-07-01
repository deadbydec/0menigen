<template>
  <div v-if="visible" class="picker-modal">
    <div class="picker-content">
      <h2>Выбери предмет</h2>

      <div v-if="loading" class="loading">Загрузка...</div>
      <div v-else-if="items.length === 0" class="empty">Нет доступных предметов</div>

      <div v-else class="inventory-grid">
        <div
          v-for="item in items"
          :key="item.id"
          class="inventory-wrapper"
          @click="selectItem(item)"
        >
          <div class="inventory-slot">
            <img
              :src="`${STATIC_BASE}/static/goods/${item.product.image}`"
              :alt="item.product.name"
              @error="onImageError"
            />
          </div>
          <div class="item-caption">
            <div class="item-name">{{ item.product.name }}</div>
            <div class="item-rarity" :class="getRarityClass(item.product.rarity)">
              {{ item.product.rarity }}
            </div>
          </div>
        </div>
      </div>

      <div class="buttons">
        <button @click="$emit('close')">❌ Отмена</button>
      </div>
    </div>
  </div>
</template>


<script setup>
import { ref, onMounted, computed } from 'vue'
import { useInventoryStore } from '@/store/inventory'

defineProps({ visible: Boolean })
const emit = defineEmits(['close', 'select'])

const inventoryStore = useInventoryStore()
const items = computed(() => inventoryStore.tradableItems)
const loading = ref(true)
const STATIC_BASE = import.meta.env.VITE_STATIC_URL || 'https://localhost:5002'

function selectItem(item) {
  emit('select', item)
  emit('close')
}

function onImageError(e) {
  e.target.src = `${STATIC_BASE}/static/goods/noimage.png`
}

function getRarityClass(rarity) {
  return `rarity-${rarity?.toLowerCase()}` || 'rarity-common'
}

onMounted(async () => {
  loading.value = true
  await inventoryStore.fetchInventory()
  loading.value = false
})
</script>


<style scoped>
.picker-modal {
  position: fixed;
  inset: 0;
  display: flex;
  justify-content: center;
  align-items: center;
  background: transparent;
  z-index: 1000;
  animation: fadeIn 0.2s ease;

}

.picker-content {
  background: #161616;
  border: 1px solid rgba(255, 255, 255, 0.2);
  border-radius: 16px;
  padding: 20px;
  max-width: 500px;
  width: 100%;
  box-shadow: 0 0 24px rgba(0, 0, 0, 0.5);
  color: #c4c4c4;
  font-family: 'Fira Code', monospace;
  max-height: 80vh;
  overflow-y: auto;
  scale: 90%;
}

.item-rarity {
  font-size: 0.65em;
  opacity: 0.7;
}

.item-name {
  font-size: 0.75em;
  font-weight: bold;
  color: #ddd;
  white-space: nowrap;
  overflow: hidden;
  text-overflow: ellipsis;
}

/* пример: можно подкрасить редкость */
.rarity-common { color: #aaa; }
.rarity-rare   { color: #4faaff; }
.rarity-epic   { color: #c86fff; }
.rarity-legendary { color: gold; }

.item-list {
  display: flex;
  flex-wrap: wrap;
  gap: 12px;
  margin: 14px 0;
}

.item-card {
  flex: 1 1 45%;
  background: #222;
  border: 1px solid #555;
  border-radius: 10px;
  padding: 10px;
  cursor: pointer;
  text-align: center;
  transition: 0.2s ease;
}
.item-card:hover {
  background: #2e2e2e;
}

.item-image {
  width: 60px;
  height: 60px;
  object-fit: contain;
  margin-bottom: 6px;
}

.item-name {
  font-size: 0.85em;
}

.buttons {
  text-align: right;
  margin-top: 12px;
}

button {
  background: #333;
  color: white;
  border: none;
  border-radius: 6px;
  padding: 6px 12px;
  cursor: pointer;
  font-weight: bold;
  transition: 0.2s ease;
}

button:hover {
  background: #444;
}

@keyframes fadeIn {
  from { opacity: 0; transform: scale(0.95); }
  to   { opacity: 1; transform: scale(1); }
}
</style>
