// store/pets.js
import { defineStore } from 'pinia'
import { ref } from 'vue'
import api from '@/utils/axios'


export const usePetsStore = defineStore('pets', () => {
  const myPets       = ref([])
  const currentPet   = ref(null)
  const isLoadingAll = ref(false)
  const isLoadingOne = ref(false)

  async function fetchAllPets () {
    isLoadingAll.value = true
    try {
      const res = await api.get('/pets/', { withCredentials: true })
      myPets.value = res.data
    } finally {
      isLoadingAll.value = false
    }
  }

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

  function clearCurrentPet () {
    currentPet.value = null
  }

  async function updatePetBio (petId, biography) {
    const res = await api.post(`/pets/${petId}/bio`, { biography }, { withCredentials: true })
    return res.data
  }

async function tameCompanion (petId, product_id) {
  const res = await api.post(`/pets/${petId}/companion`, {
    product_id,
    name: "",
    description: ""
  }, { withCredentials: true })

  if (res.data.success) {
    await fetchPetById(petId)  // 🔄 обновляем текущее состояние питомца
  }

  return res.data
}


  async function editCompanion (petId, name, description) {
    const res = await api.post(`/pets/${petId}/companion/edit`, {
      name,
      description
    }, { withCredentials: true })
    return res.data
  }

  async function setFavoriteItems (petId, item_ids) {
    const res = await api.post(`/pets/${petId}/favorite-items`, {
      item_ids
    }, { withCredentials: true })
    return res.data
  }

  async function removeCompanion(petId) {
  const res = await api.post(`/pets/${petId}/companion/remove`)
  if (res.data.success) {
    await fetchPetById(petId)
  }
}


  return {
    myPets,
    removeCompanion,
    currentPet,
    isLoadingAll,
    isLoadingOne,

    fetchAllPets,
    fetchPetById,
    clearCurrentPet,
    updatePetBio,
    tameCompanion,
    editCompanion,
    setFavoriteItems,
  }
})

