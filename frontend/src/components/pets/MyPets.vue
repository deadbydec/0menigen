<template>
  <div class="mypets-wrap">
    <h2 class="title">Тамаглитчи</h2>
    <div class="kennel-grid">
      <template v-for="idx in slotCount" :key="idx">
        <div
          class="kennel-slot"
          :class="{ filled: !!slots[idx - 1] }"
          @click="slots[idx - 1] && goToPet(slots[idx - 1].id)"
          v-tooltip="slots[idx - 1] ? slots[idx - 1].trait : ''"
        >
          <template v-if="slots[idx - 1]">
            <img
              :src="`${STATIC_BASE}/static/${slots[idx - 1].image}`"
              :alt="slots[idx - 1].name"
              @error="onImageError"
            />
            <div class="pet-name">{{ slots[idx - 1].name }}</div>
            <div class="pet-level">{{ slots[idx - 1].level }} lvl</div>
          </template>
          <template v-else>
            <span class="empty-text">пусто</span>
          </template>
        </div>
      </template>
    </div>
  </div>
</template>

<script setup>
import { onMounted, computed } from 'vue'
import { usePetsStore } from '@/store/pets'
import { useRouter } from 'vue-router'

const STATIC_BASE = import.meta.env.VITE_STATIC_URL || 'https://localhost:5002'
const petsStore = usePetsStore()
const router = useRouter()

const slotCount = 6
const pets = computed(() => petsStore.myPets)
const slots = computed(() => {
  const arr = Array.from({ length: slotCount }, () => null)
  pets.value.forEach((p, i) => { if (i < slotCount) arr[i] = p })
  return arr
})

onMounted(() => {
  console.log("🌀 Загружаем питомцев...")
  petsStore.fetchAllPets().then(() => {
    console.log("🐾 Загружены питомцы:", petsStore.myPets)
  })
})


function goToPet(id) {
  router.push(`/pet/${id}`)
}

function onImageError(e) {
  e.target.src = `${STATIC_BASE}/static/goods/no_image.png`
}

onMounted(() => {
  petsStore.fetchAllPets()
})
</script>

<style scoped>

.pet-name,
.pet-level {
  position: relative;
  z-index: 1;
  text-shadow: 0 0 2px rgba(0,0,0,0.8);
  color: #fff;
  font-size: 14px;
  font-weight: bold;
  line-height: 1;
}

.kennel-slot.filled {
  cursor: pointer;
}

.kennel-slot img {
  position: absolute;
  inset: 0;
  width: 80%;
  height: 80%;
  object-fit: contain;
  object-position: center bottom;
  z-index: 0;
  pointer-events: none;
}

.pet-level {
  font-size: 12px;
  opacity: 0.8;
}
.mypets-wrap {
  border: 1px solid rgba(0, 0, 0, 0.384);
  padding: 1rem 1.5rem;
  background-color: rgba(0, 0, 0, 0.35);
  backdrop-filter: blur(6px);
  border-radius: 12px;
  width: fit-content;
  margin: 0 auto;
  color: #fff;
  font-family: 'Fira Code', monospace;
  box-shadow: 0 0 15px rgba(0, 0, 0, 0.5);
}

.title {
  font-size: 20px;
  text-align: center;
  margin-bottom: 1rem;
  text-shadow: 0 1px 2px rgba(0, 0, 0, 0.6);
}

.kennel-grid {
  display: grid;
  grid-template-columns: repeat(3, 160px);
  grid-template-rows: repeat(2, 160px);
  gap: 20px;
  justify-content: center;
}

.kennel-slot {
  position: relative;
  overflow: hidden;
  background: rgba(255, 255, 255, 0.04);
  border: 1px solid rgba(255, 255, 255, 0.08);
  border-radius: 10px;
  text-align: center;
  cursor: default;
  padding: 0; 
}

.kennel-slot.filled {
  cursor: pointer;
}

.kennel-slot.filled:hover {
  background-color: rgba(255, 255, 255, 0.06);
  box-shadow: 0 0 12px rgba(255, 255, 255, 0.08);
}

.kennel-slot img {
  width: 100%;
  height: 100%;
  object-fit: contain;
  object-position: center bottom;
  background: none;
  border-radius: 6px;
}


.pet-name {
  font-weight: bold;
  font-size: 14px;
  margin-bottom: 2px;
}

.pet-level {
  font-size: 12px;
  color: #ccc;
}

.empty-text {
  font-size: 16px;
  color: #777;
}
</style>

