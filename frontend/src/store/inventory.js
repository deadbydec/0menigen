// store/inventory.js
import { defineStore } from 'pinia'
import { ref } from 'vue'
import api from '@/utils/axios'
import { useToastStore } from '@/store/toast'

export const useInventoryStore = defineStore('inventory', () => {
  /* ── state ─────────────────────────────────────────────── */
  const inventory     = ref([])
  const userRace      = ref('')
  const selectedItem  = ref(null)
  const toastStore    = useToastStore()

  const tradableItems = computed(() =>
  inventory.value.filter(i => !i.is_equipped && !i.locked && !i.in_safe && !i.in_trade)
)

  /* ── helpers ───────────────────────────────────────────── */
  function getCookie (name) {
    const m = document.cookie.match(new RegExp('(^| )' + name + '=([^;]+)'))
    return m ? m[2] : null
  }
  const csrf = () => getCookie('csrf_access_token')   // свежий токен каждый раз

  /* ▸ перезагрузка инвентаря из API */
  async function fetchInventory () {
    try {
      const { data } = await api.get('/inventory/', {
        withCredentials: true,
        headers: { 'Cache-Control': 'no-cache', Pragma: 'no-cache' }
      })
      inventory.value = (data.inventory || []).filter(i => i.quantity > 0)
      userRace.value  = data.user_race || ''
    } catch (err) {
      console.error('fetchInventory:', err)
      toastStore.addToast('Ошибка загрузки инвентаря', { type: 'error' })
    }
  }

  /* ── generic guard ─────────────────────────────────────── */
  function guardSelected (actionName) {
    if (!selectedItem.value) {
      toastStore.addToast(`Нет выбранного предмета для «${actionName}»`, { type: 'error' })
      return false
    }
    return true
  }

  /* ▸ USE (НЕ для яиц) */
  async function useItem () {
    if (!guardSelected('использования')) return

    // запрещаем «use» для яиц
    if (selectedItem.value.type === 'creature') {
      toastStore.addToast('Это яйцо. Выберите «Инкубировать / Вылупить».', { type: 'info' })
      return
    }

    try {
      const { data } = await api.post(
        `/inventory/use/${selectedItem.value.id}`,
        null,
        { withCredentials: true, headers: { 'X-CSRF-TOKEN': csrf() } }
      )
      toastStore.addToast(data.message, { type: 'success' })
    } catch (err) {
      console.error('useItem:', err)
      toastStore.addToast('Не удалось использовать предмет', { type: 'error' })
    } finally {
      await fetchInventory()
      selectedItem.value = null
    }
  }

  /* ▸ INCUBATE */
  async function incubateItem () {
    if (!guardSelected('инкубации')) return

    if (selectedItem.value.type !== 'creature') {
      toastStore.addToast('Выберите яйцо для инкубации', { type: 'error' })
      return
    }

    try {
      const { data } = await api.post(
        `/inventory/incubate/${selectedItem.value.id}`,
        null,
        { withCredentials: true, headers: { 'X-CSRF-TOKEN': csrf() } }
      )
      toastStore.addToast(data.message || 'Инкубация началась!', { type: 'success' })
    } catch (err) {
      const msg = err.response?.data?.detail || 'Ошибка запуска инкубации'
      toastStore.addToast(msg, { type: 'error' })
      console.error('incubateItem:', err)
    } finally {
      await fetchInventory()
      selectedItem.value = null
    }
  }

  /* ▸ DISCARD */
  async function destroyItem () {
    if (!guardSelected('выброса')) return
    try {
      const { data } = await api.delete(
        `/inventory/discard/${selectedItem.value.id}`,
        { withCredentials: true, headers: { 'X-CSRF-TOKEN': csrf() } }
      )
      toastStore.addToast(data.message, { type: 'success' })
    } catch (err) {
      console.error('destroyItem:', err)
      toastStore.addToast('Ошибка при выбрасывании предмета', { type: 'error' })
    } finally {
      await fetchInventory()
      selectedItem.value = null
    }
  }

  /* ▸ RECYCLE (только для Наллвур) */
  async function recycleItem () {
    if (!guardSelected('переработки')) return
    try {
      const { data } = await api.post(
        `/inventory/recycle/${selectedItem.value.id}`,
        null,
        { withCredentials: true, headers: { 'X-CSRF-TOKEN': csrf() } }
      )
      toastStore.addToast(data.message, { type: 'success' })
    } catch (err) {
      const msg = err.response?.data?.detail || 'Ошибка переработки'
      toastStore.addToast(msg, { type: 'error' })
      console.error('recycleItem:', err)
    } finally {
      await fetchInventory()
      selectedItem.value = null
    }
  }

  /* ▸ SAFE / VAULT */
  async function sendToVault (itemId, qty = 1) {
    try {
      const { data } = await api.post(
        '/safe/vault/deposit-item',
        { item_id: itemId, quantity: qty },
        { withCredentials: true, headers: { 'X-CSRF-TOKEN': csrf() } }
      )
      toastStore.addToast(data.message, { type: 'success' })
      await fetchInventory()
      selectedItem.value = null
      return data
    } catch (err) {
      const msg = err.response?.data?.detail || 'Не удалось убрать предмет в сейф'
      toastStore.addToast(msg, { type: 'error' })
      console.error('sendToVault:', err)
      throw err
    }
  }

  async function useBookOnPet(petId, productId) {
  const res = await api.post(`/pets/${petId}/use_book`, {
    product_id: productId
  }, { withCredentials: true })

  return res.data
}


  /* ▸ SELECT / TOGGLE */
  function selectItem (item) {
    // если пришёл null → просто очистить
    if (!item) {
      selectedItem.value = null
      return
    }
    selectedItem.value = selectedItem.value?.id === item.id ? null : item
  }

  /* ── expose ────────────────────────────────────────────── */
  return {
    useBookOnPet,
    inventory,
    userRace,
    selectedItem,
    tradableItems,
    fetchInventory,
    useItem,
    incubateItem,
    destroyItem,
    recycleItem,
    sendToVault,
    selectItem
  }
})


