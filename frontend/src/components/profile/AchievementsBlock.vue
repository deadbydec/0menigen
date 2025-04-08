<template>
  <div class="achievements-block">
    <h3>Ачивки</h3>

    <div class="hex-grid">
      <div 
        v-for="(ach, index) in paddedAchievements" 
        :key="index" 
        class="hex-cell"
        :class="{ placeholder: !ach.unlocked }"
        @mouseover="hoveredAchievement = ach.unlocked ? ach : null"
        @mouseleave="hoveredAchievement = null"
      >
        <img v-if="ach.unlocked" :src="ach.icon" class="achievement-icon" />
        <div v-else class="placeholder-icon">🔒</div> <!-- Заглушка -->
      </div>
    </div>

    <!-- Всплывающее название ачивки -->
    <div v-if="hoveredAchievement" class="achievement-tooltip">
      <h4>{{ hoveredAchievement.title }}</h4>
      <span class="date">{{ formatDate(hoveredAchievement.date) }}</span>
    </div>

    <!-- Кнопка "Показать все" -->
    <button class="show-all-btn" @click="showAll = true">ПОКАЗАТЬ ВСЕ</button>

    <!-- Модалка с полным списком ачивок -->
    <AchievementModal v-if="showAll" :achievements="achievements" @close="showAll = false" />
  </div>
</template>

<script setup>
import { ref, computed, onMounted } from "vue";
import { useAchievementsStore } from "@/store/achievements";
import AchievementModal from "./AchievementModal.vue";

const achievementsStore = useAchievementsStore();
const hoveredAchievement = ref(null);
const showAll = ref(false);

onMounted(() => {
  achievementsStore.fetchAchievements(); // ✅ Загружаем ачивки при загрузке
});

const achievements = computed(() => achievementsStore.achievements);
const lastAchievements = computed(() => achievementsStore.achievements.slice(0, 7));

const formatDate = (date) => new Date(date).toLocaleDateString();

// 🔥 Заполняем недостающие ячейки заглушками
  const paddedAchievements = computed(() => {
  const actualAchievements = lastAchievements.value;
  const placeholdersNeeded = 9 - actualAchievements.length;
  const placeholders = Array.from({ length: placeholdersNeeded }, () => ({ unlocked: false }));
  return [...actualAchievements, ...placeholders];

});

</script>

<style scoped>
.achievements-block {
  background: white;
  border: 2px solid rgba(0, 0, 0, 0.692);
  border-radius: 10px;
  padding: 10px;
  text-align: center;
}

.hex-grid {
  display: grid;
  grid-template-columns: repeat(3, 1fr);
  gap: 5px;
  justify-content: center;
  align-items: center;
  padding: 10px;
}

.hex-cell {
  width: 60px;
  height: 60px;
  background: rgba(255, 255, 255, 0.459);
  border: 2px solid black;
  clip-path: polygon(50% 0%, 100% 25%, 100% 75%, 50% 100%, 0% 75%, 0% 25%);
  display: flex;
  align-items: center;
  justify-content: center;
  cursor: pointer;
  transition: transform 0.2s;
}

.hex-cell.placeholder {
  background: #646364d7;
  border-color: gray;
}

.placeholder-icon {
  font-size: 24px;
  color: gray;
}

.achievement-icon {
  width: 48px;
  height: 48px;
}

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

.show-all-btn {
  background: rgba(101, 17, 150, 0.863);
  color: white;
  padding: 8px 12px;
  font-weight: bold;
  border: none;
  cursor: pointer;
  margin-top: 10px;
}
</style>
