import { defineStore } from "pinia"
import { ref } from "vue"
import api from "@/utils/axios"

export const useQuestStore = defineStore("quests", () => {
  const npcs = ref([])                // все квестодатели
  const activeQuests = ref([])       // полученные квесты
  const currentQuest = ref(null)     // текущий открытый (детальный) квест

  // 🧠 Получить всех NPC
  async function fetchNPCs() {
    try {
      const res = await api.get("/npc-quests/list")
      npcs.value = res.data || []
    } catch (err) {
      console.error("❌ Ошибка загрузки NPC:", err)
    }
  }

  // 🔄 Получить свои текущие квесты (в пределах 24ч)
  async function fetchActiveQuests() {
    try {
      const res = await api.get("/npc-quests/my")
      activeQuests.value = res.data || []
    } catch (err) {
      console.error("❌ Ошибка загрузки активных квестов:", err)
    }
  }

  // 📥 Принять квест у конкретного NPC
  async function acceptQuest(npcId) {
    try {
      const res = await api.post(`/npc-quests/accept`, null, {
        params: { npc_id: npcId },
      })
      await fetchActiveQuests()
      return res.data
    } catch (err) {
      console.error("❌ Ошибка принятия квеста:", err)
      throw err
    }
  }

  // 📤 Сдать квест
  async function turnInQuest(questId) {
    try {
      const res = await api.post("/npc-quests/turn-in", {
        quest_id: questId,
      })
      await fetchActiveQuests()
      return res.data
    } catch (err) {
      console.error("❌ Ошибка сдачи квеста:", err)
      throw err
    }
  }

  // 📎 Для открытия NPC карточки
  function setCurrentQuest(quest) {
    currentQuest.value = quest
  }

  return {
    npcs,
    activeQuests,
    currentQuest,
    fetchNPCs,
    fetchActiveQuests,
    acceptQuest,
    turnInQuest,
    setCurrentQuest,
  }
})
