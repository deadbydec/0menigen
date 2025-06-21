<template>
  <div class="clans-wrapper">
    <div class="clans-container">
      <!-- ✅ Левая колонка с те -->
      <div class="left-column">
        <MyBlock />
        <TestBlock />
        <ClanStatBlock />
      </div>

      <!-- ✅ правая колонка со списком и поиском кланов с полем и фильтрм (релевант/новые) -->
      <div class="center-column">
        <ClanListBlock />
      </div>
    </div>
  </div>
</template>


<script setup>

import MyBlock from "@/components/clans/MyBlock.vue";
import TestBlock from "@/components/clans/TestBlock.vue";
import ClanListBlock from "@/components/clans/ClanListBlock.vue";
import ClanStatBlock from "@/components/clans/ClanStatBlock.vue";

</script>

<style scoped>
.clans-wrapper {
  display:flex;
  justify-content: center;
  height: 1000px;
  width: 1200px;
  padding-top:150px;
  box-sizing: border-box;

}

.clans-container {
  width: auto;
  max-width: 1400px; /* 💥 Твоя желаемая ширина */
  display: grid;
  grid-template-columns: 3fr 3fr 0fr;
  gap: 10px;
  /*background: rgba(255, 0, 0, 0.1);*/
}


/* Левая колонка */
.left-column {
  display: flex;
  flex-direction: column;
  gap: 10px;
  
}

.center-column {
  display: flex;
  flex-direction: column;
  gap: 10px;
}

/* Правая колонка */
.right-column {
  display: flex;
  flex-direction: column;
  gap: 10px;
}

/* Блоки */
.clan-list-block, .my-block, .test-block, .clan-stat-block {
  background: #181818e7;
  padding: 16px;
  border-radius: 18px;
  font-family: 'JetBrains Mono', monospace;
  border: 1px solid rgb(187, 187, 187);
  margin-right: 2px;
}
</style>