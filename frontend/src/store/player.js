import { defineStore } from "pinia";
import { ref, computed } from "vue";
import api from "@/utils/axios"; // ✅ Используем уже настроенный axios с куками!

export const usePlayerStore = defineStore("player", () => {
  const player = ref(null);

  const xpPercent = computed(() =>
    player.value ? (player.value.xp / player.value.nextLevelXp) * 100 : 0
  );

  async function fetchPlayer() {
    console.log("🔄 [DEBUG] Запрашиваем данные игрока...");

    try {
      const response = await api.get("/player/"); // ✅ Запрос без `Authorization`
      console.log("✅ [DEBUG] API Ответ:", response.data);
      player.value = { ...response.data };
    } catch (error) {
      console.error("❌ Ошибка загрузки игрока:", error);
      player.value = null; // ✅ Если ошибка, сбрасываем данные
    }
  }

  return { player, xpPercent, fetchPlayer };
});


