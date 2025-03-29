<template>
  <div class="inventory-page">
    <h1>Инвентарь</h1>
    <p class="inventory-count">Всего предметов: {{ inventory.length }}</p>

    <div class="inventory-grid" v-if="inventory.length">
      <div 
        v-for="item in inventory" 
        :key="item.id" 
        class="inventory-slot"
        @click="selectItem(item)"
        :class="{ 'selected-item': selectedItem && selectedItem.id === item.id }"
        v-tooltip="item.product.description"
        
      >
        <img 
          :src="`${STATIC_BASE}/static/goods/${item.product.image}`" 
          :alt="item.product.name" 
          @error="onImageError"
        />
        <div class="item-name">{{ item.product.name }}</div>
        <p>Кол-во: {{ item.quantity }}</p>
        <div class="item-rarity" :class="getRarityClass(item.product.rarity)">
          {{ item.product.rarity }}
        </div>
      </div>
    </div>

    <div v-else>
      <p>Инвентарь пуст.</p>
    </div>

    <!-- ВНЕ v-for! ОДИН раз! -->
    <div v-if="selectedItem" class="global-inventory-actions">
      <p class="selected-label">Выбран: {{ selectedItem.product.name }}</p>
      <div class="inventory-actions">
        <button @click="useItem" class="use-button">Использовать</button>
        <button @click="destroyItem" class="destroy-button">Уничтожить</button>
        <button @click="giftModalOpen = true" class="gift-button">Подарить</button>


        <GiftModal
    v-if="giftModalOpen"
    :visible="giftModalOpen"
    :item-id="selectedItem?.id"
    :item-name="selectedItem?.product.name"
    @close="giftModalOpen = false"
  />
      </div>
    </div>

  </div>
</template>

<script setup>
import { onMounted, onUnmounted, computed } from 'vue'
import { useInventoryStore } from '@/store/inventory'
import GiftModal from "./GiftModal.vue"

const STATIC_BASE = import.meta.env.VITE_STATIC_URL || 'https://localhost:5002'

const inventoryStore = useInventoryStore()
const inventory = computed(() => inventoryStore.inventory)
const selectedItem = computed(() => inventoryStore.selectedItem)
const fetchInventory = inventoryStore.fetchInventory
const selectItem = inventoryStore.selectItem
const useItem = inventoryStore.useItem
const destroyItem = inventoryStore.destroyItem
const giftModalOpen = ref(false)


function onImageError(e) {
  e.target.src = `${STATIC_BASE}/static/goods/no_image.png`
}

onMounted(() => fetchInventory())

onUnmounted(() => {
  inventoryStore.selectedItem = null
})

function getRarityClass(rarity) {
  switch (rarity) {
    case 'обычный': return 'rarity-common';
    case 'особый': return 'rarity-special';
    case 'редкий': return 'rarity-rare';
    case 'легендарный': return 'rarity-legendary';
    default: return '';
  }
}
</script>

<style scoped>
html,
body {
  height: 100%;
  display: flex;
  flex-direction: column;
}

.inventory-page {
  padding: 20px;
  text-align: center;
}

.inventory-count {
  margin-bottom: 20px;
}

/* Сетка инвентаря, аналогичная магазину, максимум 5 карточек в ряду */
.inventory-grid {
  display: grid;
  grid-template-columns: repeat(auto-fill, minmax(200px, 1fr));
  gap: 1rem;
  max-width: 1000px; /* например, чтобы максимум умещалось 5 */
}

/* Карточка предмета */
.inventory-slot {
  position: relative;
  display: flex;
  flex-direction: column;
  align-items: center;
  justify-content: space-between;
  width: 150px;
  height: 180px;
  padding: 10px;
  border: 1px solid #ccc;
  border-radius: 8px;
  background-color: #f9f9f9;
  transition: transform 0.2s, box-shadow 0.2s;
  text-align: center;
  overflow: hidden;
}

.inventory-slot:hover {
  box-shadow: 0 0 10px rgba(0, 0, 0, 0.3);
}

.item-rarity {
  font-weight: bold;
  padding: 4px 6px;
  border-radius: 4px;
  text-align: center;
  margin-top: 6px;
  font-size: 12px;
  background-color: transparent; /* или убери вообще */
  border: none; /* чтобы не было визуального шума */
}

/* Кастомные классы по редкости */
.rarity-common {
  color: #5a5959;
}
.rarity-special {
  color: #13b383;
}
.rarity-rare {
  color: #88c3ff;
}
.rarity-legendary {
  color: gold;
}

/* Выделение */
.selected-item {
  outline: 2px solid white;
  transform: scale(1.03);
  box-shadow: 0 0 8px rgba(255, 255, 255, 0.3);
}

.inventory-slot img {
  width: 80px;
  height: 80px;
  object-fit: contain;
  margin-bottom: 5px;
}

.item-name {
  word-wrap: break-word;
  overflow-wrap: break-word;
  white-space: normal;
  text-align: center;
  display: block;
  color: #333;
  font-weight: bold;
  font-size: 14px;
  max-width: 160px;
}


.inventory-slot p {
  font-size: 12px;
  color: #333;
}

/* Блок кнопок, появляющийся при выделении */
.inventory-actions {
  margin: 20px auto 0;
  display: flex;
  justify-content: center;
  gap: 20px;
  padding: 10px 0;
}

.inventory-actions button {
  padding: 10px 20px;
  border: 1px solid transparent;
  border-radius: 10px;
  cursor: pointer;
  font-size: 14px;
  font-weight: bold;
  font-family: 'Fira Code', monospace;
  transition: all 0.2s ease-in-out;
  width: fit-content; /* 💥 УБИВАЕМ ширину */
  max-width: 140px; /* На всякий пожарный ограничим */
  box-shadow: 0 2px 6px rgba(0,0,0,0.2);
}

:deep(.v-popper__inner) {
  background: rgba(15, 15, 20, 0.95);
  color: #f0f0f0;
  font-family: 'Fira Code', monospace;
  font-size: 13px;
  padding: 8px 12px;
  border-radius: 6px;
  border: 1px solid rgba(255, 255, 255, 0.1);
  box-shadow: 0 0 12px rgba(0, 0, 0, 0.5);
  max-width: 240px;
  white-space: pre-wrap;
  line-height: 1.4;
  pointer-events: none;
  user-select: none;
}

:deep(.v-popper__arrow-container) {
  display: none;
}

/* Использовать */
.use-button {
  background-color: #15ce90bd;
  color: white;
}

.use-button:hover {
  transform: translateY(-1px);
  box-shadow: 0 4px 10px rgba(0, 0, 0, 0.5);
}

/* Уничтожить */
.destroy-button {
  background-color: #000000ab;
  color: white;
}

.destroy-button:hover {
  transform: translateY(-1px);
  box-shadow: 0 4px 10px rgba(0, 0, 0, 0.5);
}

.gift-button {
  background-color: #cea419bd;
  color: white;
}

.gift-button:hover {
  transform: translateY(-1px);
  box-shadow: 0 4px 10px rgba(0, 0, 0, 0.5);
}


</style>



