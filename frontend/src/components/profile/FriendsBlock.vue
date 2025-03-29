<template>
  <div class="friends-block">
    <h3>👥 Друзья</h3>
    <ul>
      <li v-for="friend in friends" :key="friend.id">
        <router-link :to="`/profile/${friend.id}`">
          <img :src="friend.avatar" alt="Avatar" class="avatar-small" />
          {{ friend.username }}
        </router-link>
      </li>
    </ul>
  </div>
</template>

<script setup>
import { useFriendsStore } from "@/store/friends";
const { friends } = useFriendsStore();
</script>

<style scoped>
.friends-block {
  max-width: 400px;
  border: 2px solid rgba(0, 0, 0, 0.692);
}

.addPost {
  position: sticky;
  top: 20px; /* Фиксируем кнопку на высоте 10px от верха */
  background:transparent;
  color: white;
  padding: 10px 12px;
  border: none;
  border-radius: 5px;
  cursor: pointer;
}


</style>

  