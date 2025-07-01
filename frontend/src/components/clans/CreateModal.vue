<template>
    <Teleport to="body">
  <div v-if="visible" class="create-modal">
    <div class="create-modal-content">
      <h2>🛡️ {{ liveTitle }}</h2>

        <img
      :src="createImage"
      class="create-banner"
      alt="Баннер магазина"
    />
    <p class="caption">«Клан — это не ты, это то, что растёт из тебя»</p>

      <form @submit.prevent="submitForm" class="form">
        <input
          v-model.trim="form.name"
          type="text"
          @input="playTypeSound"
          placeholder="Название клана (до 20 символов)"
          maxlength="20"
          required
        />

        <textarea
          v-model="form.description"
          rows="3"
          placeholder="Описание клана (опционально)"
        ></textarea>

        <label class="checkbox">
          <input type="checkbox" v-model="form.is_private" />
          Приватный клан
        </label>

        <div class="buttons">
          <button type="submit" :disabled="loading">
            🚀 Создать
          </button>
          <button type="button" @click="$emit('close')">
            ❌ Отмена
          </button>
        </div>

        <div v-if="error" class="error-msg">⚠️ {{ error }}</div>
      </form>
    </div>
  </div>
  </Teleport>
</template>

<script setup>
import { ref } from 'vue'
import { useClansStore } from '@/store/clans'
import { useToastStore } from '@/store/toast'

const props = defineProps({ visible: Boolean })
const emit = defineEmits(['close'])

const clansStore = useClansStore()
const toast = useToastStore()
const createImage = '/src/assets/clan_create.png'  // или путь куда ты положил баннер

const loading = ref(false)
const error = ref(null)

const form = ref({
  name: '',
  description: '',
  is_private: true
})

async function submitForm() {
  if (!form.value.name.trim()) return (error.value = 'Укажи название!')
  loading.value = true
  error.value = null

  const res = await clansStore.createClan({ ...form.value })

  loading.value = false

  if (res.success) {
    toast.success("🎉 Клан создан!")
    emit('close')
  } else {
    error.value = res.error || 'Что-то пошло не так'
  }
}

const liveTitle = computed(() => {
  return form.value.name.trim()
    ? form.value.name.slice(0, 30) // ограничение на всякий
    : "Новый клан"
})

const lastSoundTime = ref(0)
const typeSound = new Audio("/sfx/type-soft.mp3")

function playTypeSound() {
  const now = Date.now()
  if (now - lastSoundTime.value < 50) return  // ⏱ анти-флуд
  lastSoundTime.value = now

  typeSound.currentTime = 0
  typeSound.play().catch(() => {}) // 💥 на всякий
}
</script>

<style scoped>

.caption {
  text-align: center;
  font-size: 0.8em;
  color: #999;
  margin-top: -0.6em;
  margin-bottom: 1.2em;
  font-style: italic;
  text-shadow: 
    0 0 2px rgb(0, 0, 0), 
    0 0 4px rgb(255, 255, 255), 
    0 0 2px rgb(0, 0, 0);
}

.create-banner {
  padding-bottom: 20px;
  padding-top: 20px;
  max-width: 70%;       
  height: auto;         
  object-fit: contain;  
  border-radius: 20px;
  display: block;
  
  margin: 4px auto;
  animation: floatY 3.5s ease-in-out infinite;
}

@keyframes floatY {
  0%   { transform: translateY(0); }
  50%  { transform: translateY(-8px); }
  100% { transform: translateY(0); }
}

.create-modal {
  position: fixed;
  inset: 0;
  display: flex;
  align-items: center;
  
  justify-content: center;
  z-index: 1000;
  animation: fadeInBg 0.3s ease forwards;
  background: rgba(0, 0, 0, 0.6);
}

.create-modal-content {
  background: #161616;
  border: 1px solid rgba(255, 255, 255, 0.322);
  border-radius: 12px;
  color: #fff;
  padding: 22px 26px;
  width: 100%;
  max-width: 420px;
  box-shadow: 0 0 24px rgba(0, 0, 0, 0.5);
  animation: scaleIn 0.25s ease forwards;
  text-align: left;
  font-family: 'Fira Code', monospace;
}

.form {
  display: flex;
  flex-direction: column;
  gap: 1em;
}

input[type="text"],
textarea {
  padding: 0.6em 0.8em;
  background: #222;
  border: 1px solid #555;
  border-radius: 6px;
  color: #fff;
  font-family: inherit;
}

.checkbox {
  display: flex;
  align-items: center;
  gap: 0.5em;
  font-size: 0.9em;
}

.buttons {
  display: flex;
  justify-content: flex-end;
  gap: 1em;
}

button {
  padding: 0.5em 1.1em;
  border: none;
  border-radius: 6px;
  cursor: pointer;
  font-weight: bold;
  font-family: inherit;
  transition: 0.2s ease;
}

button[type="submit"] {
  background:linear-gradient(20deg, rgb(5, 73, 70), rgb(13, 211, 211));
  color: rgb(24, 24, 24);
}

button[type="button"] {
  background: #333;
  color: white;
}

button:disabled {
  opacity: 0.6;
  pointer-events: none;
}

.error-msg {
  color: #ff8080;
  font-size: 0.85em;
  margin-top: -0.4em;
}
@keyframes scaleIn {
  0%   { transform: scale(0.9); opacity: 0; }
  100% { transform: scale(1);   opacity: 1; }
}
</style>
