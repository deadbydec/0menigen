<template>
  <div class="wall-block">
    <h3>Стена записей</h3>
    <ul>
      <li v-for="post in wallPosts" :key="post.id">
        <p>{{ post.text }}</p>
        <span>{{ post.created_at }}</span>
      </li>
    </ul>
    <input v-model="newPost" placeholder="Написать пост..." />
    <button class="addPost"><i class="fa-solid fa-pen"></i></button>
  </div>
</template>

<script setup>
import { ref, onMounted } from "vue";
import { useWallStore } from "@/store/wall";
const wallStore = useWallStore();
const { wallPosts, fetchWallPosts, addWallPost } = wallStore;
const newPost = ref("");

onMounted(fetchWallPosts);
const addPost = async () => {
  if (newPost.value.trim()) {
    await addWallPost(newPost.value);
    newPost.value = "";
  }
};
</script>
<style scoped>
.wall-block {
  height: 370px;
  border: 2px solid rgba(0, 0, 0, 0.692);
  max-height: 500px;
}

.addPost {
  position: sticky;
  top: 200px; /* Фиксируем кнопку на высоте 10px от верха */
  background:transparent;
  color: white;
  padding: 10px 12px;
  border: none;
  border-radius: 5px;
  cursor: pointer;
}


</style>

  



  
  