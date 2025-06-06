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
    <section class="glass-card below-avatar">
  <h3 class="card-title">Компаньон</h3>
  <p>Здесь будет инфа о прирученном спутнике 
    этого питомца.</p>
</section>

    <!-- ╭─ Stats ───────────────────────────────────────────╮ -->
    <section class="glass-card stats-card" v-if="!isLoading && pet">
      <h3 class="card-title">Статистика</h3>
      <ul class="stats-list">
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
      <p class="bio-text" v-if="pet.bio?.trim().length">
        {{ pet.bio }}
      </p>
      <p class="bio-placeholder" v-else>
        Расскажите о&nbsp;питомце… 📝
      </p>
    </section>
    <section class="glass-card below-bio">
  <h3 class="card-title">Реликвии</h3>
  <p>Здесь можно отобразить значимые предметы для этого питомца</p>
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

const route         = useRoute()
const router        = useRouter()
const petsStore     = usePetsStore()
const renderStore   = usePetRenderStore()
const wardrobeStore = useWardrobeStore()


const isLoading = ref(true)
const petId = Number(route.params.id)
const pet = computed(() => petsStore.myPets.find(p => p.id === petId))

const layers = ref([])


onMounted(async () => {
  const petId = Number(route.params.id)

  await petsStore.fetchPetById(petId)
  const realPetId = petsStore.currentPet?.id
  if (realPetId) {
    await renderStore.fetchAppearance(realPetId, true)
  }

  await wardrobeStore.fetchWardrobe()

  if (pet.value?.id) {
    layers.value = buildLayersCustom(
      pet.value,
      renderStore.appearances[pet.value.id] || [],
      renderStore.getSlotOrderFor(pet.value.id),
      layer => {
        return layer.rid != null
          ? wardrobeStore.byRid(layer.rid)
          : wardrobeStore.byPid(layer.pid)
      }
    )
  }

  isLoading.value = false
})

onMounted(async () => {
  // 1. если питомцы ещё не загружены, грузим всех
  if (!petsStore.myPets.length) {
    await petsStore.fetchAllPets()
  }

  // 2. загружаем внешний вид (appearance) и гардероб
  await Promise.all([
    renderStore.fetchAppearance(petId, true),
    wardrobeStore.fetchWardrobe()
  ])

  isLoading.value = false
})


function formatDate(iso) {
  return iso ? dayjs(iso).format('DD.MM.YYYY HH:mm') : '—'
}

function openWardrobe() {
  if (pet.value?.id) {
    router.push({ path: '/wardrobe', query: { pet: pet.value.id } })
  }
}



watchEffect(() => {
  if (pet.value?.id) {
    layers.value = renderStore.getLayersForPet(pet.value.id)
  }
})
</script>




<style scoped>
/* ── Grid layout ───────────────────────────────────── */
.pet-grid {
  display: grid;
  grid-template-columns: 360px 1fr;   /* левая колонка уже, правая — всё остальное */
  grid-template-rows: auto auto auto; /* 1-я строка stats, 2-я bio, 3-я extra */
  column-gap: 2.0rem;
  row-gap: 2rem;                      /* горизонтальный и вертикальный «воздух» */
  max-width: 900px;
  margin: 1rem auto;                  /* внешний отступ сверху/снизу */
  padding: 0 1.5rem 2rem;             /* внутренний отступ по бокам + снизу */
  box-sizing: border-box;
}

/* ── Glasslite base ────────────────────────────────── */
.glass-card {
  background:rgba(38, 32, 39, 0.664);
  width: 100%;
  /* height убрали, чтобы карточка росла только по содержимому */
  border: 1px solid #000;
  backdrop-filter: blur(7px);
  box-shadow: 0 0 15px rgba(0, 0, 0, 0.4);
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



