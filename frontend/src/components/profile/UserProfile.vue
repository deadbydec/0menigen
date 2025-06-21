<template>
  <div class="profile-wrapper">
    <div class="profile-container">
      <!-- ✅ Левая колонка -->
      <div class="left-column">
        <AvatarBlock />
        <AchievementsBlock />
      </div>

      <!-- ✅ Центральная гигастенка -->
      <div class="center-column">
        <BioBlock />
        <WallBlock />
        <PetsBlock />
      </div>

      <!-- ✅ Правая колонка -->
      <div class="right-column">
        <FriendsBlock />
        <CollectBlock />
      </div>
    </div>
  </div>
</template>


<script setup>

import AvatarBlock from "@/components/profile/AvatarBlock.vue";
import BioBlock from "@/components/profile/BioBlock.vue";
import WallBlock from "@/components/profile/WallBlock.vue";
import FriendsBlock from "@/components/profile/FriendsBlock.vue";
import AchievementsBlock from "@/components/profile/AchievementsBlock.vue";
import CollectBlock from "@/components/profile/CollectBlock.vue";
import PetsBlock from "@/components/profile/PetsBlock.vue";

</script>

<style scoped>
.profile-wrapper {
  display:flex;
  justify-content: center;
  width: 100%;
  padding-top:120px;
  box-sizing: border-box;

}

.profile-container {
  width: auto;
  max-width: 1300px; /* 💥 Твоя желаемая ширина */
  display: grid;
  grid-template-columns: 1fr 2fr 1fr;
  gap: 10px;
  background: rgba(255, 0, 0, 0.1);
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

/* Правая колонка */


/* Блоки */
.avatar-block, .bio-block, .wall-block, .friends-block, .achievements-block, .collect-block, .pets-block {
  background: #181818e7;
  padding: 16px;
  border-radius: 18px;
  border: 1px solid rgb(196, 196, 196);
  box-shadow: 0 2px 5px rgba(0, 0, 0, 0.1);
  font-family: 'JetBrains Mono', monospace;
  backdrop-filter: blur(1px);
}
</style>



  
  