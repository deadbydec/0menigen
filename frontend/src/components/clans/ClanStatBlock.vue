<template>
  <div class="clan-stat-block stat-block">
    <h2>📊 Клановая статистика</h2>

    <ul>
      <li>Всего кланов: <strong>{{ stats.total_clans }}</strong></li>
      <li>Создано за неделю: <strong>{{ stats.new_this_week }}</strong></li>

      <li v-if="stats.top_by_level">
        🏆 Клан недели (по уровню): 
        <strong>{{ stats.top_by_level.name }}</strong> — {{ stats.top_by_level.level }} ур.
      </li>

      <li v-if="stats.top_by_xp_week">
        🔥 Лидер по опыту за неделю: 
        <strong>{{ stats.top_by_xp_week.name }}</strong>
      </li>

      <li v-if="stats.most_members">
        👥 Самый массовый клан: 
        <strong>{{ stats.most_members.name }}</strong> ({{ stats.most_members.member_count }} участников)
      </li>
    </ul>
  </div>
</template>

<script setup>
import { onMounted } from 'vue'
import { useClansStore } from "@/store/clans"
import { storeToRefs } from "pinia"

const clansStore = useClansStore()
const { clanStats } = storeToRefs(clansStore)
const stats = computed(() => clanStats.value || {})

onMounted(() => {
  clansStore.fetchClanStats()
})
</script>

<style scoped>

.clan-stat-block {
  background: rgba(255, 255, 255, 0.05);
  border: 1px solid #444;
  height: 150px;
  border-radius: 12px;
  text-align: left;
}

.stat-block ul {
  line-height: 1.4;
  list-style: none; /* Убирает точки */
}
</style>
