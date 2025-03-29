import { defineStore } from "pinia";
import { ref } from "vue";
import axios from "@/utils/axios";

export const useWallStore = defineStore("wall", () => {
  const wallPosts = ref([]);

  // ✅ Загружаем посты
  async function fetchWallPosts() {
    try {
      const res = await axios.get("/wall", {
        headers: { Authorization: `Bearer ${localStorage.getItem("auth_token")}` },
      });
      wallPosts.value = res.data || [];
    } catch (err) {
      console.error("❌ Ошибка загрузки стены:", err);
    }
  }

  // ✅ Добавляем пост
  async function addWallPost(text) {
    try {
      const res = await axios.post(
        "/wall/add",
        { text },
        {
          headers: { Authorization: `Bearer ${localStorage.getItem("auth_token")}` },
        }
      );

      if (res.data.success) {
        fetchWallPosts(); // 🔥 Перезагружаем стену после нового поста
      }
    } catch (err) {
      console.error("❌ Ошибка добавления поста:", err);
    }
  }

  return {
    wallPosts,
    fetchWallPosts,
    addWallPost
  };
});
