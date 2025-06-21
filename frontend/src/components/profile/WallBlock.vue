<template>
  <div class="wall-block">
    <div class="wall-header">
  <div class="wall-title">
    <h2 class="section-title"> Стена записей</h2>
  </div>


</div>



    <div class="wall-content">
      <ul class="wall-posts">
        <li v-if="!wallPosts.length" class="wall-empty">Записей пока нет. Будь первым!</li>

        <li v-for="post in wallPosts" :key="post.id" class="wall-post">
          <div class="text">
  <router-link
    v-if="post.author"
    class="author-link"
    :to="`/user/${post.author.id}`"
  >
    @{{ post.author.username }}
  </router-link>
  <br />
  {{ post.text }}
</div>

          <div class="meta">
            <time>{{ formatDate(post.created_at) }}</time>
            <div class="actions">
  <button @click="toggleLike(post)" :class="{ liked: post.liked_by_me }">
    ❤ {{ post.likes }}
  </button>
  <button @click="toggleComments(post)">💬 {{ post.comments?.length ?? 0 }}</button>
  <button
    v-if="post.author?.id === profileStore.profile?.id"
    @click="handleDelete(post)"
    title="Удалить пост"
  >❌</button>
</div>

          </div>

          <div v-if="post.showComments" class="wall-comments">
            <ul>
              <li v-for="c in post.comments" :key="c.id">
                {{ c.text }} <time>{{ formatDate(c.created_at) }}</time>
              </li>
            </ul>
            <div class="comment-new">
              <input v-model="post.newComment" @keyup.enter="addComment(post)" placeholder="Комментарий..." />
              <button @click="addComment(post)">✉</button>
            </div>
          </div>
        </li>
      </ul>
    </div>

    <div class="wall-new">
      <input v-model="newPost" placeholder="Напиши что-нибудь…" @keyup.enter="addPost" />
      <button @click="addPost"><i class="fa-solid fa-pen" /></button>
    </div>
  </div>
</template>

<script setup>
import { ref, onMounted, computed, watchEffect } from 'vue'
import { useWallStore } from '@/store/wall'
import { useToastStore } from '@/store/toast'
import { useProfileStore } from '@/store/profile'

const toast = useToastStore()
const wallStore = useWallStore()
const profileStore = useProfileStore()

const wallPosts = computed(() => wallStore.wallPosts)


const {

  fetchWallPosts,
  addWallPost,
  deleteWallPost, // 👈 вот это
  toggleLike,
  fetchComments,
  addCommentToPost
} = wallStore

const newPost = ref('')

async function addPost () {
  const text = newPost.value.trim()
  if (!text) return
  await addWallPost(text)
  toast.addToast('📌 Запись добавлена!', { type: 'success' })
  newPost.value = ''
}

async function handleDelete(post) {
  if (!confirm('Удалить эту запись?')) return
  await deleteWallPost(post.id)
  toast.addToast('🗑 Запись удалена', { type: 'success' })
}


async function toggleComments (post) {
  post.showComments = !post.showComments
  if (post.showComments && !post.commentsLoaded) {
    await fetchComments(post)
  }
}

async function addComment (post) {
  const text = (post.newComment || '').trim()
  if (!text) return
  await addCommentToPost(post.id, text)
  post.newComment = ''
}

function formatDate (iso) {
  return new Date(iso).toLocaleString('ru-RU', {
    dateStyle: 'short',
    timeStyle: 'short'
  })
}

watchEffect(() => {
  const userId = profileStore.profile?.id
  if (userId && wallStore.wallPosts.length === 0) {
    wallStore.fetchWallPosts(userId)
  }
})
</script>

<style scoped lang="scss">

.wall-block {
  max-width: 700px;
  height: 360px;
  background: rgba(38, 32, 39, 0.48);
  border: 1px solid #2e2c2c;
  border-radius: 8px;
  padding: 10px;
  font-size: 13px;
  font-family: 'JetBrains Mono', monospace;
  display: flex;
  flex-direction: column;
  gap: 10px;
  box-sizing: border-box;
  color: white;
}


.author-link {
  color: #aaa;
  font-weight: 500;
  text-decoration: none;
}
.author-link:hover {
  text-decoration: underline;
}




.wall-header {
  display: flex;
  flex-direction: column;
  align-items: center;
  gap: 6px;

  .wall-title {
    width: 100%;
    text-align: center;
  }

  .refresh-btn {
    align-self: flex-end;
    background: none;
    border: none;
    color: inherit;
    cursor: pointer;
    font-size: 14px;
  }
}

.section-title {
  position: relative;
  font-size: 16px;
  font-weight: 600;
  color: white;
  text-align: left;
  margin: 0;

  &::after {
    content: "";
    display: block;
    width: 100%;
    height: 1px;
    background-color: white;
    opacity: 0.3;
    margin: 6px auto 0;
    border-radius: 1px;
  }
}



.wall-content {
  max-height: 220px;
  overflow-y: auto;
}

.wall-posts {
  list-style: none;
  padding: 0;
  margin: 0;

  .wall-empty {
    text-align: center;
    opacity: 0.6;
    padding: 10px;
  }

  .wall-post {
    border: 1px solid rgba(255, 255, 255, 0.08);
    border-radius: 6px;
    padding: 6px 8px;
    margin-bottom: 8px;
    background: rgba(255, 255, 255, 0.02);

    .text {
      margin-bottom: auto;
      white-space: pre-wrap;
    }

    .meta {
      display: flex;
      justify-content: space-between;
      align-items: center;
      font-size: 11px;
      opacity: 0.8;

      .actions {
        display: flex;
        gap: 10px;

        button {
          background: none;
          border: none;
          color: inherit;
          font-size: 12px;
          cursor: pointer;

          &.liked {
            color: #ff6a6a;
          }
        }
      }
    }

    .wall-comments {
      margin-top: 6px;

      ul {
        padding: 0;
        margin: 0 0 6px;
        list-style: none;

        li {
          font-size: 12px;
          opacity: 0.85;
          padding: 2px 0;
          display: flex;
          justify-content: space-between;
        }
      }

      .comment-new {
        display: flex;
        gap: 6px;

        input {
          flex: 1;
          background: transparent;
          border: 1px solid rgba(255, 255, 255, 0.15);
          border-radius: 6px;
          padding: 4px 6px;
          color: inherit;
        }

        button {
          background: none;
          border: none;
          color: inherit;
          cursor: pointer;
        }
      }
    }
  }
}

.wall-new {
  display:flex;
  gap: 10px;

  input {
    flex: 1;
    background: linear-gradient(90deg, #1df0c615, #00585118);
    border: 1px solid rgba(255, 255, 255, 0.15);
    border-radius: 6px;
    padding: 6px 3px;
    color: inherit;
  }

  button {
    display:flex;
    max-width: 60px;
    background: none;
    border: none;
    color: inherit;
    cursor: pointer;
  }
}
</style>




  



  
  