<template>
    <router-link :to="'/forum/' + thread.id" class="thread-card">
      <h3 class="thread-title">{{ thread.title }}</h3>
      <p class="thread-desc">{{ thread.description }}</p>
      <div class="thread-stats">
        👁 {{ thread.views }} | 💬 {{ thread.postsCount }}
      </div>
    </router-link>
  </template>
  
  <script setup>
  defineProps({
    thread: Object
  });
  </script>
  
  <style scoped>
  .thread-card {
    display: block;
    padding: 15px;
    border-radius: 10px;
    background: #1a1a1a;
    color: #fff;
    text-decoration: none;
    transition: 0.2s;
  }
  
  .thread-card:hover {
    background: #292929;
  }
  </style>
  