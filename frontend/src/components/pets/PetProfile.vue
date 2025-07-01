<template>
  <div class="pet-grid">
    <!-- ╭─ Avatar + wardrobe ───────────────────────────────╮ -->
    <section class="glass-card avatar-card" v-if="!isLoading && pet">
      <h3 class="card-title"><strong>{{ pet.name }}</strong></h3>

      <!-- холст со слоями -->
      <div class="pet-canvas">
        <img
          v-for="layer in layers"
          :key="layer.slot"
          :src="layer.src"
          :class="['pet-layer', `layer--${layer.slot}`]"
          :style="{ zIndex: layer.z }"
          :alt="`layer ${layer.slot}`"
        />
      </div>

      <button class="wardrobe-btn" @click="openWardrobe">
        Гардероб
      </button>
    </section>
 <section class="glass-card below-avatar" v-if="!isLoading && pet?.companion !== undefined">
  <h3 class="card-title">Компаньон</h3>

  <div v-if="pet?.companion" class="companion-layout">
    <img :src="companionIcon" alt="icon" class="companion-image" />

    <div class="companion-info">
      <!-- 🎭 ИМЯ -->
      <h4 class="companion-name" v-if="!editingCompanion">{{ pet.companion.name }}</h4>
      <input
        v-else
        v-model="companionName"
        class="companion-name-input"
        maxlength="100"
        placeholder="Имя спутника"
      />

      <!-- 📝 ОПИСАНИЕ -->
      <p class="companion-description" v-if="!editingCompanion">{{ pet.companion.description }}</p>
      <textarea
        v-else
        v-model="companionDesc"
        class="companion-description-input"
        rows="3"
        maxlength="2000"
        placeholder="Описание спутника"
      />

      <!-- 🔘 КНОПКИ -->
      <div class="companion-actions">
        <button v-if="!editingCompanion" @click="startEditCompanion">✏️ Редактировать</button>
        <button v-if="editingCompanion" @click="saveCompanionInfo">💾 Сохранить</button>
        <button v-if="editingCompanion" @click="editingCompanion = false">❌ Отмена</button>

        <button v-if="pet.companion?.product_id && !editingCompanion" @click="removeCompanion">🚫 Убрать</button>
      </div>
    </div>
  </div>

  <div v-else>
    <p>Нет спутника</p>
    <button @click="showPicker = true">🐾 Приручить</button>
  </div>
</section>


<CompanionModal
  :visible="showPicker"
  :pet-id="pet?.id"
  @close="showPicker = false"
  @updated="refreshPet"
/>


    <!-- ╭─ Stats ───────────────────────────────────────────╮ -->
    <section class="glass-card stats-card" v-if="!isLoading && pet">
      <h3 class="card-title">Инфо</h3>
      <ul class="stats-list">
        <li><strong>Раса:</strong> {{ pet.species?.race_name || 'неизвестен' }}</li>
<li><strong>Вид:</strong> {{ pet.species?.name || 'неизвестен' }}</li>




        <li><strong>🧬 Черта:</strong> {{ pet.trait }}</li>
        <li><strong>📈 Уровень:</strong> {{ pet.level }}</li>
        <li><strong>🧠 Интеллект:</strong> {{ pet.intelligence }}</li>
        <li><strong>🍖 Сытость:</strong> {{ pet.fullness }}</li>
        <li><strong>⚡ Энергия:</strong> {{ pet.energy }}</li>
        <li><strong>❤️ Здоровье:</strong> {{ pet.health }}</li>
        <li><strong>🤝 Привязанность:</strong> {{ pet.bond }}</li>
        <li><strong>🧪 Аномалия:</strong> {{ pet.anomaly_level }}</li>
        <li><strong>🗓️ Дата рождения:</strong> {{ formatDate(pet.birthdate) }}</li>
      </ul>
    </section>

    <!-- ╭─ Bio ─────────────────────────────────────────────╮ -->
    <section class="glass-card bio-card" v-if="!isLoading && pet">
  <h3 class="card-title">Биография</h3>

  <div v-if="editingBio">
    <textarea v-model="newBio" class="bio-textarea" rows="5" />
    <button @click="saveBio">💾 Сохранить</button>
    <button @click="editingBio = false">❌ Отмена</button>
  </div>

  <div v-else @click="() => { newBio = pet.bio || ''; editingBio = true }">
    <p v-if="pet.bio?.trim().length">{{ pet.bio }}</p>
    <p v-else class="bio-placeholder">Расскажите о&nbsp;питомце… 📝</p>
  </div>
</section>

    <section class="glass-card below-bio" v-if="!isLoading && pet?.favorite_items?.length">
  <h3 class="card-title">Реликвии</h3>
  <div class="favorite-items">
    <img
      v-for="pid in pet.favorite_items"
      :key="pid"
      :src="(wardrobeStore.byPid(pid) || inventoryStore.byPid(pid))?.image || ''"
      class="favorite-icon"
      :alt="'item ' + pid"
    />
  </div>
</section>


    <!-- loader / fallback -->
    <div v-if="isLoading" class="loader">Загрузка питомца…</div>
    <p v-else-if="!pet && !isLoading" class="not-found">Питомец не найден 🤔</p>
  </div>
</template>


<script setup>
import { computed, ref, onMounted, watchEffect } from 'vue'
import { useRoute, useRouter } from 'vue-router'
import dayjs from 'dayjs'

import { usePetsStore } from '@/store/pets'
import { usePetRenderStore } from '@/store/petRender'
import { useWardrobeStore } from '@/store/wardrobe'
import { useInventoryStore } from '@/store/inventory'
import CompanionModal from './CompanionModal.vue'
const showPicker = ref(false)

const route         = useRoute()
const router        = useRouter()
const petsStore     = usePetsStore()
const renderStore   = usePetRenderStore()
const wardrobeStore = useWardrobeStore()
const inventoryStore = useInventoryStore()

const petId = Number(route.params.id)
const isLoading = ref(true)

const layers = ref([])
const pet = computed(() => petsStore.currentPet) // ✅ теперь всегда используем только currentPet

const newBio = ref('')
const editingBio = ref(false)
const editingCompanion = ref(false)
const companionName = ref('')
const companionDesc = ref('')
const speciesMeta = computed(() => petsStore.speciesMap || {})

function formatRace(code) {
  if (!code) return '—'
  return code.includes('+') ? code.split('+').join(' + ') : code
}

const getItemIcon = (filename) =>
  `${import.meta.env.VITE_STATIC_URL || 'https://localhost:5002'}/static/goods/${filename}`

onMounted(async () => {
  isLoading.value = true

  const rawId = route.params.id
  const petId = Number(rawId)

  if (!rawId || isNaN(petId)) {
    console.error("💥 некорректный ID из маршрута:", rawId)
    isLoading.value = false
    router.push("/mypets")
    return
  }

  await petsStore.fetchSpeciesMeta()

  if (!petsStore.myPets.length) {
    await petsStore.fetchAllPets()
  }

  await petsStore.fetchPetById(petId)

  await Promise.all([
    renderStore.fetchAppearance(petId, true),
    wardrobeStore.fetchWardrobe(),
    inventoryStore.fetchInventory(),
  ])

  const p = pet.value
  if (p?.id) {
    layers.value = renderStore.getLayersForPet(p.id)
    newBio.value = p.biography || ''

    if (p.companion && typeof p.companion === 'object') {
      companionName.value = p.companion.name || ''
      companionDesc.value = p.companion.description || ''
    } else {
      companionName.value = ''
      companionDesc.value = ''
    }
  }

  isLoading.value = false
})

function startEditCompanion() {
  if (!pet.value?.companion) return

  companionName.value = pet.value.companion.name || ''
  companionDesc.value = pet.value.companion.description || ''
  editingCompanion.value = true
}

const cancelEditCompanion = () => {
  editingCompanion.value = false
}

const cancelEditBio = () => {
  editingBio.value = false
}

const speciesName = computed(() => {
  const code = pet.value?.species_code
  const meta = speciesMeta.value?.[code]
  return meta?.species_name || code || '—'
})



const companionIcon = computed(() => {
  const companion = pet.value?.companion
  if (!companion || !companion.image) return ''
  return getItemIcon(companion.image)
})


async function refreshPet() {
  if (!pet.value?.id) return
  await petsStore.fetchPetById(pet.value.id)
}

async function removeCompanion() {
  if (!pet.value) return
  await petsStore.removeCompanion(pet.value.id)
}


async function saveBio() {
  if (!pet.value) return
  await petsStore.updatePetBio(pet.value.id, newBio.value)
  await petsStore.fetchPetById(pet.value.id)
  editingBio.value = false
}

async function saveCompanionInfo() {
  if (!pet.value) return
  await petsStore.editCompanion(pet.value.id, companionName.value, companionDesc.value)
  await petsStore.fetchPetById(pet.value.id)
  editingCompanion.value = false
}

function formatDate(iso) {
  return iso ? dayjs(iso).format('DD.MM.YYYY HH:mm') : '—'
}

function openWardrobe() {
  if (pet.value?.id) {
    router.push({ path: '/wardrobe', query: { pet: pet.value.id } })
  }
}

function openCompanionPicker() {
  console.warn("openCompanionPicker ещё не реализован")
  // тут будет логика выбора спутника
}

watchEffect(() => {
  if (pet.value?.id) {
    layers.value = renderStore.getLayersForPet(pet.value.id)
  }
})
</script>

<style scoped>

.companion-layout {
  display: flex;
  gap: 20px;
  align-items: flex-start;
  margin-top: 16px;
}

.companion-image {
  width: 120px;
  height: 120px;
  object-fit: contain;
  border-radius: 8px;
  border: 1px solid rgba(255, 255, 255, 0.1);
}

.companion-info {
  flex: 1;
}

.companion-name {
  font-size: 1.4em;
  font-weight: bold;
  margin-bottom: 8px;
}

.companion-description {
  font-size: 1em;
  margin-bottom: 12px;
  white-space: pre-line;
}

.companion-name-input,
.companion-description-input {
  background: rgba(255, 255, 255, 0.08);
  border: 1px solid rgba(255, 255, 255, 0.2);
  padding: 6px 8px;
  color: white;
  width: 100%;
  border-radius: 6px;
  font-size: 1em;
  resize: vertical;
  margin-bottom: 10px;
}

.companion-name-input {
  font-weight: bold;
  font-size: 1.2em;
  margin-bottom: 6px;
}

.companion-actions {
  display: flex;
  gap: 10px;
  flex-wrap: wrap;
}


.companion-layout {
  display: flex;
  gap: 20px;
  align-items: flex-start;
  margin-top: 16px;
}

.companion-image {
  width: 120px;
  height: 120px;
  object-fit: contain;
  border-radius: 8px;
  border: 1px solid rgba(255, 255, 255, 0.1);
}

.companion-info {
  flex: 1;
}

.companion-name {
  font-size: 1.4em;
  font-weight: bold;
  margin-bottom: 8px;
}

.companion-description {
  font-size: 1em;
  margin-bottom: 12px;
}

.companion-actions {
  display: flex;
  gap: 10px;
}


.companion-icon,
.favorite-icon {
  width: 48px;
  height: 48px;
  object-fit: contain;
  margin: 4px;
}

button {
  background: transparent;
  color: #ccc;

  padding: 4px 10px;
  border-radius: 6px;
  font-size: 14px;
  cursor: pointer;
  transition: background 0.2s ease-in-out, color 0.2s;

  &:hover {
    background: rgba(255, 255, 255, 0.05);
    color: #fff;
    border-color: #666;
  }

  &:active {
    background: rgba(255, 255, 255, 0.1);
    transform: scale(0.98);
  }
}



/* ── Grid layout ───────────────────────────────────── */
.pet-grid {
  display: grid;
 grid-template-columns: 400px 1fr;

  grid-template-rows: auto auto auto; /* 1-я строка stats, 2-я bio, 3-я extra */
  column-gap: 2.0rem;
  row-gap: 2rem;                      /* горизонтальный и вертикальный «воздух» */
  max-width: 1300px;
  margin: 1rem auto;                  /* внешний отступ сверху/снизу */
  padding: 0 1.5rem 2rem;             /* внутренний отступ по бокам + снизу */
  box-sizing: border-box;
  margin-top: 120px;
}

/* ── Glasslite base ────────────────────────────────── */
.glass-card {
  background: #181818e7;
  width: 100%;
  /* height убрали, чтобы карточка росла только по содержимому */
  border: 1px solid rgb(196, 196, 196);
  border-radius: 12px;
  padding: 1rem 0.0rem;
  font-family: 'JetBrains Mono', monospace;
  display: flex;
  flex-direction: column;
}

.card-title {
  text-align: center;
  margin-bottom: 0.5rem;
  font-weight: 700;
  letter-spacing: .6px;
}

/* ── Avatar block ──────────────────────────────────── */
.avatar-card {
  grid-column: 1 / 2;
  grid-row: 1 / span 2;   /* тянем на две верхние строки */
  align-items: center;
}

/* перенесём стили .pet-img на контейнер */
.img {
  border: 1px solid #000;
}

.pet-img {
  width: 100%;
  height: 100%;
  /* из .pet-img */
  object-fit: contain;          /* хотя object-fit на контейнере мало влияет */
  border-radius: 8px;
  border: 1px solid #000;
  margin-bottom: auto;
  position: relative;
  overflow: hidden;
  aspect-ratio: 1 / 1;
}

.pet-canvas {
  width: 111%;
  height: 111%;
  /* из .pet-img */
  object-fit: contain;          /* хотя object-fit на контейнере мало влияет */
  border-radius: 8px;
  margin-bottom: auto;
  position: relative;
  overflow: hidden;
  aspect-ratio: 1 / 1;
}

/* каждый слой растягиваем, но сохраняем object-fit и border-radius */
.pet-layer {
  position: absolute;
  top: 0;
  left: 0;
  width: 100%;
  height: 100%;
  object-fit: contain;          /* из .pet-img */
  border-radius: 8px;           /* чтобы углы у всех слоёв совпадали */
  pointer-events: none;
}

.pet-layer.layer--base {
  z-index: 3 !important;
}

/* ── Wardrobe button ───────────────────────────────── */
.wardrobe-btn {
  margin-top: 1.25rem;
  padding: 6px 18px;
  border: none;
  border-radius: 8px;
  border: 1px solid #000000cc;
  background:linear-gradient(80deg, #292527be,rgba(78, 158, 153, 0.95));
  color: #fff;
  font-size: 0.9rem;
  cursor: pointer;
  transition: transform .15s ease, box-shadow .15s ease;
}
.wardrobe-btn:hover {
  border-radius: 9px;
  
}

/* ── Stats block ───────────────────────────────────── */
.stats-card {
  grid-column: 2 / 3;
  grid-row: 1;
}
.stats-list {
  list-style: none;
  padding: 0;
  margin: 0;
  font-size: 0.9rem;
  line-height: 1.55rem;
}

/* ── Bio block ─────────────────────────────────────── */
.bio-card {
  grid-column: 2 / 3;
  grid-row: 2;
}
.bio-text { white-space: pre-wrap; line-height: 1.45rem; }
.bio-placeholder {
  margin: auto;
  opacity: .6;
  text-align: center;
  font-style: italic;
}

/* ── Extra blocks (Спутник / Хроника) ─────────────── */
.below-avatar { grid-column: 1; grid-row: 3; }
.below-bio    { grid-column: 2; grid-row: 3; }

/* ── Loader / not-found ───────────────────────────── */
.loader, .not-found {
  grid-column: 1 / -1;
  text-align: center;
  font-family: 'JetBrains Mono', monospace;
  padding: 2rem 0;
}
</style>



