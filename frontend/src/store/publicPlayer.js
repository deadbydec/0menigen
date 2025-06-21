import { defineStore } from "pinia"
import { ref, computed } from "vue"
import api from "@/utils/axios"

export const usePublicPlayerStore = defineStore("publicPlayer", () => {
  const publicProfile = ref(null)
  const myId = ref(null) // 🧠 Для вычисления isOwner, если надо

  const isOwner = computed(() => {
    return (
      publicProfile.value?.id &&
      myId.value &&
      publicProfile.value.id === myId.value
    )
  })

  async function fetchPublicProfile(userId) {
    try {
      const { data } = await api.get(`/players/public/${userId}`)
      publicProfile.value = {
        id: data.id,
        username: data.username,
        user_type: data.usertype,
        avatar: data.avatar,
        bio: data.bio,
        level: data.level,
        xp: 0,
        nextLevelXp: 1,
        race: data.race,
        gender: data.gender,
        registrationDate: data.registrationDate,
        status: data.status || "offline",
        coins: data.coins || 0,
      }
    } catch (e) {
      console.error("❌ Ошибка загрузки публичного профиля:", e)
      publicProfile.value = null
    }
  }

  function clearPublicProfile() {
    publicProfile.value = null
  }

  return {
    publicProfile,
    myId,
    isOwner,
    fetchPublicProfile,
    clearPublicProfile,
  }
})
