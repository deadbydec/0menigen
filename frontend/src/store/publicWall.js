import { defineStore } from 'pinia'
import { ref } from 'vue'
import axios from '@/utils/axios'

export const usePublicWallStore = defineStore('publicWall', () => {
  const wallPosts = ref([])
  const targetUserId = ref(null)

  // 🔄 Загрузка стены чужого пользователя
  async function fetchWallPosts(userId) {
    try {
      if (userId) targetUserId.value = userId
      const uid = targetUserId.value
      if (!uid) {
        console.warn('⚠ Нет userId для загрузки публичной стены')
        return
      }

      const { data } = await axios.get('/wall/', {
        params: { target_user_id: uid }
      })

      wallPosts.value = (data || []).map(p => ({
        ...p,
        showComments: false,
        commentsLoaded: false,
        comments: [],
        newComment: ''
      }))
    } catch (err) {
      console.error('❌ Ошибка загрузки публичной стены:', err)
    }
  }

  // 💬 Загрузка комментариев
  async function fetchComments(post) {
    try {
      const { data } = await axios.get(`/wall/${post.id}/comments`)
      post.comments = data || []
      post.commentsLoaded = true
    } catch (err) {
      console.error('❌ Ошибка загрузки комментариев:', err)
    }
  }

  // ✏ Добавление комментария
  async function addCommentToPost(postId, text) {
    try {
      const { data } = await axios.post(`/wall/${postId}/comment`, { text })
      const post = wallPosts.value.find(p => p.id === postId)
      if (post) post.comments.unshift(data)
    } catch (err) {
      console.error('❌ Ошибка добавления комментария:', err)
    }
  }

  // ❤️ Лайк / дизлайк
  async function toggleLike(post) {
    try {
      const { data } = await axios.post(`/wall/${post.id}/like`)
      post.likes = data.likes
      post.liked_by_me = data.liked_by_me
    } catch (err) {
      console.error('❌ Ошибка при лайке на чужой стене:', err)
    }
  }

  function clearWall() {
  wallPosts.value = []
}


  return {
    clearWall,
    wallPosts,
    targetUserId,
    fetchWallPosts,
    fetchComments,
    addCommentToPost,
    toggleLike
  }
})
