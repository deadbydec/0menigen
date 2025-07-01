<template>
  <div class="neon-circus">
    <div class="games-section">
      <div class="game-card-list">
        <div v-for="game in games" :key="game.id" class="game-card">
          <img
            :src="game.image"
            alt="game preview"
            class="game-image"
            @click="openGame(game)"
          />
          <div class="game-info">
            <h3>{{ game.name }}</h3>
            <p>{{ game.description }}</p>
          </div>
        </div>
      </div>
    </div>
  </div>
  <GameModal
  v-if="showModal"
  :gameComponent="currentGameComponent"
 @close="showModal = false"
/>

</template>

<script setup>
import { ref, markRaw } from 'vue'
import { useRouter } from 'vue-router'
import Match3Game from '@/components/games/Match3Game.vue'
import GameModal from '@/components/games/GameModal.vue' // сам компонент создашь ниже

const showModal = ref(false)
const currentGameComponent = ref(null)

function openGame(game) {
  if (game.id === 1) {
    currentGameComponent.value = markRaw(Match3Game)
  }
  showModal.value = true
}
const router = useRouter()

const games = ref([
  {
    id: 1,
    name: 'Баги в ряд',
    description: 'Собери баги в ряд и заработай немного монет. Осторожно: может затянуть.',
    image: '/static/images/match3.png',
    route: '/games/match3'
  },
  {
    id: 2,
    name: 'Клоунадо',
    description: 'Мини-игра с Клоунидом. Сколько шуток ты выдержишь, прежде чем сойдёшь с ума?',
    image: '/static/images/clownado.png',
    route: '/games/clownado'
  }
])

function goToGame(route) {
  router.push(route)
}
</script>

<style scoped>
.neon-circus {
  margin-top: 100px;
  padding: 30px 10px;
  min-height: 90vh;
  display: flex;
  flex-direction: column;
  align-items: center;
  background: transparent;
  color: white;
}

.games-section {
  width: 100%;
  max-width: 800px;
  display: flex;
  flex-direction: column;
  align-items: center;
}

.games-section h2 {
  font-size: 32px;
  margin-bottom: 20px;
  text-shadow: 0 0 10px cyan;
}

.game-card-list {
  width: 100%;
  display: flex;
  flex-direction: column;
  gap: 20px;
}

.game-card {
  background: #181818e7;
  border: 1px solid rgb(196, 196, 196);
  border-radius: 16px;
  padding: 16px;
  display: flex;
  gap: 16px;
  align-items: center;
  transition: transform 0.2s ease;
  box-shadow: 0 0 12px rgba(111, 0, 255, 0.3);
}

.game-card:hover {
  transform: scale(1.02);
  box-shadow: 0 0 20px rgba(111, 0, 255, 0.6);
}

.game-image {
  width: 180px;
  height: 180px;
  object-fit: cover;
  border-radius: 12px;
  background: #111;
}

.game-info {
  flex: 1;
  display: flex;
  flex-direction: column;
  gap: 6px;
}

.game-info h3 {
  font-size: 20px;
  margin: 0;
}

.game-info p {
  font-size: 14px;
  color: #ccc;
  margin: 0;
}

button {
  align-self: flex-start;
  background: #6f00ff;
  color: white;
  padding: 6px 12px;
  border-radius: 8px;
  border: none;
  cursor: pointer;
  transition: background 0.2s;
}

button:hover {
  background: #9e00ff;
}
</style>

  