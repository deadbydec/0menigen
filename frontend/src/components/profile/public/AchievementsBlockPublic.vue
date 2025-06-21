<template>
  <div class="achievements-block">
    <h2>Достижения</h2>

    <div class="achievements-placeholder">
  <p class="placeholder-text">⚙ Раздел с достижениями появится в одном из следующих обновлений. Пока просто представь, что ты — победитель.</p>
</div>


    <!-- Всплывающее название ачивки -->
    <div v-if="hoveredAchievement" class="achievement-tooltip">
      <h4>{{ hoveredAchievement.title }}</h4>
      <span class="date">{{ formatDate(hoveredAchievement.date) }}</span>
    </div>



    <!-- Модалка с полным списком ачивок -->
    <AchievementModal v-if="showAll" :achievements="achievements" @close="showAll = false" />
  </div>
</template>

<script setup>
import { ref, computed, onMounted } from "vue";
import { useAchievementsStore } from "@/store/achievements";

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
  gap: 10px;
  height: 190px;
  max-width: 588px;
  backdrop-filter: blur(7px);
  background: rgba(38, 32, 39, 0.48);
  border: 1px solid #2e2c2c;
  border-radius: 8px;
  padding: 10px;
  font-size: 13px;
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
  background:linear-gradient(80deg, #2925278c,rgba(78, 158, 153, 0.637));
  

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
  background:linear-gradient(80deg, #292527be,rgba(78, 158, 153, 0.95));
  color: white;
  padding: 8px 12px;
  font-weight: bold;

  cursor: pointer;
  margin-top: 10px;
  border: 1px solid #2e2c2c;
}

.achievements-block h2 {
  position: relative;
  font-size: 18px;
  text-align: left;
  color: white;
  margin-bottom: 8px;
}

.achievements-block h2::after {
  content: "";
  display: block;
  width: 100%;
  height: 1px;
  background-color: white;
  opacity: 0.4; /* 👈 мягкий, неяркий акцент */
  margin: 6px auto 0;
  border-radius: 1px;
}

.achievements-placeholder {
  background: rgba(255, 255, 255, 0.05);
  border: 1px dashed rgba(255, 255, 255, 0.3);
  border-radius: 8px;
  padding: 20px;
  text-align: center;
  color: rgba(255, 255, 255, 0.7);
  font-style: italic;
  font-size: 13px;
  margin-top: 10px;
}

.placeholder-text {
  margin: 0;
  line-height: 1.4;
}

</style>
