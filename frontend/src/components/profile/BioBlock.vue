<template>
  <div class="bio-block">
    <h3>О себе</h3>

    <div v-if="isEditing">
      <textarea
        v-model="editableBio"
        @keyup.enter="saveBio"
        @blur="saveBio"
        ></textarea>
    </div>

    <p v-else @click="startEditing">
      {{ profile?.bio || "Нет информации" }}
    </p>

    <button
      class="edit-btn"
      v-if="!isEditing"
      @click="startEditing"
    >
      <i class="fa-solid fa-pen"></i>
    </button>

    <button
      class="save-btn"
      v-else
      @click="saveBio"
    >
      <i class="fa-solid fa-floppy-disk"></i>
    </button>
  </div>
</template>

  
<script setup>
import { ref, watch } from "vue";
import { useProfileStore } from "@/store/profile";

const profileStore = useProfileStore();
const profile = profileStore.profile;

const isEditing = ref(false);
const editableBio = ref("");

// 🔥 следим за реактивным обновлением
watch(
  () => profile?.bio,
  (newBio) => {
    editableBio.value = newBio || "";
  }
);

const startEditing = () => {
  editableBio.value = profile?.bio || "";
  isEditing.value = true;
};

const saveBio = async () => {
  if (editableBio.value.trim() !== profile?.bio) {
    await profileStore.updateBio(editableBio.value);
    profile.bio = editableBio.value; // 💥 сразу меняем на клиенте
  }
  isEditing.value = false;
};

</script>

<style scoped>
.bio-block {
  position: relative;
  max-width: 400px;
  border: 2px solid rgba(0, 0, 0, 0.692);
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
  