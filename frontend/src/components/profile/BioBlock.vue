<template>
  <div class="bio-block">
    <h2>Досье</h2>

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
import { computed } from 'vue'
const profile = computed(() => profileStore.profile)


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
  if (!profile) {
    console.warn('⛔ Профиль ещё не загружен');
    return;
  }

  if (editableBio.value.trim() !== profile.bio) {
    await profileStore.updateBio(editableBio.value);
    profile.bio = editableBio.value; // ✅ теперь безопасно
  }

  isEditing.value = false;
};


</script>

<style scoped>
.bio-block {
  max-width: 600px;
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

.bio-block h2 {
  position: relative;
  font-size: 18px;
  text-align: left;
  color: white;
  margin-bottom: 8px;
}

.bio-block h2::after {
  content: "";
  display: block;
  width: 100%;
  height: 1px;
  background-color: white;
  opacity: 0.4; /* 👈 мягкий, неяркий акцент */
  margin: 6px auto 0;
  border-radius: 1px;
}

</style>
  