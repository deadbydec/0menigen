<template>
  <div class="quest-board">
    <h1>КВЕСТЫ</h1>
    <div class="npc-grid">
      <div
  v-for="npc in questStore.npcs"
  :key="npc.id"
  class="npc-cell"
>
  <div class="npc-avatar" @click="goToNPC(npc.id)">
    <img :src="getAvatarUrl(npc.avatar)" alt="NPC" />
  </div>
  <div class="npc-name">{{ npc.name }}</div>
</div>

    </div>
  </div>
</template>

<script setup>
import { onMounted } from "vue"
import { useRouter } from "vue-router"
import { useQuestStore } from "@/store/questStore"

const questStore = useQuestStore()
const router = useRouter()
const STATIC_BASE = import.meta.env.VITE_STATIC_URL || 'https://localhost:5002'

function getAvatarUrl(filename) {
  return `${STATIC_BASE}/static/npcs/${filename}`
}

function goToNPC(npcId) {
  router.push(`/npc_quests/${npcId}`)
}


onMounted(() => {
  questStore.fetchNPCs()
})
</script>

<style scoped lang="scss">
.quest-board {
  max-width: 1000px;
  width: 800px;
  height: 600px;
  margin: 40px auto;
  margin-top: 120px;
  padding: 30px;
  border-radius: 16px;
  background: #181818e7;
  border: 1px solid rgb(196, 196, 196);
  box-shadow: 0 0 40px rgba(0, 0, 0, 0.2);
  color: #fff;

  h1 {
    text-align: center;
    margin-bottom: 30px;
    font-size: 28px;
    letter-spacing: 2px;
  }

  .npc-grid {
    display: grid;
    grid-template-columns: repeat(auto-fill, minmax(150px, 1fr));
    gap: 30px;
    justify-items: center;
  }

  .npc-cell {
    cursor: pointer;
    display: flex;
    flex-direction: column;
    align-items: center;
    transition: transform 0.2s ease;

    &:hover {
      transform: scale(1.05);
    }

    .npc-avatar {
      width: 155px;
      height: 155px;
      border-radius: 50%;
      overflow: hidden;
      border: 2px solid rgba(255, 255, 255, 0.3);
      box-shadow: 0 0 10px rgba(0, 0, 0, 0.4);

      img {
        width: 100%;
        height: 100%;
        object-fit: cover;
        border-radius: 50%;
      }
    }

    .npc-name {
      margin-top: 10px;
      font-size: 16px;
      font-weight: bold;
      text-align: center;
      color: #f0f0f0;
      text-shadow: 0 0 3px rgba(0, 0, 0, 0.6);
    }
  }
}
</style>

