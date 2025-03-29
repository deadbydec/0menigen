import { defineStore } from "pinia";
import { usePlayerStore } from "@/store/player";
import { ref, computed } from "vue";
import api from "@/utils/axios";

export const useProfileStore = defineStore("profile", () => {
  const playerStore = usePlayerStore();
  const profile = computed(() => playerStore.player); // ✅ Доступ к данным для шаблонов

  function getCookie(name) {
    const match = document.cookie.match(new RegExp("(^| )" + name + "=([^;]+)"));
    return match ? match[2] : null;
  }

  async function updateBio(newBio) {
    const csrfToken = getCookie("csrf_access_token");
  
    // ✅ Безопасно очищаем био от null/undefined
    const safeBio = typeof newBio === "string" ? newBio.trim() : "";
  
    // 🧼 Если пусто — не шлём вообще (можешь убрать это, если хочешь разрешить пустое био)
    if (!safeBio) {
      console.warn("📭 Пустое био не отправляется.");
      return;
    }
  
    try {
      const res = await api.post(
        "/profile/edit_bio",
        { bio: safeBio },
        {
          withCredentials: true,
          headers: {
            "X-CSRF-TOKEN": csrfToken,
          },
        }
      );
  
      if (res.data.success) {
        console.log("✅ Био обновлено:", res.data.bio);
        await playerStore.fetchPlayer(); // 💾 подтягиваем заново
      }
    } catch (err) {
      console.error("❌ Ошибка обновления био:", err);
    }
  }
  

  async function uploadAvatar(file) {
    if (!file) return;
  
    const formData = new FormData();
    formData.append("avatar", file);
  
    const csrfToken = getCookie("csrf_access_token");
  
    try {
      const res = await api.post("/profile/upload-avatar", formData, {
        withCredentials: true,
        headers: {
          "X-CSRF-TOKEN": csrfToken, // ⬅️ только этот, не трогаем Content-Type
        },
      });
  
      if (res.data.avatarUrl) {
        console.log("✅ Аватар обновлён:", res.data.avatarUrl);
        await playerStore.fetchPlayer(); // 💾 подтягиваем заново
      }
    } catch (err) {
      console.error("❌ Ошибка загрузки аватара:", err);
    }
  }

  return { profile, updateBio, uploadAvatar }; // ⬅️ ВОТ ЭТО ВАЖНО
});




