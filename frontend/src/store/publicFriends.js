import { defineStore } from 'pinia'
import { ref } from 'vue'
import api from '@/utils/axios'

export const usePublicFriendsStore = defineStore('publicFriends', () => {
  const publicFriends = ref([])

  /** Получить список друзей для публичного профиля */
  async function fetchPublicFriends(userId) {
    try {
      const res = await api.get(`/friends/public/${userId}`)
      publicFriends.value = res.data
    } catch (err) {
      console.error('❌ Ошибка загрузки друзей:', err)
      publicFriends.value = []
    }
  }

  /** Проверка статуса дружбы */
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

  /** Отправка запроса в друзья */
  async function sendRequest(friendId) {
    try {
      await api.post('/friends/add', { friend_id: friendId })
    } catch (err) {
      console.error('❌ Ошибка отправки запроса в друзья:', err)
    }
  }

  /** Удаление из друзей */
  async function removeFriend(friendId) {
    try {
      await api.post('/friends/remove', { friend_id: friendId })
    } catch (err) {
      console.error('❌ Ошибка удаления друга:', err)
    }
  }

  return {
    publicFriends,
    fetchPublicFriends,
    checkStatus,
    sendRequest,
    removeFriend,
  }
})
