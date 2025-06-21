<template>
  <div class="my-block clan-block">
    <h2>🏕 Мои кланы</h2>

    <div v-if="myClans.length">
      <div 
        v-for="clan in myClans" 
        :key="clan.id" 
        class="my-clan-entry"
      >
        <img 
          :src="getAvatar(clan.avatar_url)" 
          class="clan-avatar"
          :alt="clan.name"
        />
        <div class="clan-info">
          <h3>{{ clan.name }}</h3>
          <p>{{ clan.description || 'Без описания' }}</p>
        </div>
      </div>
    </div>

    <div v-else class="no-clans">
      Сейчас вы не состоите ни в одном клане.
    </div>
  </div>
</template>

<script setup>
import { storeToRefs } from 'pinia'
import { usePlayerStore } from '@/store/player'
import { useClansStore } from '@/store/clans'

const { player } = storeToRefs(usePlayerStore())
const clansStore = useClansStore()

const myClans = computed(() => {
  const ids = player.value?.clans?.map(c => c.id) || []
  return clansStore.clans.filter(clan => ids.includes(clan.id))
})


const getAvatar = (filename) => {
  return filename
    ? `${import.meta.env.VITE_STATIC_URL}/static/clan_avatars/${filename}`
    : '/img/default_clan_avatar.png'
}
</script>

<style scoped>

.my-block {
    height: 200px;
}


.my-clan-entry {
  display: flex;
  align-items: center;
  gap: 10px;
  background: rgba(255, 255, 255, 0.03);
  padding: 10px;
  border-radius: 8px;
  min-height: 250px;
}

.clan-avatar {
  width: 48px;
  height: 48px;
  border-radius: 6px;
  object-fit: cover;
  border: 1px solid rgba(255, 255, 255, 0.1);
}

.clan-info h3 {
  margin: 0;
  font-size: 1.1rem;
}

.no-clans {
  opacity: 0.6;
  font-style: italic;
}
</style>
