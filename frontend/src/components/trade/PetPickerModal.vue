<template>
  <div v-if="visible" class="picker-modal">
    <div class="picker-content pets-block">
      <h2>Выбери питомца</h2>

      <div v-if="petsStore.isLoadingAll" class="loading">Загрузка...</div>
      <div v-else-if="petsStore.myPets.length === 0" class="empty">Нет доступных питомцев</div>

      <div class="pet-row">
        <div
          v-for="pet in petsStore.myPets"
          :key="pet.id"
          class="pet-avatar"
          @click="selectPet(pet)"
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

      <div class="buttons">
        <button @click="$emit('close')">❌ Отмена</button>
      </div>
    </div>
  </div>
</template>

<script setup>
import { onMounted } from 'vue'
import { usePetsStore } from '@/store/pets'

const petsStore = usePetsStore()
defineProps({ visible: Boolean })
const emit = defineEmits(['close', 'select'])

function orderedLayers(layers) {
  return [...(layers || [])].sort((a, b) => a.z - b.z)
}

function selectPet(pet) {
  emit('select', pet)
  emit('close')
}

onMounted(() => {
  petsStore.fetchAllPets()
})
</script>

<style scoped>
.picker-modal {
  position: fixed;
  inset: 0;
  z-index: 999;
  background: transparent;
  display: flex;
  align-items: center;
  justify-content: center;
}

.picker-content {
  width: 550px;
  gap: 10px;
  height: 390px;
  background: #181818e7;
  border: 1px solid rgb(196, 196, 196);
  border-radius: 18px;
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
  width: 130px;
  cursor: pointer;
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

.layer {
  position: absolute;
  width: 196px;
  height: 196px;
  top: -35px;
  left: -17px;
  transform: scale(1.1);
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

h2::after {
  content: "";
  display: block;
  width: 100%;
  height: 1px;
  background-color: white;
  opacity: 0.4;
  margin: 6px auto 0;
  border-radius: 1px;
}

.buttons {
  margin-top: 130px;
  margin-left: 120px;
  width: 300px;
  display: flex;
  justify-content: center;
  border-radius: 18px;
}
</style>

