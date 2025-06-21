import { defineStore } from 'pinia'
import { ref } from 'vue'
import api from '@/utils/axios'
import { useToastStore } from '@/store/toast'

export const useLandfillStore = defineStore('landfill', () => {
  const landfillItems = ref([])
  const limitInfo = ref({ used: 0, max: 3 })

  const toast = useToastStore()

  // 🔄 Получить список предметов на свалке
  async function fetchItems() {
    try {
      const res = await api.get('/landfill', { withCredentials: true })
      landfillItems.value = res.data || []
    } catch (err) {
      console.error('❌ Ошибка загрузки свалки:', err)
    }
  }

  // 📊 Получить текущий лимит подбора
  async function fetchLimit() {
    try {
      const res = await api.get('/landfill/limit', { withCredentials: true })
      limitInfo.value = res.data || { used: 0, max: 3 }
    } catch (err) {
      console.error('❌ Ошибка загрузки лимита:', err)
    }
  }

  // 🤲 Подобрать предмет со свалки
  async function pickupItem(item) {
    try {
      const res = await api.post(`/landfill/pickup/${item.id}`, {}, { withCredentials: true })
      toast.success(res.data?.message || '🎉 Предмет подобран!')
      await Promise.all([fetchItems(), fetchLimit()])
    } catch (err) {
      const msg = err.response?.data?.detail || '❌ Не удалось подобрать предмет'
      toast.error(msg)
      throw err
    }
  }

  return {
    landfillItems,
    limitInfo,
    fetchItems,
    fetchLimit,
    pickupItem,
  }
})



