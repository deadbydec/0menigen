// stores/friends.js
import { defineStore } from "pinia"
import { ref } from "vue"
import api from "@/utils/axios"

export const useFriendsStore = defineStore("friends", () => {
  const friends = ref([])
  const requests = ref([])
  const activeTab = ref("friends")

  // 🔄 Получить список друзей
  async function fetchList() {
  try {
    const res = await api.get("/friends/list", { withCredentials: true })
    friends.value = res.data || []
  } catch (err) {
    console.error("❌ Ошибка загрузки друзей:", err)
  }
}


  // 🔄 Получить входящие заявки
  async function fetchRequests() {
    try {
      const res = await api.get("/friends/requests", { withCredentials: true })
      requests.value = res.data || []
    } catch (err) {
      console.error("❌ Ошибка загрузки заявок:", err)
      requests.value = []
    }
  }

  // ✅ Принять заявку
  async function acceptRequest(requestId) {
    try {
      await api.post("/friends/accept", { request_id: requestId }, { withCredentials: true })
      await fetchList()
      await fetchRequests()
    } catch (err) {
      console.error("❌ Ошибка принятия заявки:", err)
    }
  }

  // ❌ Отклонить заявку
  async function rejectRequest(requestId) {
    try {
      await api.post("/friends/reject", { request_id: requestId }, { withCredentials: true })
      await fetchRequests()
    } catch (err) {
      console.error("❌ Ошибка отклонения заявки:", err)
    }
  }

  // ➕ Отправить запрос в друзья
  async function sendRequest(friendId) {
    try {
      await api.post("/friends/add", { friend_id: friendId }, { withCredentials: true })
    } catch (err) {
      console.error("❌ Ошибка отправки запроса:", err)
    }
  }

  // ❎ Удалить друга
  async function removeFriend(friendId) {
    try {
      await api.post("/friends/remove", { friend_id: friendId }, { withCredentials: true })
      await fetchList()
    } catch (err) {
      console.error("❌ Ошибка удаления друга:", err)
    }
  }

  // 📍 Проверить статус между пользователями
  async function checkStatus(friendId) {
    try {
      const res = await api.get("/friends/status", {
        params: { friend_id: friendId },
        withCredentials: true,
      })
      return res.data.status // 'none' | 'pending' | 'accepted'
    } catch (err) {
      console.error("❌ Ошибка проверки статуса:", err)
      return "none"
    }
  }

  // ✅ Получить друзей другого юзера
async function fetchPublicFriends(userId) {
  try {
    const res = await api.get(`/friends/public/${userId}`)
    friends.value = res.data || []
  } catch (err) {
    console.error("❌ Ошибка загрузки публичных друзей:", err)
    friends.value = []
  }
}

function resetFriends() {
  friends.value = []
  requests.value = []
}



  return {
    friends,
    resetFriends,
    requests,
    activeTab,
    fetchRequests,
    acceptRequest,
    rejectRequest,
    sendRequest,
    removeFriend,
    checkStatus,
    fetchList,
    fetchPublicFriends
  }
})

