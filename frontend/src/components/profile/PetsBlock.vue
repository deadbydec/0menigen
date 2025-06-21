<script setup>
import { onMounted } from 'vue'
import { usePetsStore } from '@/store/pets'
import { useRouter } from 'vue-router'

const petsStore = usePetsStore()
const router = useRouter()

function orderedLayers(layers) {
  return [...(layers || [])].sort((a, b) => a.z - b.z)
}

function openPet(pet) {
  router.push(`/pet/${pet.id}`)
}

onMounted(async () => {
  await petsStore.fetchAllPets()
})
</script>

<template>
  <div class="pets-block">
    <h2>Тамаглитчи</h2>
    <div class="pet-row">
      <div
        v-for="pet in petsStore.myPets"
        :key="pet.id"
        class="pet-avatar"
        @click="openPet(pet)"
      >
        <div class="mini-head-mask">
          <div class="pet-render">
            <img
              v-for="layer in orderedLayers(pet.avatar_layers)"
              :key="layer.src + layer.z"
              :src="layer.src"
              class="layer"
              :class="`layer-${layer.slot}`"
              :style="{ zIndex: layer.z }"
            />
          </div>
        </div>
        <div class="pet-name">{{ pet.name }}</div>
      </div>
    </div>
  </div>
</template>

<style>
.pets-block {
  max-width: 600px;

  gap: 10px;
  height: 190px;
  max-width: 588px;
  backdrop-filter: blur(7px);
  background: rgba(38, 32, 39, 0.48);
  border: 1px solid #2e2c2c;
  border-radius: 8px;
  padding: 10px;
  font-size: 13px;
}

h2 {
  margin: 0 0 12px;
  font-size: 20px;
  color: white;
}

.pet-row {
  display: flex;
  gap: 5px;
  flex-wrap: wrap;
}

.pet-avatar {
  display: flex;
  flex-direction: column;
  align-items: center;
  width: 130px; /* подогнано под увеличенную маску */
  cursor: pointer; /* 👈 добавь это */
}

.mini-head-mask {
  width: 100px;
  height: 100px;
  border-radius: 50%;
  overflow: hidden;
  background: #1f1f1f;
  position: relative;
}

.pet-render {
  position: relative;
  width: 88px;
  height: 88px;
}

/* 🎯 МАСШТАБ — прямо на каждом слое */
.layer {
  position: absolute;
  width: 196px;
  height: 196px;
  top: -35px;
  left: -17px;

  transform: scale(1.1); /* чуть меньше чтобы не вылезал за края */
  transform-origin: center;

  object-fit: cover;
  pointer-events: none;
  image-rendering: pixelated;
}


.pet-name {
  margin-top: 4px;
  font-size: 12px;
  text-align: center;
  color: #ccc;
}

.pets-block h2 {
  position: relative;
  font-size: 18px;
  text-align: left;
  color: white;
  margin-bottom: 8px;
}

.pets-block h2::after {
  content: "";
  display: block;
  width: 100%;
  height: 1px;
  background-color: white;
  opacity: 0.4; /* 👈 мягкий, неяркий акцент */
  margin: 6px auto 0;
  border-radius: 1px;
}
</style>

