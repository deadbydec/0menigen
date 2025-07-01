import { defineStore } from "pinia"
import { ref, computed } from "vue"
import api from "@/utils/axios"
import { useToastStore } from "@/store/toast"

export const usePlayerStore = defineStore("player", () => {
  const player = ref(null)
  const toastStore = useToastStore()

  const xpPercent = computed(() =>
    player.value ? (player.value.xp / player.value.nextLevelXp) * 100 : 0
  )

  async function fetchPlayer() {
    try {
      const res = await api.get("/player/")
      player.value = res.data

      if (res.data.random_event) {
        const ev = res.data.random_event
        const msg = `🌀 ${ev.title}\n\n${ev.description}`
        toastStore.addToast(msg, { type: "info", duration: 6000 })
      }
    } catch (err) {
      console.error("❌ Ошибка загрузки игрока:", err)
      player.value = null
    }
  }

  // 🧃 тихий запрос баланса и состояния игрока (без тостов и ивентов)
  async function fetchMe() {
    try {
      const res = await api.get("/player/")
      player.value = res.data
    } catch (err) {
      console.error("❌ Ошибка тихого обновления игрока:", err)
    }
  }

  function resetPlayer() {
    player.value = null
  }

  return {
    player,
    xpPercent,
    fetchPlayer,
    fetchMe,     // 💥 вот сюда экспортируем
    resetPlayer,
  }
})








