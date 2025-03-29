<template>
    <div v-if="thread">
      <h1>{{ thread.title }}</h1>
      <p>{{ thread.description }}</p>
  
      <div v-for="post in thread.posts" :key="post.id">
        <div class="post">
          <strong>{{ post.author }}</strong>: {{ post.content }}
        </div>
      </div>
    </div>
    <div v-else>
      <p>Загрузка...</p>
    </div>
  </template>
  
  <script setup>
  import { onMounted, ref } from 'vue';
  import { useRoute } from 'vue-router';
  import axios from 'axios';
  
  const route = useRoute();
  const thread = ref(null);
  
  onMounted(async () => {
    try {
      const response = await axios.get(`/api/forum/thread/${route.params.thread_id}`);
      thread.value = response.data;
    } catch (error) {
      console.error('Ошибка загрузки темы:', error);
    }
  });
  </script>
  