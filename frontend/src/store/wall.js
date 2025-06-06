import { defineStore } from 'pinia'
import { ref } from 'vue'
import axios from '@/utils/axios'

export const useWallStore = defineStore('wall', () => {
  const wallPosts = ref([])
  const targetUserId = ref(null) // 🧠 сохраняем id между вызовами

  // 🔄 Загрузка всех постов
  async function fetchWallPosts(userId) {
    try {
      if (userId) targetUserId.value = userId
      const uid = targetUserId.value
      if (!uid) {
        console.warn('⚠ Нет userId для загрузки стены')
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
      console.error('❌ Ошибка загрузки стены:', err)
    }
  }

  // ➕ Добавление нового поста
  async function addWallPost(text) {
    try {
      const { data } = await axios.post('/wall/add', { text })

      if (data && data.id) {
        wallPosts.value.unshift({
          ...data,
          showComments: false,
          commentsLoaded: false,
          comments: [],
          newComment: ''
        })
      }
    } catch (err) {
      console.error('❌ Ошибка добавления поста:', err)
    }
  }

  // ❤️ Лайк / дизлайк
  async function toggleLike(post) {
    try {
      const { data } = await axios.post(`/wall/${post.id}/like`)
      post.likes = data.likes
      post.liked_by_me = data.liked_by_me
    } catch (err) {
      console.error('❌ Ошибка при лайке:', err)
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

  return {
    wallPosts,
    targetUserId,
    fetchWallPosts,
    addWallPost,
    toggleLike,
    fetchComments,
    addCommentToPost
  }
})


