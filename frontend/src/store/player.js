import { defineStore } from "pinia";
import { ref, computed } from "vue";
import api from "@/utils/axios"; // ✅ Используем уже настроенный axios с куками!
import { useToastStore } from "@/store/toast";

export const usePlayerStore = defineStore("player", () => {
  const player = ref(null);
  const toastStore = useToastStore(); // ⬅️ Вынесем сюда
  const xpPercent = computed(() =>
    player.value ? (player.value.xp / player.value.nextLevelXp) * 100 : 0
  );

  async function fetchPlayer() {
    console.log("🔄 [DEBUG] Запрашиваем данные игрока...");
  
    try {
      const response = await api.get("/player/");
      console.log("✅ [DEBUG] API Ответ:", response.data);
      player.value = { ...response.data };

      if (response.data.random_event) {
        const ev = response.data.random_event;
        const msg = `🌀 ${ev.title}\n\n${ev.description}`;
        toastStore.addToast(msg, { type: "info", duration: 6000 });
      }
    } catch (error) {
      console.error("❌ Ошибка загрузки игрока:", error);
      player.value = null;
    }
  }

  function resetPlayer() {
  player.value = null;
}


  return { player, xpPercent, fetchPlayer, resetPlayer };
});



