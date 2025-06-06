<template>
  <div class="inv-wrapper">
  <div class="inventory-page">
    <h1>Инвентарь</h1>
    <p class="inventory-count">Всего предметов: {{ inventory.length }}</p>

    <!-- ▸ GRID WRAPPER -->
    <div class="block">
      <div v-if="inventory.length" class="inventory-grid">
        <div
          v-for="item in inventory"
          :key="item.id"
          class="inventory-slot"
          @click="handleItemClick(item)"
          :class="{
            'selected-item': selectedItem && selectedItem.id === item.id,
            'egg-ready':   item.type === 'creature' && isReadyToHatch(item),
            'egg-running': item.type === 'creature' && item.incubation && !isReadyToHatch(item)
          }"
          v-tooltip="item.product.description"
        >
          <!-- ▸ ICON -->
          <img
            :src="`${STATIC_BASE}/static/goods/${item.product.image}`"
            :alt="item.product.name"
            @error="onImageError"
          />

          <!-- ▸ TIMER OVERLAY -->
          <div
            v-if="item.type === 'creature' && item.incubation && !isReadyToHatch(item)"
            class="egg-timer-overlay"
          >
            {{ formatRemaining(item.incubation.hatch_at) }}
          </div>

          <!-- ▸ CAPTIONS -->
          <div class="item-name">{{ item.product.name }}</div>
          <div class="item-rarity" :class="getRarityClass(item.product.rarity)">
            {{ item.product.rarity }}
          </div>
        </div>
      </div>
      <p v-else>Инвентарь пуст.</p>
    </div>

    <!-- ▸ GLOBAL ACTIONS -->
    <div
  v-if="selectedItem && !(isEggRunning || isEggReady)"
  class="global-inventory-actions"
>
  <p class="selected-label">
    Выбран: {{ selectedItem.product.name }}
  </p>

  <div class="inventory-actions">
    <!-- если косметика — показываем только «в гардероб» -->
  <button
    v-if="selectedItem.product.product_type === 'косметический'"
    class="wardrobe-button"
    @click="sendToWardrobe(selectedItem.id)"
  >
    В гардероб
  </button>
    <!-- единая кнопка (инкубация / использование) -->
    <button
    v-else
      class="use-button"
      :disabled="isEggRunning"
      @click="handlePrimary"
    >
      {{ primaryLabel }}
    </button>

    

        <!-- переработка / выбросить -->
        <button
          v-if="inventoryStore.userRace === 'nullvour'"
          @click="inventoryStore.recycleItem"
        >
          Переработка
        </button>
        <button v-else @click="inventoryStore.destroyItem">Выбросить</button>

        <!-- подарок / сейф -->
        <button @click="giftModalOpen = true" class="gift-button">Подарить</button>
        <button @click="sendToVault">В&nbsp;сейф</button>
        </div>
        <GiftModal
          v-if="giftModalOpen"
          :visible="giftModalOpen"
          :item-id="selectedItem?.id"
          :item-name="selectedItem?.product.name"
          @close="giftModalOpen = false"
        />
      </div>
    </div>

    <!-- ▸ HATCH MODAL -->
    <HatchModal
  :visible="showHatchModal"
  :incubation-id="selectedItem?.incubation?.id"
  @close="showHatchModal = false"
  @hatched="handleHatched"
/>
  </div>

</template>

<script setup>
import { ref, computed, onMounted, onUnmounted } from 'vue'
import { useRouter } from 'vue-router'
import { useInventoryStore } from '@/store/inventory'
import GiftModal from './GiftModal.vue'
import HatchModal from '@/components/HatchModal.vue'
import api from '@/utils/axios'
import { useWardrobeStore } from '@/store/wardrobe'
const wardrobeStore = useWardrobeStore()
import { useToastStore } from '@/store/toast'

/* ▸ CONSTS */
const STATIC_BASE = import.meta.env.VITE_STATIC_URL || 'https://localhost:5002'

const toast = useToastStore()
/* ▸ STORE + STATE */
const inventoryStore = useInventoryStore()
const inventory     = computed(() => inventoryStore.inventory)
const selectedItem  = computed(() => inventoryStore.selectedItem)   // 💡 только читаем

/* ▸ UI FLAGS */
const giftModalOpen  = ref(false)
const showHatchModal = ref(false)
const petName        = ref('')

/* ▸ TIMER TICK (для овера модуля) */
const nowTick = ref(Date.now())
let timerId
onMounted(() => {
  inventoryStore.fetchInventory()
  timerId = setInterval(() => (nowTick.value = Date.now()), 1000)
})
onUnmounted(() => {
  clearInterval(timerId)
  inventoryStore.selectItem(null)
})

/* ▸ HELPERS & COMPUTEDS */
function isReadyToHatch(item) {
  return (
    item &&
    item.type === 'creature' &&
    item.incubation &&
    new Date(item.incubation.hatch_at).getTime() <= nowTick.value
  )
}

const isEgg        = computed(() => selectedItem.value?.type === 'creature')
const isEggRunning = computed(
  () => isEgg.value && selectedItem.value.incubation && !isReadyToHatch(selectedItem.value)
)
const isEggReady = computed(() => isEgg.value && isReadyToHatch(selectedItem.value))

const primaryLabel = computed(() => {
  if (selectedItem.value?.product?.product_type === "cosmetic") {
    return "В гардероб"
  }

  if (isEgg.value && !selectedItem.value.incubation) return 'Инкубировать'
  if (isEggRunning.value) return 'Вылупление…'
  return 'Использовать'
})

function formatRemaining(hatchISO) {
  const diff = Math.max(0, Math.floor((new Date(hatchISO) - nowTick.value) / 1000))
  const m = String(Math.floor(diff / 60)).padStart(2, '0')
  const s = String(diff % 60).padStart(2, '0')
  return `${m}:${s}`
}

/* ▸ CLICK HANDLERS */
function handleItemClick(item) {
  inventoryStore.selectItem(item)

  if (item.type === 'creature' && isReadyToHatch(item)) {
    petName.value = ''
    showHatchModal.value = true
  }
}

function handleHatched(data) {
  inventoryStore.selectItem(null)
  inventoryStore.fetchInventory()
}

async function handlePrimary () {
  if (!selectedItem.value) return

  // 💄 КОСМЕТИКА → в гардероб
  if (selectedItem.value?.product?.product_type === "cosmetic")
 {
    await sendToWardrobe(selectedItem.value.id)
    return
  }

  // 🥚 ИНКУБАЦИЯ
  if (isEgg.value && !selectedItem.value.incubation) {
    await inventoryStore.incubateItem()
  }

  // 🧪 ОБЫЧНОЕ ИСПОЛЬЗОВАНИЕ
  else if (!isEgg.value) {
    await inventoryStore.useItem()
  }
}


async function sendToVault() {
  if (!selectedItem.value) return
  try {
    await inventoryStore.sendToVault(selectedItem.value.id, 1)
    alert('Предмет отправлен в сейф!')
  } catch (err) {
    console.error('Ошибка при отправке в сейф', err)
    alert(err.response?.data?.detail || 'Не удалось отправить предмет в сейф')
  }
}

const sendToWardrobe = async (itemId) => {
  try {
    await wardrobeStore.addToWardrobe(itemId)
    toast.addToast('🎽 Отправлено в гардероб!', { type: 'success' })
  } catch (err) {
    toast.addToast('❌ Не удалось добавить в гардероб', { type: 'error' })
  }
}


function onImageError(e) {
  e.target.src = `${STATIC_BASE}/static/goods/no_image.png`
}

/* ▸ HATCH */
const router = useRouter()
async function submitHatch() {
  try {
    const { data } = await api.post(
      '/api/pets/hatch',
      { name: petName.value },
      { withCredentials: true }
    )
    showHatchModal.value = false
    inventoryStore.selectItem(null)
    await inventoryStore.fetchInventory()
    router.push(`/pet/${data.id}`)
  } catch (err) {
    console.error(err)
    alert('Не удалось вылупить яйцо :(')
  }
}

/* ▸ COLOR BY RARITY */
function getRarityClass(rarity) {
  switch (rarity) {
    case 'мусорный':   return 'rarity-trash'
    case 'обычный':    return 'rarity-common'
    case 'призовой':   return 'rarity-prize'
    case 'особый':     return 'rarity-special'
    case 'эпический':  return 'rarity-epic'
    case 'редкий':     return 'rarity-rare'
    case 'легендарный':return 'rarity-legendary'
    case 'уникальный': return 'rarity-unique'
    case 'древний':    return 'rarity-elder'
    case 'исчезнувший':return 'rarity-vanished'
    case 'глитчевый':  return 'rarity-glitched'
    case 'пустотный':  return 'rarity-void'
    default:           return ''
  }
}
</script>

<style scoped lang="scss">
/* Убираем лишние стили для body */

$glass-bg: rgba(255, 255, 255, 0.05);
$glass-border: rgba(255, 255, 255, 0.1);
$glass-hover: rgba(255, 255, 255, 0.08);
$accent: #d6dcdda6;


body {
  overflow-y: scroll;
  height: 100vh;
}

html {
  scroll-behavior: smooth;
}

/* Убираем дефолтные стили */
html, body {
  margin: 0;
  padding: 0;

  font-family: 'JetBrains Mono', monospace;
}


/* Блок со всем контентом инвентаря. Ставим масштаб 80%. */
.inv-wrapper {
  background:rgba(38, 32, 39, 0.48);
  overflow-y: auto;
  border: 1px solid rgb(36, 35, 37);
  margin: 0 auto;
  padding: 10px;
  border-radius: 17px;


  transform-origin: top center;
  text-align: center;
  font-family: 'JetBrains Mono', monospace;

  /* Скрываем скроллбар, но сохраняем прокрутку */
  scrollbar-width: none; /* Firefox */
  -ms-overflow-style: none; /* IE и Edge */

  &::-webkit-scrollbar {
    display: none; /* Chrome, Safari */
  }
}

.inventory-page {
  /* Снимаем лишние отступы, ставим масштаб 80% */
  margin: 0 auto;
  padding: 10px;
  transform: scale(0.8);
  transform-origin: top center;
  text-align: center;
  font-family: 'JetBrains Mono', monospace;
}

h1 {
  background: rgba(0, 0, 0, 0.4);
  padding: 6px 14px;

  border-radius: 12px;
  display: inline-block;


  font-family: 'JetBrains Mono', monospace;
}

.inventory-count {
    margin-bottom: 10px;
  }


/* Сетка, аналогичная магазину */
.inventory-grid {
  display: grid;
  font-family: 'JetBrains Mono', monospace;
  grid-template-columns: repeat(auto-fill, minmax(160px, 1fr));
  gap: 1rem;
  max-width: 1000px;
  margin: 0 auto;
}

/* Карточка предмета */
.inventory-slot {
  will-change: transform;
  position: relative;
  font-family: 'JetBrains Mono', monospace;
  display: flex;
  flex-direction: column;
  align-items: center;
  padding: 6px;
  border: 1px solid #2e2c2c;
  border-radius: 9px;
  background:linear-gradient(80deg, #cfcdceb2,rgba(197, 228, 226, 0.664));
  transition: transform 0.2;
  text-align: center;
  overflow: hidden;

  &:hover {
    transform: scale(1.05);
  }

  img {
    width: 110px;
    height: 110px;
    object-fit: contain;
    margin-bottom: 3px;
    cursor: pointer;
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

  }
}

/* Кнопки */
.use-button {
  background-color: #15ce90bd;
  color: white;
  &:hover {
    transform: translateY(-1px);

  }
}

.destroy-button {
  background-color: #000000ab;
  color: white;
  &:hover {
    transform: translateY(-1px);

  }
}

.gift-button {
  background-color: #cea419bd;
  color: white;
  &:hover {
    transform: translateY(-1px);

  }
}

/* всегда относительный контекст — для любых оверлеев */
.inventory-slot {
  position: relative;          // 🔑 перемещено из .egg-running
}

/* ───── 1. Визуальная «маска», когда яйцо инкубируется ───── */
.inventory-slot.egg-running::after,
.inventory-slot.egg-ready::after {
  content: '';
  position: absolute;
  inset: 0;                    // top:0; right:0; bottom:0; left:0;
  background: rgba(0, 0, 0, 0.45);   // полупрозрачный слой
  backdrop-filter: blur(1px);        // лёгкое размытие
  border-radius: inherit;
  z-index: 2;                  // выше картинки, ниже таймера
}

/* таймер рисуем поверх маски */
.egg-timer-overlay {
  z-index: 3;                  // было 2 — увеличили, чтобы оказаться над ::after
}
</style>





