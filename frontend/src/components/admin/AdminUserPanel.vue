<template>
    <div class="admin-panel p-4">
      <h1 class="text-2xl font-bold mb-4">Админка: Пользователи</h1>
  
      <input v-model="query" @keyup.enter="searchUsers" placeholder="Поиск по нику..." class="p-2 border rounded w-full mb-4" />
  
      <table class="w-full table-auto border border-gray-400">
        <thead>
          <tr class="bg-gray-100">
            <th class="border px-2 py-1">ID</th>
            <th class="border px-2 py-1">Ник</th>
            <th class="border px-2 py-1">Тип</th>
            <th class="border px-2 py-1">Email</th>
            <th class="border px-2 py-1">Действия</th>
          </tr>
        </thead>
        <tbody>
          <tr v-for="user in users" :key="user.id">
            <td class="border px-2 py-1">{{ user.id }}</td>
            <td class="border px-2 py-1">{{ user.username }}</td>
            <td class="border px-2 py-1">{{ user.usertype }}</td>
            <td class="border px-2 py-1">{{ user.email }}</td>
            <td class="border px-2 py-1">
              <button @click="deleteUser(user.id)" class="bg-red-500 text-white px-2 py-1 rounded hover:bg-red-600">
                Удалить
              </button>
            </td>
          </tr>
        </tbody>
      </table>
    </div>
  </template>
  
  <script setup>
  import { ref } from 'vue'
  import api from '@/utils/axios'
  
  const query = ref('')
  const users = ref([])
  
  async function searchUsers() {
    if (!query.value.trim()) return
    try {
      const res = await api.get(`/admin/find-users?q=${query.value}`)
      users.value = res.data
    } catch (err) {
      console.error('Ошибка при поиске:', err)
    }
  }
  
  async function deleteUser(userId) {
    if (!confirm(`Удалить пользователя с ID ${userId}?`)) return
    try {
      await api.delete(`/admin/user/${userId}`)
      users.value = users.value.filter(u => u.id !== userId)
    } catch (err) {
      console.error('Ошибка при удалении:', err)
    }
  }
  </script>
  
  <style scoped>
  .admin-panel {
    max-width: 800px;
    margin: 0 auto;
  }
  </style>
  