import { defineStore } from "pinia";
import { ref } from "vue";
import api from "@/utils/axios";

export const useFriendsStore = defineStore("friends", () => {
  const friends = ref([]);
  const requests = ref([]);
  const activeTab = ref("friends");

  // ✅ Загружаем список друзей
  async function fetchFriends() {
    try {
      const res = await api.get("friends", {
        headers: { Authorization: `Bearer ${localStorage.getItem("auth_token")}` },
      });
      friends.value = res.data || [];
    } catch (err) {
      console.error("❌ Ошибка загрузки друзей:", err);
    }
  }

  // ✅ Загружаем входящие заявки в друзья
  async function fetchRequests() {
    try {
      const res = await api.get("friends/requests", {
        headers: { Authorization: `Bearer ${localStorage.getItem("auth_token")}` },
      });
      requests.value = res.data || [];
    } catch (err) {
      console.error("❌ Ошибка загрузки заявок:", err);
      requests.value = [];
    }
  }

  // ✅ Принять заявку в друзья
  async function acceptRequest(requestId) {
    try {
      await api.post(
        "friends/accept",
        { request_id: requestId },
        {
          headers: { Authorization: `Bearer ${localStorage.getItem("auth_token")}` },
        }
      );
      fetchFriends();
      fetchRequests();
    } catch (err) {
      console.error("❌ Ошибка принятия заявки:", err);
    }
  }

  // ✅ Отклонить заявку
  async function rejectRequest(requestId) {
    try {
      await api.post(
        "friends/reject",
        { request_id: requestId },
        {
          headers: { Authorization: `Bearer ${localStorage.getItem("auth_token")}` },
        }
      );
      fetchRequests();
    } catch (err) {
      console.error("❌ Ошибка отклонения заявки:", err);
    }
  }

  return {
    friends,
    requests,
    activeTab,
    fetchFriends,
    fetchRequests,
    acceptRequest,
    rejectRequest,
  };
});
