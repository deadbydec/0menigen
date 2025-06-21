<template>
  <div class="friends-block">
    <h3>👥 Друзья</h3>

    <ul v-if="publicFriendsStore.publicFriends.length > 0" class="friend-list">
      <li v-for="friend in publicFriendsStore.publicFriends" :key="friend.id" class="friend-item">
        <router-link :to="`/profile/${friend.id}`" class="friend-link">
          <img :src="getFullAvatar(friend.avatar || friend.avatar_url)" alt="Avatar" class="avatar-small" />
          <span class="username">{{ friend.username }}</span>
        </router-link>
      </li>
    </ul>

    <p v-else class="no-friends">У этого игрока пока нет друзей.</p>
  </div>
</template>

<script setup>
import { onMounted, watch } from 'vue'
import { usePublicFriendsStore } from '@/store/publicFriends'

const props = defineProps({
  userId: {
    type: Number,
    required: true
  }
})

const publicFriendsStore = usePublicFriendsStore()

function getFullAvatar(avatar) {
  return avatar?.startsWith("http") ? avatar : `https://localhost:5002${avatar}`
}

async function load(userId) {
  if (userId) await publicFriendsStore.fetchPublicFriends(userId)
}

onMounted(() => {
  load(props.userId)
})

watch(() => props.userId, (newId) => {
  load(newId)
})
</script>

<style scoped>
.friends-block {
  max-width: 400px;
  height: 350px;
  overflow-y: auto;
  border: 2px solid rgba(0, 0, 0, 0.692);
  padding: 10px;
  box-sizing: border-box;
}

h3 {
  margin: 0 0 12px;
  font-size: 20px;
  color: white;
}

.friend-list {
  list-style: none;
  margin: 0;
  padding: 0;
}

.friend-item {
  margin-bottom: 12px;
}

.friend-link {
  display: flex;
  align-items: center;
  text-decoration: none;
  color: white;
}

.avatar-small {
  width: 60px;
  height: 60px;
  border-radius: 50%;
  object-fit: cover;
  border: 2px solid #aaa;
  margin-right: 14px;
}


.username {
  font-size: 16px;
  font-weight: 600;
}

.no-friends {
  color: white;
  font-size: 14px;
}
</style>



  