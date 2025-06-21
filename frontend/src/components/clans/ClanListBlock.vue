<template>
  <div class="clan-list-block clan-block">
    <h2>Поиск кланов</h2>

    <!-- 🔍 Поле поиска -->
    <input
      v-model="searchQuery"
      type="text"
      placeholder="🔎 Поиск клана по названию..."
      class="search-input"
    />

    <!-- 📊 Сортировка (можно расширить) -->
    <div class="sort-controls">
      <label>
        <input type="radio" value="level" v-model="sortBy" />
        По уровню
      </label>
      <label>
        <input type="radio" value="newest" v-model="sortBy" />
        Новые
      </label>
    </div>

    <!-- 🧱 Список кланов -->
    <div class="clan-list">
      <div
        v-for="clan in filteredClans"
        :key="clan.id"
        class="clan-entry"
      >
        <img :src="getAvatar(clan.avatar_url)" class="clan-avatar" />
        <div class="clan-info">
          <h3>{{ clan.name }}</h3>
          <p>{{ clan.description || "Без описания" }}</p>
          <div class="meta">
            🧬 Уровень: {{ clan.level }} | ✨ XP: {{ clan.xp }}
          </div>
        </div>
      </div>
    </div>
  </div>
</template>

<script setup>
import { onMounted } from "vue"
import { useClansStore } from "@/store/clans"

const clansStore = useClansStore()

onMounted(() => {
  clansStore.fetchClans()
})
</script>

<style scoped>
.clan-list-block {
  display: flex;
  flex-direction: column;
  gap: 12px;
  width: 550px;
  height: 650px;
  border: 1px solid rgb(36, 35, 37);
}

.search-input {
  align-items: center;
  position: relative;
  width: 450px;
  padding: 10px;
  border-radius: 8px;
  border: white;
  background: rgba(255, 255, 255, 0.1);
  color: #fff;
  font-family: inherit;
}

.sort-controls {
  display: flex;
  gap: 20px;
  font-size: 14px;
  color: #ccc;
}

.clan-list {
  display: flex;
  flex-direction: column;
  gap: 14px;
}

.clan-entry {
  display: flex;
  gap: 12px;
  background: rgba(255, 255, 255, 0.03);
  border-radius: 8px;
  padding: 12px;
  align-items: center;
}

.clan-avatar {
  width: 64px;
  height: 64px;
  object-fit: cover;
  border-radius: 50%;
  background: #111;
  border: 2px solid #444;
}

.clan-info {
  flex-grow: 1;
}

.meta {
  font-size: 13px;
  color: #999;
}
</style>
