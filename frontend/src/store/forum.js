import { defineStore } from "pinia";
import { ref } from "vue";
import api from "@/utils/axios";

export const useForumStore = defineStore("forum", () => {
  const threads = ref([]);
  const mainTopics = ref([]);
  const popularThreads = ref([]);
  const forumStats = ref({});
  const activeUsers = ref([]);

  async function fetchThreads() {
    try {
      const res = await api.get("forum/threads");
      threads.value = res.data;
      mainTopics.value = threads.value.filter(t => t.is_main);
      popularThreads.value = threads.value.sort((a, b) => b.views - a.views).slice(0, 5);
    } catch (err) {
      console.error("Ошибка загрузки тем:", err);
    }
  }

  async function fetchStats() {
    try {
      const res = await api.get("forum/stats");
      forumStats.value = res.data;
      activeUsers.value = res.data.activeUsers;
    } catch (err) {
      console.error("Ошибка загрузки статистики:", err);
    }
  }

  return { threads, mainTopics, popularThreads, forumStats, activeUsers, fetchThreads, fetchStats };
});
