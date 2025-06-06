<template>

  <div class="profile-container">
    <!-- ✅ Левая колонка -->
    <div class="left-column">
      <AvatarBlock />
      <AchievementsBlock />
      
      
    </div>

    <div class="center-column">
    <!-- ✅ Центральная гигастенка -->
    <BioBlock />
    <WallBlock />
    <PetsBlock />
  </div>
    

    <!-- ✅ Правая колонка (Друзья + Ачивки) -->
    <div class="right-column">
      <CollectBlock/>
      <FriendsBlock />
      
    </div>

    <!--<div class="last-column">-->
      

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
.profile-container {
  zoom: 95%;
  display: grid;
  grid-template-columns: 2fr 4fr 2fr;
  grid-template-rows: auto;
  gap: 10px;
  padding: 20px;
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
.avatar-block, .bio-block, .wall-block, .friends-block, .achievements-block, .actives-block, .collect-block, .libra-block, .pets-block {
  background:rgba(38, 32, 39, 0.48);
  padding: 16px;
  border-radius: 10px;
  box-shadow: 0 2px 5px rgba(0, 0, 0, 0.1);
  font-family: 'JetBrains Mono', monospace;
  backdrop-filter: blur(7px);
}
</style>



  
  