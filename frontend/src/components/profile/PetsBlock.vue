<script setup>
import { onMounted } from 'vue'
import { usePetsStore } from '@/store/pets'

const petsStore = usePetsStore()

onMounted(async () => {
  await petsStore.fetchAllPets()
})
</script>

<template>
  <div class="pets-block">
    <h2>Мои петы</h2>
    <div class="pet-row">
      <div
        v-for="pet in petsStore.myPets"
        :key="pet.id"
        class="pet-avatar"
      >
        <div class="pet-render">
          <img
  v-for="layer in pet.avatar_layers"
  :key="layer.src"
  :src="layer.src"
  class="layer"
/>
        </div>
        <div class="pet-name">{{ pet.name }}</div>
      </div>
    </div>
  </div>
</template>

<style scoped>
.pets-block {
  display: flex;
  flex-direction: column;
  gap: 10px;
  max-width: 588px;
  backdrop-filter: blur(7px);
  background: rgba(38, 32, 39, 0.48);
  border: 1px solid #2e2c2c;
  border-radius: 8px;
  padding: 10px;
  font-size: 13px;
}

.pet-row {
  display: flex;
  gap: 12px;
  flex-wrap: wrap;
}

.pet-avatar {
  display: flex;
  flex-direction: column;
  align-items: center;
  width: 80px;
}

.pet-render {
  position: relative;
  width: 64px;
  height: 64px;
  border-radius: 50%;
  overflow: hidden;
  background: #1f1f1f;
  box-shadow: 0 0 3px rgba(0,0,0,0.5);
}

.layer {
  position: absolute;
  top: 0;
  left: 0;
  width: 64px;
  height: 64px;
  object-fit: cover;
}

.pet-name {
  margin-top: 4px;
  font-size: 12px;
  text-align: center;
  color: #ccc;
}
</style>
