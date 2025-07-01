// store/vipshop.js

import { defineStore } from "pinia"
import { ref } from "vue"
import api from "@/utils/axios"
import { useInventoryStore } from "@/store/inventory"
import { usePlayerStore } from "@/store/player"
import { useToastStore } from "@/store/toast"

export const useVipShopStore = defineStore("vipshop", () => {
  const vipItems = ref([])
  const toastStore = useToastStore()

  async function fetchVipItems() {
    try {
      const res = await api.get("/donateshop/", { withCredentials: true })
      vipItems.value = res.data.products || []
    } catch (e) {
      console.error("❌ [VIP] Ошибка загрузки:", e)
      toastStore.addToast("Ошибка загрузки VIP-магазина", { type: "error" })
    }
  }

  async function buyVipProduct(productId) {
    const csrfToken = document.cookie.match(/csrf_access_token=([^;]+)/)?.[1]
    if (!csrfToken) {
      toastStore.addToast("CSRF-токен не найден", { type: "error" })
      return
    }

    try {
      const res = await api.post(`/donateshop/buy/${productId}`, null, {
        headers: { "X-CSRF-TOKEN": csrfToken },
        withCredentials: true,
      })

      toastStore.addToast(res.data.message || "🧿 Покупка успешна!", { type: "success" })

      const playerStore = usePlayerStore()
      const inventoryStore = useInventoryStore()
      await Promise.all([
        playerStore.fetchPlayer(),
        inventoryStore.fetchInventory(),
        fetchVipItems()
      ])
    } catch (err) {
      const msg = err?.response?.data?.detail || "Ошибка при покупке!"
      toastStore.addToast(msg, { type: "error" })
      console.error("❌ [VIP] Ошибка покупки:", err)
    }
  }

  return {
    vipItems,
    fetchVipItems,
    buyVipProduct,
  }
})

