<template>
  <div class="inventory-page">
    <h1>Инвентарь</h1>
    <p class="inventory-count">Всего предметов: {{ inventory.length }}</p>

    <div class="block">
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
    </div>

    <!-- Действия с выбранным предметом -->
    <div v-if="selectedItem" class="global-inventory-actions">
      <p class="selected-label">Выбран: {{ selectedItem.product.name }}</p>
      <div class="inventory-actions">
        <button @click="useItem" class="use-button">Использовать</button>
        
        <!-- Если пользователь Наллвур → кнопка Переработки, иначе Уничтожить -->
        <button v-if="inventoryStore.userRace === 'nullvour'" @click="inventoryStore.recycleItem">
          Переработка
        </button>
        <button v-else @click="inventoryStore.destroyItem">
          Выбросить
        </button>

        <button @click="giftModalOpen = true" class="gift-button">Подарить</button>
        <button @click="sendToVault">В сейф</button>

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
import { onMounted, onUnmounted, computed, ref } from 'vue'
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

async function sendToVault() {
  if (!selectedItem.value) return
  try {
    await inventoryStore.sendToVault(selectedItem.value.id, 1)
    alert("Предмет отправлен в сейф!")
  } catch (err) {
    console.error("Ошибка при отправке в сейф", err)
    alert(err.response?.data?.detail || "Не удалось отправить предмет в сейф")
  }
}

function onImageError(e) {
  e.target.src = `${STATIC_BASE}/static/goods/no_image.png`
}

onMounted(() => fetchInventory())
onUnmounted(() => {
  inventoryStore.selectedItem = null
})

function getRarityClass(rarity) {
  switch (rarity) {
    case 'мусорный': return 'rarity-trash';
    case 'обычный': return 'rarity-common';
    case 'призовой': return 'rarity-prize';
    case 'особый': return 'rarity-special';
    case 'эпический': return 'rarity-epic';
    case 'редкий': return 'rarity-rare';
    case 'легендарный': return 'rarity-legendary';
    case 'уникальный': return 'rarity-unique';
    case 'древний': return 'rarity-elder';
    case 'исчезнувший': return 'rarity-vanished';
    case 'глитчевый': return 'rarity-glitched';
    case 'пустотный': return 'rarity-void';
    default: return '';
  }
}
</script>

<style scoped lang="scss">
/* Убираем лишние стили для body */
html, body {
  margin: 0;
  padding: 0;
  background: #f0f0f0;
  overflow-y: auto; /* Скролл пойдёт по всей странице */
}

/* Блок со всем контентом инвентаря. Ставим масштаб 80%. */
.inventory-page {
  margin: 0 auto;
  padding: 10px;
  transform: scale(0.8);
  transform-origin: top center;
  text-align: center;

  h1 {
    margin: 0 0 15px;
    font-size: 24px;
    font-weight: 700;
  }

  .inventory-count {
    margin-bottom: 10px;
  }
}

/* Сетка, аналогичная магазину */
.inventory-grid {
  display: grid;
  grid-template-columns: repeat(auto-fill, minmax(160px, 1fr));
  gap: 1rem;
  max-width: 1000px;
  margin: 0 auto;
}

/* Карточка предмета */
.inventory-slot {
  position: relative;
  display: flex;
  flex-direction: column;
  align-items: center;
  padding: 6px;
  border: 1px solid #303030;
  border-radius: 9px;
  background-color: #f9f9f9cc;
  transition: transform 0.2s, box-shadow 0.2s;
  text-align: center;
  overflow: hidden;

  &:hover {
    transform: scale(1.05);
    box-shadow: 0 4px 12px rgba(0, 0, 0, 0.3);
  }

  img {
    width: 110px;
    height: 110px;
    object-fit: contain;
    margin-bottom: 3px;
  }

  p {
    font-size: 12px;
    color: #333;
    margin: 2px 0; 
  }
}

/* Название */
.item-name {
  margin: 2px 0;
  font-size: 13px;
  font-weight: 700;
  line-height: 1.2;
  color: #333;
  max-width: 90%;
  word-break: break-word;
}

/* Редкость */
.item-rarity {
  margin: 2px 0;
  font-size: 12px;
  line-height: 1.2;
  font-weight: bold;
  max-width: 90%;
  word-break: break-word;
  background-color: transparent;
  border: none;
}

/* Расцветки редкостей */
.rarity-trash { color: #585858; }
.rarity-common { color: #406374; }
.rarity-prize { color: rgb(255, 76, 201); }
.rarity-special { color: #48e9b3; }
.rarity-rare { color: #20cf46; }
.rarity-epic { color: rgb(131, 37, 238); }
.rarity-legendary { color: rgb(230, 158, 24); }
.rarity-unique { color: rgb(238, 108, 76); }
.rarity-elder { color: rgb(143, 36, 17); }
.rarity-vanished { color: rgb(144, 197, 181); }
.rarity-glitched { color: rgb(136, 93, 255); }
.rarity-void { color: rgb(71, 29, 221); }

/* Выделение выбранного */
.selected-item {
  outline: 2px solid white;
  transform: scale(1.03);
  box-shadow: 0 0 8px rgba(255, 255, 255, 0.3);
}

/* Блок с кнопками */
.inventory-actions {
  margin: 20px auto 0;
  display: flex;
  justify-content: center;
  gap: 20px;
  padding: 10px 0;

  button {
    padding: 10px 20px;
    border: 1px solid transparent;
    border-radius: 10px;
    cursor: pointer;
    font-size: 14px;
    font-weight: bold;
    font-family: 'Fira Code', monospace;
    transition: all 0.2s ease-in-out;
    width: fit-content;
    max-width: 140px;
    box-shadow: 0 2px 6px rgba(0, 0, 0, 0.2);
  }
}

/* Кнопки */
.use-button {
  background-color: #15ce90bd;
  color: white;
  &:hover {
    transform: translateY(-1px);
    box-shadow: 0 4px 10px rgba(0, 0, 0, 0.5);
  }
}

.destroy-button {
  background-color: #000000ab;
  color: white;
  &:hover {
    transform: translateY(-1px);
    box-shadow: 0 4px 10px rgba(0, 0, 0, 0.5);
  }
}

.gift-button {
  background-color: #cea419bd;
  color: white;
  &:hover {
    transform: translateY(-1px);
    box-shadow: 0 4px 10px rgba(0, 0, 0, 0.5);
  }
}
</style>





