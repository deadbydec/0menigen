<script setup>
import { ref, computed, onMounted, onUnmounted } from 'vue'
import { useRouter } from 'vue-router'
import { useInventoryStore } from '@/store/inventory'
import GiftModal from './GiftModal.vue'
import HatchModal from '@/components/HatchModal.vue'
import api from '@/utils/axios'
import { useWardrobeStore } from '@/store/wardrobe'
import { useToastStore } from '@/store/toast'
import { useTooltipStore } from '@/store/tooltipStore'
import ReadForModal from './ReadForModal.vue'

const wardrobeStore = useWardrobeStore()

const tooltip = useTooltipStore()
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
  if (selectedItem.value?.product?.product_type === "book") return "Прочитать"

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
  if (item.state === 'auction') return
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

    // Удаляем предмет из инвентаря вручную
    inventoryStore.inventory = inventoryStore.inventory.filter(item => item.id !== itemId)

    // Сброс выбора
    inventoryStore.selectItem(null)

    toast.addToast('🎽 Отправлено в гардероб!', { type: 'success' })
  } catch (err) {
    toast.addToast('❌ Не удалось добавить в гардероб', { type: 'error' })
  }
}



function onImageError(e) {
  e.target.src = `${STATIC_BASE}/static/goods/noimage.png`
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

//const wrapperMarginTop = computed(() => {
 // const count = inventory.value.length

 // if (count > 50) return "1700px"
 // if (count > 45) return "1500px"
 // if (count > 40) return "1300px"
 // if (count > 35) return "1100px"
 // if (count > 30) return "900px"
 // if (count > 25) return "700px"
 // if (count > 20) return "500px"
 // if (count > 15) return "300px"
 // if (count > 10) return "100px"
 // if (count > 5) return "50px"
 // return "50px"
//})

const showBookModal = ref(false)
const allMyPets = ref([])
const availablePetsToRead = computed(() =>
  allMyPets.value.filter(pet =>
    !pet.read_books?.includes(selectedItem.value?.product?.custom?.unique_read_id)
  )
)

async function openBookModal() {
  try {
    const { data } = await api.get('/pets/') // или свой endpoint
    allMyPets.value = data
    showBookModal.value = true
  } catch (err) {
    toast.addToast('Ошибка загрузки питомцев', { type: 'error' })
  }
}

async function readBook(petId) {
  try {
    const result = await inventoryStore.useBookOnPet(petId, selectedItem.value.product_id)
    toast.addToast(result.message, { type: 'success' })
    showBookModal.value = false
    selectedItem.value = null
    await inventoryStore.fetchInventory()
  } catch (err) {
    toast.addToast(err.response?.data?.detail || 'Ошибка при чтении книги', { type: 'error' })
  }
}


</script>




<template>
  <div class="page-inner">
    
    <div class="inventory-layout">
        <!-- 🧷 ПАНЕЛЬ С ДЕЙСТВИЯМИ (СЛЕВА) -->
        <div
          class="inventory-actions-panel"
          v-if="selectedItem && selectedItem.state !== 'auction' && !(isEggRunning || isEggReady)"
        >
          <p class="selected-label">
            Выбрано: {{ selectedItem.product.name }}
          </p>

          <div class="inventory-actions">
            <button
              v-if="selectedItem.product.product_type === 'косметический'"
              class="ghost-button"
              @click="sendToWardrobe(selectedItem.id)"
            >
              В гардероб
            </button>

            <button
  v-else-if="selectedItem.product.product_type?.toLowerCase() === 'книга'"
  class="ghost-button"
  @click="openBookModal"
>
  Прочитать
</button>

<button
  v-else
  class="ghost-button"
  :disabled="isEggRunning"
  @click="handlePrimary"
>
  {{ primaryLabel }}
</button>


            <button
              v-if="inventoryStore.userRace === 'nullvour'"
              @click="inventoryStore.recycleItem"
              class="ghost-button"
            >
              Переработка
            </button>
            <button
              v-else
              @click="inventoryStore.destroyItem"
              class="ghost-button"
            >
              Выбросить
            </button>

            <button @click="giftModalOpen = true" class="ghost-button">
              Подарить
            </button>
            <button @click="sendToVault" class="ghost-button">
              В&nbsp;сейф
            </button>
          </div>
    </div>
    <!-- ▸ ОСНОВНОЙ БЛОК ИНВЕНТАРЯ -->
    
    <div class="inv-wrapper" :style="{ marginTop: wrapperMarginTop }">
      <h1>Инвентарь</h1>
      <p class="inventory-count">Всего предметов: {{ inventory.length }}/50</p>

      

        <!-- 🧩 СЕТКА ПРЕДМЕТОВ -->
        <div v-if="inventory.length" class="inventory-grid">
          <div
            v-for="item in inventory"
            :key="item.id"
            class="inventory-wrapper"
          >
            <!-- ▸ КАРТОЧКА ПРЕДМЕТА -->
            <div
              class="inventory-slot"
              @click="handleItemClick(item)"
              @mouseenter="(e) => tooltip.show(item.product.description, e)"
              @mouseleave="tooltip.hide()"
              :class="{
                'selected-item': selectedItem && selectedItem.id === item.id,
                'egg-ready':   item.type === 'creature' && isReadyToHatch(item),
                'egg-running': item.type === 'creature' && item.incubation && !isReadyToHatch(item),
                'disabled-slot': item.state === 'auction'
              }"
            >
              <img
                :src="`${STATIC_BASE}/static/goods/${item.product.image}`"
                :alt="item.product.name"
                @error="onImageError"
              />
              <div
                v-if="item.type === 'creature' && item.incubation && !isReadyToHatch(item)"
                class="egg-timer-overlay"
              >
                {{ formatRemaining(item.incubation.hatch_at) }}
              </div>
            </div>

            <!-- ▸ НАДПИСИ ПОД КАРТОЧКОЙ -->
            <div class="item-caption">
  <div class="item-name">{{ item.product.name }}</div>
  <div class="item-rarity" :class="getRarityClass(item.product.rarity)">
    {{ item.product.rarity }}
  </div>
  <div class="item-status" v-if="item.state === 'auction'">
    <span class="locked">🔒 На аукционе</span>
  </div>
</div>

          </div>
        </div>

        <p v-else>Инвентарь пуст.</p>
      </div>
    </div>

    <!-- 🪆 МОДАЛКИ -->
    <GiftModal
      v-if="giftModalOpen"
      :visible="giftModalOpen"
      :item-id="selectedItem?.id"
      :item-name="selectedItem?.product.name"
      @close="giftModalOpen = false"
    />

    <HatchModal
      :visible="showHatchModal"
      :incubation-id="selectedItem?.incubation?.id"
      @close="showHatchModal = false"
      @hatched="handleHatched"
    />
  </div>

  <ReadForModal
  :visible="showBookModal"
  :pets="availablePetsToRead"
  title="Выбор питомца"
  @close="showBookModal = false"
  @select="readBook"
/>

</template>


<style lang="scss">
/* Убираем лишние стили для body */

.item-status .locked {
  font-size: 0.85em;
  color: #999;
  font-style: italic;
  margin-top: 2px;
  display: block;
}


.disabled-slot {
  pointer-events: none;
  opacity: 0.4;
  filter: grayscale(0.6);
}


.page-inner {
  position: relative; // ← обязательно
}

/* Блок со всем контентом инвентаря. Ставим масштаб 80%. */
.inv-wrapper {
  background: #181818e7;
  border: 1px solid rgb(196, 196, 196);
  max-width: 1300px;
  padding: 10px 30px 10px;
  border-radius: 22px;
  text-align: center;
  font-family: 'JetBrains Mono', monospace;
  display:flexbox;

}

h1 {
  font-size: 24px;
  background: rgba(0, 0, 0, 0.4);
  border-radius: 12px;
  font-family: 'JetBrains Mono', monospace;
}

.inventory-count {
  font-family: 'JetBrains Mono', monospace;
    margin-bottom: 40px;
    font-style: italic;
  }


/* Сетка, аналогичная магазину */
.inventory-grid {
  display: grid;
  font-family: 'JetBrains Mono', monospace;
  grid-template-columns: repeat(auto-fill, minmax(150px, 1fr));
  gap: 0rem;
  max-width: 800px;
  text-align: center;
}

/* Карточка предмета */
.inventory-slot {
  width: 100px; // меньше, стало воздушнее
  height: 100px; // уменьшаем под чисто иконку
  padding: 16px;
  border-radius: 16px;
  background: transparent;
  border: 1px solid #969696;
  display: inline-flex;
  align-items: center;
  position: relative;
  justify-content: center;
  
}
  .inventory-slot img {
  max-width: 100%;
  max-height: 100%;
  cursor: pointer;
  transition: transform 0.3s ease;
}


.item-caption {
  margin-top: 10px;
  text-align: center;
  margin-bottom: 10px;

  .item-name {
    font-size: 13px;
    font-weight: bold;
    color: #dfdfdf;
  }

  .item-rarity {
    font-size: 12px;
    font-style: italic;
  }
}



.inventory-layout {
  display: flex;
  align-items: flex-start;
  gap: 30px; // ← расстояние между панелью и инвентарём
  width: 100%;
  justify-content: center; // центрируем весь блок по ширине экрана
  
}



/* Блок с кнопками */
/* СТАЦИОНАРНАЯ, НО "ПРИЛИПАЮЩАЯ" ПАНЕЛЬ */
.inventory-actions-panel {
  position:fixed;
  left:350px;
  top: 150px;
  background: #181818e7;
  border: 1px solid rgb(196, 196, 196);
  padding: 16px 20px;
  border-radius: 18px;
  width: 180px;
  font-family: 'JetBrains Mono', monospace;
  color: #fff;
  flex-shrink: 0;
  z-index: 1000;

  .selected-label {
    font-size: 13px;
    font-style: italic;
    margin-bottom: 16px;
    color: #aaaaaa;
  }

  .inventory-actions {
    display: flex;
    flex-direction: column;
    gap: 12px;

    button {
      width: 100%;
    }
  }
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

.tooltip {
  max-width: 240px;
  max-height: 150px;
  overflow: auto;
  white-space: normal;
  word-break: break-word;
  padding: 5px 10px;
  border-radius: 8px;
  background: rgba(20, 20, 20, 0.95);
  color: #e7e7e7;
  font-size: 18px;
  font-family: 'JetBrains Mono', monospace;
  box-shadow: 0 0 6px rgba(0,0,0,0.5);
  z-index: 9999;
}

/* Смещение вниз + вправо */
.tooltip[data-popper-placement^='top'] {
  margin-bottom: 5px;
}
.tooltip[data-popper-placement^='bottom'] {
  margin-top: 5px;
}
.tooltip[data-popper-placement^='left'] {
  margin-right: 5px;
}
.tooltip[data-popper-placement^='right'] {
  margin-left: 5px;
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
.rarity-glitched { color: rgba(165, 132, 255, 0.801); }
.rarity-void { color: rgb(71, 29, 221); }

/* Выделение выбранного */
.selected-item {
  outline: 2px solid white;
  transform: scale(1.03);
}
</style>





