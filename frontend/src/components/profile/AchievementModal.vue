<template>
  <div class="modal">
    <div class="modal-content">
      <!-- 🔥 Кнопка закрытия -->
      <button class="close-btn" @click="$emit('close')">✖</button>
      <h3>🏆 Все ачивки</h3>

      <!-- Вкладки -->
      <div class="tabs">
        <button :class="{ active: activeTab === 'unlocked' }" @click="activeTab = 'unlocked'">
          ✅ Полученные
        </button>
        <button :class="{ active: activeTab === 'locked' }" @click="activeTab = 'locked'">
          ❌ Неполученные
        </button>
      </div>

      <!-- Сетка ачивок в виде сот -->
      <div class="hex-grid">
        <div 
          v-for="(ach, index) in paddedAchievements" 
          :key="index" 
          class="hex-cell"
          :class="{ locked: !ach.unlocked }"
          @mouseover="hoveredAchievement = ach.unlocked ? ach : null"
          @mouseleave="hoveredAchievement = null"
        >
          <img v-if="ach.unlocked" :src="ach.icon" class="achievement-icon" />
          <div v-else class="locked-icon">🔒</div>
        </div>
      </div>

      <!-- Всплывающее описание -->
      <div v-if="hoveredAchievement" class="achievement-tooltip">
        <h4>{{ hoveredAchievement.title }}</h4>
        <p>{{ hoveredAchievement.description }}</p>
        <span v-if="hoveredAchievement.unlocked" class="date">
          Получено: {{ formatDate(hoveredAchievement.date) }}
        </span>
      </div>
    </div>
  </div>
</template>

<script setup>
import { ref, computed } from "vue";
import { useAchievementsStore } from "@/store/achievements";

const achievementsStore = useAchievementsStore();
const hoveredAchievement = ref(null);
const activeTab = ref("unlocked");

const filteredAchievements = computed(() =>
  achievementsStore.achievements.filter((ach) =>
    activeTab.value === "unlocked" ? ach.unlocked : !ach.unlocked
  )
);

// 🔥 Если вкладка "Неполученные" пуста, заполняем заглушками
const paddedAchievements = computed(() => {
  const actualAchievements = filteredAchievements.value;
  const placeholdersNeeded = Math.max(24
   - actualAchievements.length, 0); // Фиксированное количество (20)
  const placeholders = Array.from({ length: placeholdersNeeded }, () => ({ unlocked: false }));
  return [...actualAchievements, ...placeholders];
});

const formatDate = (date) => new Date(date).toLocaleDateString();
</script>

<style scoped>
/* 🎨 Основное окно */
.modal {
  position: fixed;
  top: 0;
  left: 0;
  width: 100%;
  height: 100%;
  background: rgba(0, 0, 0, 0.7);
  display: flex;
  align-items: center;
  justify-content: center;
}

.modal-content {
  background: white;
  padding: 20px;
  border-radius: 8px;
  width: 450px;
  position: relative;
  text-align: center;
}

/* ❌ Кнопка закрытия */
.close-btn {
  position: absolute;
  color: black;
  top: 10px;
  right: 10px;
  background: none;
  border: none;
  font-size: 20px;
  cursor: pointer;
}

/* Вкладки */
.tabs {
  display: flex;
  justify-content: center;
  gap: 10px;
  margin-bottom: 10px;
}

.tabs button {
  padding: 8px;
  cursor: pointer;
  border: none;
  border-radius: 5px;
  font-size: 14px;
}

.tabs .active {
  background: black;
  color: white;
}

/* 📌 Сетка сот */
.hex-grid {
  display: grid;
  grid-template-columns: repeat(auto-fill, minmax(60px, 1fr));
  gap: 5px;
  justify-content: center;
  align-items: center;
  padding: 10px;
}

/* 🔳 Соты */
.hex-cell {
  width: 60px;
  height: 60px;
  background: white;
  border: 2px solid black;
  clip-path: polygon(50% 0%, 100% 25%, 100% 75%, 50% 100%, 0% 75%, 0% 25%);
  display: flex;
  align-items: center;
  justify-content: center;
  cursor: pointer;
  transition: transform 0.2s;
}

/* 🕵️‍♂️ Заблокированные ачивки */
.hex-cell.locked {
  background: #ddd;
  border-color: gray;
}

.locked-icon {
  font-size: 24px;
  color: gray;
}

/* 🏅 Иконки ачивок */
.achievement-icon {
  width: 48px;
  height: 48px;
}

/* 📌 Всплывающее описание */
.achievement-tooltip {
  position: absolute;
  background: black;
  color: white;
  padding: 5px;
  border-radius: 5px;
  font-size: 14px;
  width: 120px;
  text-align: center;
}

.date {
  font-size: 12px;
  color: gray;
}
</style>
