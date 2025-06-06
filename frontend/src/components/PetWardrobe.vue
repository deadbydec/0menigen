<template>
  <div v-if="selectedPet" class="pw">
    <h1 class="pw__title">ГАРДЕРОБ</h1>

    <div class="pw__layout">
      <!-- ─────────── ЛЕВАЯ ПАНЕЛЬ ─────────── -->
      <section class="panel panel--left">
        <div class="panel__slot-bar">
          <button @click="prevSlot" class="nav-btn">
            <i class="fa fa-chevron-left" />
          </button>
          <span class="slot-label">{{ activeSlotLabel }}</span>
          <button @click="nextSlot" class="nav-btn">
            <i class="fa fa-chevron-right" />
          </button>
        </div>

        <div class="panel__grid" :key="renderKey">
  <div
    v-for="item in slotItems"
    :key="`${item.wardrobe_id}_${item.instance ?? 0}`"
    :class="[
      'grid-item',
      {
        'grid-item--used': isEquippedGlobally(item.wardrobe_id, item.instance ?? 0),
        'grid-item--active': isEquippedHere(item.wardrobe_id, item.instance ?? 0)
      }
    ]"
    @click="isWithdrawMode ? withdrawItem(item) : toggleEquip(item)"
  >
    <img
      :src="resolveItemImage(item)"
      :alt="item.name"
      :class="[
        'grid-item__img',
        { 'grid-item__img--active': isEquippedHere(item.wardrobe_id, item.instance ?? 0) }
      ]"
    />
  </div>
</div>


        <div class="panel__footer">
          <button
  class="action-btn"
  :class="{ 'action-btn--active': isWithdrawMode }"
  @click="toggleWithdrawMode"
>

  ВЫВЕСТИ В ИНВЕНТАРЬ
</button>
<button
  class="action-btn"
  :class="{ 'action-btn--active': showAllWardrobeItems }"
  @click="toggleShowAll"
>
  ПОКАЗАТЬ ВСЕ
</button>

        </div>
      </section>

      <!-- ─────────── ЦЕНТР ─────────── -->
      <section class="panel panel--center">
        <h2 class="viewer__name">{{ selectedPet.name }}</h2>

        <div class="viewer">
          <template v-for="layer in renderedLayers" :key="`${layer.slot}_${layer.rid ?? layer.pid}_${layer.instance ?? 0}`">
            <img
              :src="layer.src"
              :class="['viewer__layer', 'layer-' + layer.slot]"
            />
          </template>
        </div>

        <div class="carousel">
          <button @click="prevPet" class="nav-btn">
            <i class="fa fa-chevron-left" />
          </button>
          <div class="carousel__strip">
            <div
              v-for="p in petsStore.myPets"
              :key="p.id"
              :class="['carousel__thumb', { 'carousel__thumb--active': selectedPet.id === p.id }]"
              @click="selectPet(p)"
            >
              <img :src="getPetImage(p)" alt="pet avatar" />
            </div>
          </div>
          <button @click="nextPet" class="nav-btn">
            <i class="fa fa-chevron-right" />
          </button>
        </div>
      </section>

      <!-- ─────────── ПРАВАЯ ПАНЕЛЬ ─────────── -->
      <section class="panel panel--right">
        <h2 class="equipped-title">Слои</h2>

        <div class="equipped-list">
          <div
            v-for="lay in renderedLayers"
            :key="`${lay.slot}_${lay.rid ?? lay.pid}_${lay.instance ?? 0}`"
            class="equipped-item"
            @mouseenter="hoveredSlot = `${lay.slot}_${lay.rid ?? lay.pid}_${lay.instance ?? 0}`"
            @mouseleave="hoveredSlot = null"
          >
            <div class="equipped-row">
              <button
                v-if="hoveredSlot === `${lay.slot}_${lay.rid ?? lay.pid}_${lay.instance ?? 0}` && lay.pid !== -1"
                class="slot-remove-btn"
                @click="removeLayer(lay)"
                title="Снять предмет"
              >
                ❌
              </button>
              <span class="equipped-item__name">
  {{ getItemName(lay.pid) || '—' }}
</span>

              <div
                v-if="hoveredSlot === `${lay.slot}_${lay.rid ?? lay.pid}_${lay.instance ?? 0}`"
                class="equipped-item__arrows"
              >
                <button @click="moveItemUp(lay.rid, lay.instance)" class="nav-btn arrow-btn">
                  <i class="fa fa-chevron-up" />
                </button>
                <button @click="moveItemDown(lay.rid, lay.instance)" class="nav-btn arrow-btn">
                  <i class="fa fa-chevron-down" />
                </button>
              </div>
            </div>
            <div class="equipped-divider" />
          </div>
        </div>

        <div class="equipped-actions">
          <button class="action-btn" @click="saveChanges">СОХРАНИТЬ</button>
          <button class="action-btn" @click="clearAll">СНЯТЬ ВСЕ</button>
        </div>
      </section>
    </div>
  </div>

  <div v-else class="pw__loading">Загрузка питомца…</div>
</template>





<script setup>
import { ref, reactive, computed, onMounted, watchEffect, defineExpose } from 'vue'
import api from '@/utils/axios'
import { useRoute } from 'vue-router'

import { usePetsStore } from '@/store/pets'
import { useWardrobeStore } from '@/store/wardrobe'
import { useToastStore } from '@/store/toast'
import { usePetRenderStore } from '@/store/petRender'

const STATIC = import.meta.env.VITE_STATIC_URL || 'https://localhost:5002'
const petsStore = usePetsStore()
const wardrobeStore = useWardrobeStore()
const toast = useToastStore()
const renderStore = usePetRenderStore()
const route = useRoute()
const isWithdrawMode = ref(false)
const showAllWardrobeItems = ref(false)
const renderKey = ref(0)


function toggleShowAll() {
  showAllWardrobeItems.value = !showAllWardrobeItems.value
}


const slots = ['background','foreground','aura','companion','body','paws','wings','eyes','head','tail','accessory','face','skin','dye']
const slotLabels = {
  background:'Фон', aura:'Окружение', companion:'Спутник',
  body:'Тело', paws:'Лапы', wings:'Крылья', eyes:'Глаза',
  head:'Голова', tail:'Хвост', accessory:'Аксессуар',
  face:'Морда', skin:'Покров', foreground:'Передний план', dye:'Эссенция'
}
const SLOT_RU2EN = Object.fromEntries(Object.entries(slotLabels).map(([en, ru]) => [ru.toLowerCase(), en]))

const EN_TO_RU = {
  background: 'фон', aura: 'окружение', companion: 'спутник',
  body: 'тело', paws: 'лапы', wings: 'крылья',
  eyes: 'глаза', head: 'голова', tail: 'хвост',
  accessory: 'аксессуар', face: 'морда', skin: 'покров', foreground:'передний план', dye:'эссенция'
}


const selectedPet = ref(null)
const initialAppearance = reactive({})
const previewAppearance = reactive({})
const selectedCard = ref(null)
const hoveredSlot = ref(null)
const activeSlotIndex = ref(0)
const slotOrder = ref([])

const activeSlot = computed(() => slots[activeSlotIndex.value])
const activeSlotLabel = computed(() => slotLabels[activeSlot.value])

const DIR_STATIC  = import.meta.env.VITE_STATIC_URL + '/static'
const DIR_COSMO   = DIR_STATIC + '/cosmetic'
const DIR_GOODS   = DIR_STATIC + '/goods'

async function withdrawItem(item) {
  isWithdrawMode.value = false
  try {
    await wardrobeStore.removeFromWardrobe(item.wardrobe_id)
    removeLayer(item) // снимаем визуально и из store
    toast.addToast('Предмет выведен в инвентарь', { type: 'success' })
  } catch {
    toast.addToast('Ошибка при выводе предмета', { type: 'error' })
  }
}

function resolveItemImage(it) {
  const slot = it.slot?.toLowerCase()
  const custom = typeof it.custom === 'string'
    ? (() => { try { return JSON.parse(it.custom) } catch { return {} } })()
    : it.custom || {}

  const raw =
    custom?.[`${slot}_image`] ||
    (['aura', 'companion', 'foreground', 'background', 'эссенция'].includes(slot) ? custom?.image : null) ||
    it.image

  if (!raw) return ''

  return raw.startsWith('http') || raw.startsWith('/')
    ? raw
    : (raw.includes('/') ? `${DIR_STATIC}/${raw}` : `${DIR_GOODS}/${raw}`)
}

const appearanceLayers = computed({
  get() {
    return selectedPet.value ? renderStore.appearances[selectedPet.value.id] ?? [] : []
  },
  set(v) {
    if (selectedPet.value) renderStore.appearances[selectedPet.value.id] = v
  }
})

function toggleWithdrawMode() {
  isWithdrawMode.value = !isWithdrawMode.value
  if (isWithdrawMode.value) {
    toast.addToast('Выберите предмет для вывода в инвентарь', { type: 'info' })
  }
}


/* ► слои с нормализованными src для рендера */
const renderedLayers = computed(()=>{
  if(!selectedPet.value) return []
  return renderStore.getLayersFromPreview(selectedPet.value, previewAppearance, slotOrder.value)
})

/* ► предметы активного слота */
const slotItems = computed(() => {
  let items = showAllWardrobeItems.value
    ? wardrobeStore.items
    : wardrobeStore.items.filter(it => it.slot === EN_TO_RU[activeSlot.value])

  return [...items].sort((a, b) => b.wardrobe_id - a.wardrobe_id)
})




const getPetImage = p =>
  p?.image?.startsWith('http') ? p.image : `${STATIC}/static/${p?.image||''}`
defineExpose({ getPetImage })

const getItemName = pid=>{
  if(pid === -1) return 'База'
  const it = wardrobeStore.items.find(i=>i.product_id === pid)
  return it?.name || '—'
}

/* ────────── equipment checks ────────── */
function matched(a,b){                           // helper: rid приоритетен, иначе pid
  if(a.rid != null && b.rid != null) return a.rid === b.rid && (a.instance??0)===(b.instance??0)
  return a.pid === b.pid && (a.instance??0)===(b.instance??0)
}
const isEquippedGlobally = (rid, inst = 0) => Object.values(renderStore.appearances).some(layers => layers?.some(l => (l.rid ?? -999) === rid && (l.instance ?? 0) === inst))
const isEquippedHere = (rid, inst = 0) => appearanceLayers.value?.some(l => (l.rid ?? -999) === rid && (l.instance ?? 0) === inst)

/* ────────── UI nav ────────── */
const prevSlot =()=>{ activeSlotIndex.value=(activeSlotIndex.value-1+slots.length)%slots.length; selectedCard.value=null }
const nextSlot =()=>{ activeSlotIndex.value=(activeSlotIndex.value+1)%slots.length; selectedCard.value=null }

function prevPet(){
  const arr=petsStore.myPets, i=arr.findIndex(p=>p.id===selectedPet.value.id)
  selectPet(arr[(i-1+arr.length)%arr.length])
}
function nextPet(){
  const arr=petsStore.myPets, i=arr.findIndex(p=>p.id===selectedPet.value.id)
  selectPet(arr[(i+1)%arr.length])
}

/* ────────── equip / unequip ────────── */
function toggleEquip(it){
  const rid = it.wardrobe_id, pid = it.product_id
  const inst = it.instance ?? 0
  const slot = SLOT_RU2EN[it.slot?.toLowerCase()] || it.slot


  const idx = appearanceLayers.value.findIndex(l=>matched(l,{rid,pid,instance:inst}))
  if(idx!==-1){                                  // снять
    appearanceLayers.value.splice(idx,1)
    slotOrder.value = slotOrder.value.filter(l=>!matched(l,{rid,pid,instance:inst}))
    previewAppearance[slot] = (previewAppearance[slot]||[]).filter(l=>!matched(l,{rid,pid,instance:inst}))
    selectedCard.value=null
    return
  }
  // надеть
  const layer = { rid, pid, slot, instance:inst }
  appearanceLayers.value.push(layer)
  slotOrder.value.push(layer)
  ;(previewAppearance[slot] ||= []).push(layer)
  selectedCard.value = it
}

function removeLayer(lay) {
  const slot = lay.slot
  previewAppearance[slot] = (previewAppearance[slot] || []).filter(l => !matched(l, lay))
  slotOrder.value = slotOrder.value.filter(l => !matched(l, lay))
  appearanceLayers.value = appearanceLayers.value.filter(l => !matched(l, lay))
  renderStore.setCustomSlotOrder(selectedPet.value.id, slotOrder.value)
}


function moveItemUp(rid, instance = 0) {
  const i = slotOrder.value.findIndex(
    p => (p.rid ?? -999) === rid && (p.instance ?? 0) === instance
  )
  if (i > 0) {
    const newOrder = [...slotOrder.value]
    ;[newOrder[i - 1], newOrder[i]] = [newOrder[i], newOrder[i - 1]]
    slotOrder.value = newOrder
    renderStore.setCustomSlotOrder(selectedPet.value.id, newOrder)
  }
}


function moveItemDown(rid, instance = 0) {
  const i = slotOrder.value.findIndex(
    p => (p.rid ?? -999) === rid && (p.instance ?? 0) === instance
  )
  if (i !== -1 && i < slotOrder.value.length - 1) {
    const newOrder = [...slotOrder.value]
    ;[newOrder[i], newOrder[i + 1]] = [newOrder[i + 1], newOrder[i]]
    slotOrder.value = newOrder
  }
}

/* ────────── bulk ops ────────── */
function clearAll(){
  Object.keys(previewAppearance).forEach(k=>{ if(k!=='base') previewAppearance[k]=[] })
  slotOrder.value          = [{ rid:-1,pid:-1,instance:0, slot: 'base' }]
  appearanceLayers.value   = appearanceLayers.value.filter(l=>l.pid===-1)
  selectedCard.value=null
}

/* ────────── API helpers ────────── */
async function loadAppearance() {
  if (!selectedPet.value) return
  try {
    const { data } = await api.get(`/pets/${selectedPet.value.id}/appearance`)

    // 🔄 Очищаем
    Object.keys(previewAppearance).forEach(k => delete previewAppearance[k])
    appearanceLayers.value = []

    const layers = []

    for (const [slot, arr] of Object.entries(data.appearance || {})) {
      const lays = Array.isArray(arr) ? arr : [arr]

      for (const l of lays) {
        const layer = {
          pid: typeof l.pid === 'object' ? l.pid?.pid ?? -1 : l.pid ?? -1,
          rid: l.rid ?? null,
          instance: l.instance ?? 0,
          slot: slot === 'pet' ? 'base' : slot
        }
        layers.push(layer)
        ;(previewAppearance[layer.slot] ||= []).push(layer)
      }
    }

    // 🐾 добавляем base, если не было
    const hasBase = layers.some(l => l.slot === 'base' && l.pid === -1)
    if (!hasBase) {
      const petLayer = { pid: -1, rid: -1, slot: 'base', instance: 0 }
      layers.unshift(petLayer)
      previewAppearance.base = [petLayer]
    }

    appearanceLayers.value = layers
    slotOrder.value = data.slot_order || []

  } catch (e) {
    console.warn('loadAppearance error', e)
    toast.addToast('Не удалось загрузить внешний вид', { type: 'error' })
  }
}


async function moveBackToInventory() {
  if (!selectedCard.value) return
  try {
    await wardrobeStore.removeFromWardrobe(selectedCard.value.wardrobe_id)
    toggleEquip(selectedCard.value)
    toast.addToast('Снято и возвращено в инвентарь', { type: 'success' })
  } catch {
    toast.addToast('Не удалось снять предмет', { type: 'error' })
  }
}

function extractPid(layer) {
  return layer?.pid ?? layer?.product_id ?? null
}

// ⬇️ нормализуем slot_order (уникальность по ключу `${pid}:${rid}:${slot}:${instance}`)
const seen = new Set()
const order = []

for (const o of slotOrder.value) {
  const pid = typeof o.pid === 'object' ? o.pid?.pid ?? -1 : o.pid ?? -1
  const rid = o.rid ?? null
  const slot = o.slot === 'pet' ? 'base' : o.slot
  const instance = o.instance ?? 0

  const key = `${pid}:${rid}:${slot}:${instance}`
  if (!seen.has(key)) {
    seen.add(key)
    order.push({ pid, rid, instance, slot })
  }
}


async function saveChanges() {
  if (!selectedPet.value) return

  const appearance = {}

  for (const [slot, lays] of Object.entries(previewAppearance)) {
    const realSlot = slot === 'pet' ? 'base' : slot
    appearance[realSlot] = lays.map((l, index) => ({
      pid: typeof l.pid === 'object' ? l.pid?.pid ?? -1 : l.pid ?? -1,
      rid: l.rid ?? null,
      instance: l.instance ?? index,
    }))
  }

  // 🐾 slot_order по факту = slotOrder.value
  const order = slotOrder.value.map(l => ({
    pid: typeof l.pid === 'object' ? l.pid?.pid ?? -1 : l.pid ?? -1,
    rid: l.rid ?? null,
    instance: l.instance ?? 0,
    slot: l.slot === 'pet' ? 'base' : l.slot,
  }))

  // 🐾 гарантируем наличие базы
  const hasBase = order.some(o => o.slot === 'base' && o.pid === -1)
  if (selectedPet.value?.image && !hasBase) {
    appearance.base = appearance.base ?? []
    appearance.base.unshift({ pid: -1, rid: -1, instance: 0 })
    order.unshift({ pid: -1, rid: -1, instance: 0, slot: 'base' })
  }

  console.log("🐛 appearance →", appearance)
  console.log("🐛 slot_order →", order)

  try {
    await api.post(
      `/pets/${selectedPet.value.id}/appearance/bulk`,
      { appearance, slot_order: order },
      { withCredentials: true }
    )
    toast.addToast('Сохранено', { type: 'success' })
  } catch (e) {
    console.error('💥 saveChanges error:', e.response?.data || e)
    toast.addToast('Ошибка при сохранении', { type: 'error' })
  }
}





/* ────────── pet select / init ────────── */
function selectPet(p){ if(p){ selectedPet.value=p; loadAppearance() } }

onMounted(async ()=>{
  await Promise.all([petsStore.fetchAllPets(), wardrobeStore.fetchWardrobe()])
  const start = petsStore.myPets.find(p=>p.id===Number(route.query.pet)) || petsStore.myPets[0]
  selectPet(start)
})

watchEffect(()=>{
  if(selectedPet.value && !petsStore.myPets.find(p=>p.id===selectedPet.value.id)){
    selectPet(petsStore.myPets[0]||null)
  }
})
</script>


<style lang="scss" scoped>
// ───────── Base fonts & vars ───────── //
$glass-bg:rgba(38, 32, 39, 0.13);
$glass-border: 1px solid #000;
$glass-hover: rgba(255, 255, 255, 0.08);
$accent: #d6dcdda6;

.action-btn--active {
  border: 3px solid #00000081;
  background-color: rgba(255, 0, 85, 0.1);
  box-shadow: 0 0 5px #0000009d;
  transition: all 0.2s ease;
}

.panel__grid {
  
  display: grid;
  grid-template-columns: repeat(auto-fit, minmax(70px, 1fr));
grid-auto-rows: 90px;
  grid-template-columns: repeat(auto-fill, 70px);
  grid-auto-rows: 90px;
  gap: 5px;
  padding: .5rem;
  justify-content: center; // 💡 чтобы центрировать при малом количестве
  align-content: start;
}



.grid-item {
  display: flex;
  justify-content: center;
  align-items: center;
  width: 100%;
  height: 100%;
}



.grid-item--used {
  opacity: 0.3;
}

.grid-item--active {
  z-index: 2;
}

.grid-item__img--active {
  filter: drop-shadow(0 0 4px #00ffee);
}

// ───────── Equipped list (Right Panel) ───────── //
.equipped-title {
  text-align: center;
  padding: .25rem 0;
  border-bottom: 1px solid $glass-border;
  font-size: .85rem;
}

.equipped-list {
  flex: 1;
  overflow-y: auto;
  padding: 0.5rem;
  display: flex;
  flex-direction: column;
  gap: 2px;
}

.equipped-item {
  display: flex;
  flex-direction: column;
  border-radius: 6px;
  transition: background 0.2s;



  &:hover .slot-remove-btn,
  &:hover .equipped-item__arrows {
    opacity: 1;
  }
}

.equipped-row {
  display: flex;
  align-items: center;
  gap: 4px;
  padding: 2px 6px;
  min-height: 24px;
}

.slot-remove-btn {
  width: 20px;
  height: 20px;
  display: flex;
  align-items: center;
  justify-content: center;
  font-size: 0.8rem;
  background: transparent;
  border: none;
  color: #ffffff;
  cursor: pointer;
  opacity: 0;
  transition: opacity 0.15s;
  flex-shrink: 0;
}

.equipped-item__name {
  flex: 1;
  font-size: 0.75rem;
  color: white;
  white-space: nowrap;
  overflow: hidden;
  text-overflow: ellipsis;
}

.equipped-item__arrows {
  display: flex;
  gap: 2px;
  opacity: 0;
  transition: opacity 0.15s;
  flex-shrink: 0;

  button {
    width: 20px;
    height: 20px;
    font-size: 0.75rem;
  }
}

.equipped-divider {
  width: 100%;
  height: 1px;
  background: rgba(255, 255, 255, 0.08);
  margin: 5px 0;
}

.equipped-actions {
  display: flex;
  gap: .5rem;
  padding: .5rem;
  border-top: 1px solid $glass-border;
}

// ───────── Layout ───────── //
.pw {
  font-family: 'JetBrains Mono', monospace;
  max-width: 1200px;
  max-height: 750px;
  display: flex;
  flex-direction: column;
  height: 100%;
  width: 100%;
  padding: 1rem;
  gap: 1rem;

  &__title {
    text-align: center;
    font-size: 1.5rem;
    font-weight: 700;
    margin-bottom: .5rem;
  }

  &__layout {
    flex: 1;
    display: flex;
    gap: 1rem;
    overflow: hidden;
    box-shadow: 0 0 15px rgba(0, 0, 0, 0.40);
  }

  &__loading {
    display: flex;
    align-items: center;
    justify-content: center;
    height: 100%;
  }
}

// ───────── Glass panels ───────── //
.panel {
  background: $glass-bg;
  border: 1px solid $glass-border;
  backdrop-filter: blur(8px);
  border-radius: 12px;
  box-shadow: 0 0 20px rgba(0, 0, 0, 0.4);
  overflow: hidden;
  display: flex;
  flex-direction: column;

  &--left {
    width: 25%;
    min-width: 220px;
  }

  &--center {
    flex: 1;
    padding: 1rem;
  }

  &--right {
    width: 25%;
    min-width: 220px;
  }

  &__slot-bar {
    display: flex;
    align-items: center;
    justify-content: space-between;
    padding: .25rem .5rem;
    border-bottom: 1px solid $glass-border;

    .slot-label {
      font-size: .75rem;
      text-transform: uppercase;
      letter-spacing: .05rem;
    }
  }

  &__grid {
    flex: 1;
    padding: .75rem;
    display: grid;
    grid-template-columns: repeat(auto-fit, minmax(70px, 1fr));

    gap: .75rem;
    overflow-y: auto;
    max-height: 520px;
  }

  &__footer {
    padding: .5rem;
    border-top: 1px solid $glass-border;
  }
}

// ───────── Buttons ───────── //
.nav-btn {
  width: 32px;
  height: 32px;
  font-size: 1rem;
  background: transparent;
  color: white;
  border: none;
  border-radius: 50%;
  cursor: pointer;
  display: flex;
  align-items: center;
  justify-content: center;
  transition: background 0.2s;

  &:hover {
    background: $glass-hover;
  }
}

.arrow-btn {
  width: 24px;
  height: 24px;
  font-size: 0.85rem;
  background: transparent;
  border: none;
  color: white;
  padding: 0;
  cursor: pointer;

  &:hover {
    background: rgba(255, 255, 255, 0.1);
    border-radius: 50%;
  }
}

.action-btn {
  background: rgba(255, 255, 255, 0.12);
  border: 1px solid rgba(255, 255, 255, 0.2);
  border-radius: 6px;
  padding: .35rem .5rem;
  font-size: .7rem;
  text-transform: uppercase;
  letter-spacing: .05rem;
  cursor: pointer;
  flex: 1;
  transition: background .2s;

  &:hover {
    background: rgba(255, 255, 255, 0.18);
  }
}

// ───────── Inventory Grid Items ───────── //
.grid-item__img {
  width: 100%;
  height: 100%;
  object-fit: contain;
  border-radius: 6px;
  cursor: pointer;
  transition: box-shadow 0.2s, outline 0.2s;

  &:hover,
  &--active {
    box-shadow: 0 0 0 2px $accent inset;
  }
}

// ───────── Viewer ───────── //
.viewer {
  position: relative;
  max-height: 800px;
  width: 100%;
  flex: 1;
  display: flex;
  align-items: center;
  justify-content: center;
  box-shadow: 0 0 15px rgba(0, 0, 0, 0.40);
  z-index: 5;

  &__layer {
    position: absolute;
    inset: 0;
    margin: auto;
    max-height: 100%;
    object-fit: contain;
  }
}

.viewer__name {
  text-align: center;
  font-size: 1.3rem;
  font-weight: 600;
  color: white;
  margin-bottom: 0.5rem;
  text-shadow: 0 0 3px rgba(0,0,0,0.6);
}

// ───────── Z-index for Slots ───────── //
.viewer__layer.layer-background { z-index: 1 }
.viewer__layer.layer-aura       { z-index: 3 }
.viewer__layer.layer-base       { z-index: 3 }
.viewer__layer.layer-body       { z-index: 3 }
.viewer__layer.layer-companion  { z-index: 3 }
.viewer__layer.layer-foreground  { z-index: 4 }
.viewer__layer.layer-paws       { z-index: 3 }
.viewer__layer.layer-wings      { z-index: 3 }
.viewer__layer.layer-eyes       { z-index: 3 }
.viewer__layer.layer-head       { z-index: 3 }
.viewer__layer.layer-tail       { z-index: 3 }
.viewer__layer.layer-accessory  { z-index: 3 }
.viewer__layer.layer-face       { z-index: 3 }
.viewer__layer.layer-skin       { z-index: 3 }


// ───────── Carousel ───────── //
.carousel {
  display: flex;
  align-items: center;
  gap: .5rem;
  margin-top: 1rem;
  justify-content: center;

  &__strip {
    display: flex;
    gap: .5rem;
    overflow-x: auto;
    max-width: 240px;
    padding: 0 .25rem;
    scrollbar-width: none;
    -ms-overflow-style: none;

    &::-webkit-scrollbar {
      display: none;
    }
  }

  &__thumb {
    width: 80px;
    height: 80px;
    border-radius: 50%;
    overflow: hidden;
    background-color: rgba(255, 255, 255, 0.05);
    border: 2px solid transparent;
    flex-shrink: 0;
    cursor: pointer;
    transition: border-color .2s;
    display: flex;
    align-items: center;
    justify-content: center;

    &--active {
      border-color: $accent;
    }

    img {
      width: 100%;
      height: 100%;
      object-fit: cover;
      object-position: center top;
      display: block;
    }
  }
}
</style>




