import { defineStore } from 'pinia'
import { ref } from 'vue'
import api from '@/utils/axios'
import { useToastStore } from '@/store/toast'

export const useWardrobeStore = defineStore('wardrobe', () => {
  /* state */
  const items = ref([])          // содержимое гардероба
  const isLoading = ref(false)
  const toast = useToastStore()

  /* actions */
  async function fetchWardrobe () {
    isLoading.value = true
    try {
      const res = await api.get('/wardrobe/', { withCredentials: true })
      items.value = res.data
    } finally { isLoading.value = false }
  }

async function addToWardrobe (inventoryId) {
  await api.post('/wardrobe/add', { item_id: inventoryId }, { withCredentials: true })
  toast.addToast('⚡ В гардероб!', { type: 'success' })
  await fetchWardrobe()
}

async function removeFromWardrobe (productId) {
  await api.post('/wardrobe/remove', { product_id: productId, quantity: 1 }, { withCredentials: true })
  toast.addToast('⬅ Вернули в инвентарь', { type: 'success' })
  await fetchWardrobe()
}



  return { items, isLoading, fetchWardrobe, addToWardrobe, removeFromWardrobe }
})
