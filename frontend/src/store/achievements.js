import { defineStore } from "pinia";
import axios from "@/utils/axios";

export const useAchievementsStore = defineStore("achievements", {
  state: () => ({
    achievements: [],
  }),

  actions: {
    // ✅ Загружаем ачивки юзера
    async fetchAchievements() {
      try {
        const token = localStorage.getItem("auth_token");
        const res = await axios.get("/achievements", {
          headers: { Authorization: `Bearer ${token}` },
        });

        this.achievements = res.data; // ✅ Сохраняем в store
      } catch (err) {
        console.error("❌ Ошибка загрузки ачивок:", err);
      }
    },

    // ✅ Разблокируем ачивку
    async unlockAchievement(achievement_id) {
      try {
        const res = await axios.post(
          "api/achievements/unlock",
          { achievement_id },
          {
            headers: { Authorization: `Bearer ${localStorage.getItem("auth_token")}` },
          }
        );

        if (res.data.success) {
          await this.fetchAchievements(); // 🔥 Перезагружаем список после получения
        }
      } catch (err) {
        console.error("❌ Ошибка выдачи ачивки:", err);
      }
    },
  },
});

