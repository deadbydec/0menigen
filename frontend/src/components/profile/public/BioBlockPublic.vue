<template>
  <div class="bio-block">
    <h2>Биография</h2>

    <p>{{ profile?.bio || "Нет информации" }}</p>
  </div>
</template>

<script setup>
const props = defineProps({
  profile: {
    type: Object,
    required: true
  }
})


</script>


<style scoped>
.bio-block {
  display: flex;
  max-width: 700px;
  flex-direction: column;
  backdrop-filter: blur(7px);
  background:rgba(38, 32, 39, 0.48);
  border: 1px solid #2e2c2c;
  border-radius: 8px;
  padding: 10px;
  font-size: 13px;
  gap: 10px;

}

textarea {
  position: relative;
  left: 1px;
  width: 95%;
  min-height: 90px;
  background:rgba(255, 255, 255, 0.144);
  resize: none;
  border: 1px solid #ccc;
  border-radius: 11px;
  padding: 5px;
}

.edit-btn,
.save-btn {
  position: sticky;
  top: 20px; /* Фиксируем кнопку на высоте 10px от верха */
  background:transparent;
  color: white;
  padding: 10px 12px;
  border: none;
  border-radius: 5px;
  cursor: pointer;
  
}

</style>
  