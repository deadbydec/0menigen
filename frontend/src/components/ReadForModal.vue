<template>
  <div v-if="visible" class="read-modal">
    <div class="read-modal-content">
      <h2>📖 {{ title || 'Выбери питомца для прочтения' }}</h2>
      <p class="caption">Питомцы, которые ещё не читали эту книгу:</p>

      <div class="pet-grid">
        <div
          class="pet-card"
          v-for="pet in pets"
          :key="pet.id"
          :class="{ selected: selectedPet?.id === pet.id }"
          @click="selectedPet = pet"
        >
          <img
            :src="`/api/pets/${pet.id}/avatar`"
            :alt="pet.name"
            class="pet-avatar"
          />
          <div class="pet-name">{{ pet.name }}</div>
          <div class="pet-stats">🧠 {{ pet.intelligence }}</div>
        </div>
      </div>

      <div v-if="!pets.length" class="no-pets">
        Все питомцы уже прочитали эту книгу
      </div>

      <div class="bottom-bar">
        <button
          class="ghost-button"
          :disabled="!selectedPet"
          @click="$emit('select', selectedPet.id)"
        >
          📘 Прочитать
        </button>
        <button class="ghost-button" @click="$emit('close')">❌ Закрыть</button>
      </div>
    </div>
  </div>
</template>


<script setup>
import { ref } from 'vue'

defineProps({
  visible: Boolean,
  pets: Array,
  title: String
})

defineEmits(['close', 'select'])

const selectedPet = ref(null)
</script>


<style scoped>

.pet-card.selected {
  outline: 2px solid #00cfcf;
  background: #2f2f2f;
}

.read-modal {
  position: fixed;
  inset: 0;
  display: flex;
  align-items: center;
  justify-content: center;
  background: rgba(5, 5, 5, 0.75);
  z-index: 9999;
  animation: fadeIn 0.2s ease;
}

.read-modal-content {
  background: #181818;
  border-radius: 12px;
  padding: 24px 30px;
  width: 90%;
  max-width: 820px;
  color: #fff;
  box-shadow: 0 0 30px rgba(0,0,0,0.6);
  animation: scaleIn 0.25s ease;
  font-family: 'Fira Code', monospace;
}

.caption {
  margin: 0.3em 0 1em;
  color: #aaa;
  font-size: 0.9em;
  text-align: center;
}

.pet-grid {
  display: grid;
  grid-template-columns: repeat(5, 1fr); /* 💡 ровно 5 */
  gap: 1em;
  margin-top: 1em;
}

.pet-card {
  background: #232323;
  border-radius: 8px;
  padding: 12px;
  text-align: center;
  border: 1px solid rgba(255,255,255,0.1);
  transition: 0.2s ease;
}

.pet-card:hover {
  transform: scale(1.03);
  background: #2a2a2a;
}

.pet-avatar {
  width: 80px;
  height: 80px;
  border-radius: 8px;
  object-fit: cover;
  margin-bottom: 0.6em;
  background: #111;
}

.pet-name {
  font-weight: bold;
  font-size: 0.95em;
  margin-bottom: 0.2em;
  white-space: nowrap;
  overflow: hidden;
  text-overflow: ellipsis;
}

.pet-stats {
  font-size: 0.85em;
  color: #bbb;
  margin-bottom: 0.6em;
}

.pet-card button {
  font-size: 0.9em;
  padding: 0.3em 0.8em;
  border: none;
  border-radius: 6px;
  cursor: pointer;
  background: linear-gradient(20deg, #06c2c2, #089a9a);
  color: black;
  font-weight: bold;
  transition: 0.2s ease;
}

.bottom-bar {
  display: flex;
  justify-content: center;
  margin-top: 2em;
}

.ghost-button {
  background: #333;
  border: none;
  padding: 0.6em 1.2em;
  border-radius: 8px;
  color: #fff;
  font-weight: bold;
  cursor: pointer;
}

.no-pets {
  text-align: center;
  font-style: italic;
  color: #888;
  margin-top: 1em;
}

@keyframes fadeIn {
  0%   { opacity: 0 }
  100% { opacity: 1 }
}

@keyframes scaleIn {
  0%   { transform: scale(0.9); opacity: 0 }
  100% { transform: scale(1);   opacity: 1 }
}
</style>
