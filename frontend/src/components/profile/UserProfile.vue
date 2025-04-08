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
  </div>
    

    <!-- ✅ Правая колонка (Друзья + Ачивки) -->
    <div class="right-column">
      <ActivesBlock />
      <FriendsBlock />
      
    </div>

    <div class="last-column">
      <CollectBlock/>
      <LibraBlock/>
    </div>
  </div>
</template>

<script setup>
import AvatarBlock from "@/components/profile/AvatarBlock.vue";
import BioBlock from "@/components/profile/BioBlock.vue";
import WallBlock from "@/components/profile/WallBlock.vue";
import FriendsBlock from "@/components/profile/FriendsBlock.vue";
import AchievementsBlock from "@/components/profile/AchievementsBlock.vue";
import ActivesBlock from "@/components/profile/ActivesBlock.vue";
import CollectBlock from "@/components/profile/CollectBlock.vue";
import LibraBlock from "@/components/profile/LibraBlock.vue";
</script>

<style scoped>
.profile-container {
  display: grid;
  grid-template-columns: 1fr 2fr 1fr 1fr;
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
.last-column {
  display: flex;
  flex-direction: column;
  gap: 10px;
}

/* Блоки */
.avatar-block, .bio-block, .wall-block, .friends-block, .achievements-block, .actives-block, .collect-block, .libra-block {
  background: rgba(0, 0, 0, 0.623);
  padding: 15px;
  border-radius: 10px;
  box-shadow: 0 2px 5px rgba(0, 0, 0, 0.1);
}
</style>



  
  