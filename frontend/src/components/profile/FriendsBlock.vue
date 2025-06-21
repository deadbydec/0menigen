<template>
  <div class="friends-block">
    <h2>Друзья</h2>
    <ul v-if="Array.isArray(friends) && friends.length > 0" class="friend-list">
      <li v-for="friend in friends" :key="friend.id" class="friend-item">
        <router-link :to="`/profile/${friend.id}`" class="friend-link">
          <img :src="getFullAvatar(friend.avatar)" alt="Avatar" class="avatar-small" />
          <span class="username">{{ friend.username }}</span>
        </router-link>
      </li>
    </ul>
    <p v-else>У вас пока нет друзей</p>
  </div>
</template>

<script setup>
import { useFriendsStore } from "@/store/friends"
import { usePlayerStore } from "@/store/player"
import { onMounted, watch, computed } from "vue"

const friendsStore = useFriendsStore()
const playerStore = usePlayerStore()
const userId = computed(() => playerStore.player?.id)

const friends = computed(() => friendsStore.friends)


function getFullAvatar(avatar) {
  return avatar?.startsWith("http") ? avatar : `https://localhost:5002${avatar}`
}

async function loadFriends() {
  if (!userId.value) return
  await friendsStore.fetchList()
}

onMounted(async () => {
  if (!playerStore.player) {
    await playerStore.fetchPlayer()
  }
  await loadFriends()
})

watch(userId, async (newId, oldId) => {
  if (newId && newId !== oldId) {
    await loadFriends()
  }
})
</script>




<style scoped>
.friends-block {
    max-width: 300px;
    border: 2px solid rgba(0, 0, 0, 0.692);
    height: 350px;

}

h2 {
  margin: 0 0 12px;
  font-size: 20px;
  color: white;
}

.friend-list {
  list-style: none;
  list-style-type: none; /* <- ЯВНО */
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

.friends-block h2 {
  position: relative;
  font-size: 18px;
  text-align: left;
  color: white;
  margin-bottom: 8px;
}

.friends-block h2::after {
  content: "";
  display: block;
  width: 100%;
  height: 1px;
  background-color: white;
  opacity: 0.4; /* 👈 мягкий, неяркий акцент */
  margin: 6px auto 0;
  border-radius: 1px;
}

</style>


  