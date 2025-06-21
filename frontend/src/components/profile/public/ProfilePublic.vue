<script setup>
import { computed, ref, onMounted, watch } from 'vue'
import { useRoute, useRouter } from 'vue-router'

// 🧠 Новый стор для публичных профилей
import { usePublicPlayerStore } from '@/store/publicPlayer'
// 👤 Личный стор
import { usePlayerStore } from '@/store/player'

import FriendsBlockPublic from './FriendsBlockPublic.vue'
import CollectBlockPublic from './CollectBlockPublic.vue'
import BioBlockPublic from './BioBlockPublic.vue'
import WallBlockPublic from './WallBlockPublic.vue'
import PetsBlockPublic from './PetsBlockPublic.vue'
import AchievementsBlockPublic from './AchievementsBlockPublic.vue'
import AvatarBlockPublic from './AvatarBlockPublic.vue'

const route = useRoute()
const router = useRouter()

const publicPlayerStore = usePublicPlayerStore()
const playerStore = usePlayerStore()

const isLoading = ref(true)
const errorMessage = ref('')

// 👤 текущий юзер
const currentUser = computed(() => playerStore.player)
// 🌐 просматриваемый профиль
const profile = computed(() => publicPlayerStore.publicProfile)

const isOwner = computed(() => {
  return profile.value?.id && currentUser.value?.id &&
    profile.value.id === currentUser.value.id
})

async function loadProfile(id) {
  isLoading.value = true
  errorMessage.value = ''

  try {
    if (!currentUser.value) await playerStore.fetchPlayer()
    publicPlayerStore.myId = currentUser.value?.id || null

    await publicPlayerStore.fetchPublicProfile(id)

    if (isOwner.value) {
      router.replace('/profile')
      return
    }
  } catch (err) {
    console.error('❌ Ошибка загрузки публичного профиля:', err)
    errorMessage.value = 'Ошибка загрузки профиля'
  } finally {
    isLoading.value = false
  }
}

onMounted(() => {
  loadProfile(Number(route.params.id))
})

watch(() => route.params.id, newId => {
  loadProfile(Number(newId))
})
</script>

<template>
  <div v-if="isLoading">Загрузка профиля...</div>
  <div v-else-if="errorMessage">{{ errorMessage }}</div>
  <div v-else :key="profile.id">
      <div class="profile-wrapper">
    <div class="profile-container">
      <!-- ✅ Левая колонка -->
      <div class="left-column">
        <AvatarBlockPublic :profile="profile" />
        <AchievementsBlockPublic :profile="profile" />
      </div>

      <!-- ✅ Центр -->
      <div class="center-column">
        <BioBlockPublic :profile="profile" />
        <WallBlockPublic :profile="profile" />
        <PetsBlockPublic :user-id="profile.id" />
      </div>

      <!-- ✅ Правая -->
      <div class="right-column">
        <CollectBlockPublic :profile="profile" />
        <FriendsBlockPublic :user-id="profile.id" />
      </div>
    </div>
  </div>
  </div>
</template>


<style scoped>
.profile-wrapper {
  display:flex;
  justify-content: center;
  width: 100%;
  padding: 20px;
  box-sizing: border-box;
  padding-top:100px;
}

.profile-container {
  width: auto;
  max-width: 1300px; /* 💥 Твоя желаемая ширина */
  display: grid;
  grid-template-columns: 1fr 2fr 1fr;
  gap: 10px;
  background: rgba(255, 0, 0, 0.1);
}

.left-column,
.center-column,
.right-column {
  display: flex;
  flex-direction: column;
  gap: 10px;
}

.avatar-block,
.bio-block,
.wall-block,
.friends-block,
.achievements-block,
.collect-block,
.pets-block {
  background: rgba(38, 32, 39, 0.48);
  padding: 16px;
  border-radius: 10px;
  box-shadow: 0 2px 5px rgba(0, 0, 0, 0.1);
  font-family: 'JetBrains Mono', monospace;
  backdrop-filter: blur(7px);
}
</style>


