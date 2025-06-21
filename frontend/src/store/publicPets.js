import { defineStore } from 'pinia'
import { ref } from 'vue'
import api from '@/utils/axios'

export const usePublicPetsStore = defineStore('publicPets', () => {
  const allPets = ref([]) // чужие петы
  const isLoading = ref(false)

  async function fetchAllPets(userId) {
    if (!userId) return
    isLoading.value = true
    try {
      const res = await api.get(`/pets/public/${userId}`)
      allPets.value = res.data
    } finally {
      isLoading.value = false
    }
  }

  function clear() {
    allPets.value = []
  }

  return {
    allPets,
    isLoading,
    fetchAllPets,
    clear,
  }
})

