// store/pets.js
import { defineStore } from 'pinia'
import { ref } from 'vue'
import api from '@/utils/axios'

export const usePetsStore = defineStore('pets', () => {
  /* ── state ───────────────────────────────────────────── */
  const myPets       = ref([])   // список всех питомцев текущего игрока
  const currentPet   = ref(null) // подробности выбранного питомца

  const isLoadingAll = ref(false)
  const isLoadingOne = ref(false)

  /* ── actions ─────────────────────────────────────────── */

  /** Получить всех питомцев пользователя */
  async function fetchAllPets () {
    
    isLoadingAll.value = true
    
    try {
      const res = await api.get('/pets/', { withCredentials: true })
      myPets.value = res.data
      console.log('🐾 myPets после запроса:', res.data)
    } finally {
      isLoadingAll.value = false
    }
  }

  /** Получить конкретного питомца по id */
  async function fetchPetById (id) {
    if (!id) return
    isLoadingOne.value = true
    try {
      const res = await api.get(`/pets/${id}`, { withCredentials: true })
      currentPet.value = res.data
    } finally {
      isLoadingOne.value = false
    }
  }

  /** Сбросить текущего питомца (при уходе со страницы) */
  function clearCurrentPet () {
    currentPet.value = null
  }

  /* ── expose ──────────────────────────────────────────── */
  return {
    myPets,
    currentPet,
    isLoadingAll,
    isLoadingOne,

    fetchAllPets,
    fetchPetById,
    clearCurrentPet,
  }
})
