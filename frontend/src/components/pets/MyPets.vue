<template>
  <div class="page-inner">
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
  <div class="pet-render-full">
    <img
      v-for="layer in orderedLayers(slots[idx - 1].avatar_layers)"
      :key="layer.src + layer.z"
      :src="layer.src"
      class="layer-full"
      :style="{ zIndex: layer.z }"
    />
  </div>
  <div class="pet-name">{{ slots[idx - 1].name }}</div>
  <div class="pet-level">{{ slots[idx - 1].level }} lvl</div>
</template>

          <template v-else>
            <span class="empty-text">пусто</span>
          </template>
        </div>
      </template>
    </div>
  </div></div>
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

function orderedLayers(layers) {
  return [...(layers || [])].sort((a, b) => a.z - b.z)
}



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

.pet-render-full {
  position: relative;
  width: 100%;
  height: 100%;
}

.layer-full {
  position: absolute;
  top: 0;
  left: 0;
  width: 100%;
  height: 100%;
  object-fit: contain;
  image-rendering: pixelated;
  pointer-events: none;
}


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
  border: 1px solid rgb(196, 196, 196);
  padding: 1rem 1.5rem;
  background: #181818e7;
  border-radius: 18px;
  width: 900px;
  height: 650px;
  margin: 60px auto;
  color: #fff;
  box-shadow: 0 0 15px rgba(0, 0, 0, 0.5);
}

.title {
  font-size: 30px;
  text-align: center;
  margin-bottom: 1rem;
  text-shadow: 0 1px 2px rgba(0, 0, 0, 0.6);
}

.kennel-grid {
  display: grid;
  grid-template-columns: repeat(3, 260px);
  grid-template-rows: repeat(3, 260px);
  gap: 30px;
  justify-content: center;
}

.kennel-slot {
  position: relative;
  overflow: hidden;
  background:transparent;
  border: 1px solid rgb(196, 196, 196);
  border-radius: 10px;
  text-align: center;
  cursor: default;
  padding: 0; 
}

.kennel-slot.filled {
  cursor: pointer;
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

