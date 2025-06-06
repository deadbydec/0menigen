<template>
  <!-- 🌱 Birth modal -->
  <div v-if="visible" class="pet-modal">
    <div class="pet-modal-content">
      <!-- close button -->
      <button class="close-modal-btn" @click="$emit('close')">✕</button>

      <h3>🎉 Ваш питомец вылупился!</h3>
      <p class="subtitle">Как назовём существо?</p>

      <input
  v-model.trim="petName"
  :class="{ invalid: !nameValid }"                       
  placeholder="Введите имя (1-30 симв.)"                
  maxlength="15" required                                 
  @keyup.enter="confirmBirth"
/>

      <div class="pet-modal-buttons">
        <button class="use-button" :disabled="!nameValid" @click="confirmBirth">Подтвердить</button>
        <button class="destroy-button" @click="$emit('close')">Отмена</button>
      </div>
    </div>
  </div>
</template>

<script setup>
import { ref, watch, computed } from 'vue'          
import { useRouter } from 'vue-router'
import api from '@/utils/axios'
import { useToastStore } from '@/store/toast'

const props = defineProps({
  visible: Boolean,
  incubationId: Number
})
const emit  = defineEmits(['close', 'hatched'])

const petName = ref('')
const nameValid = computed(() => petName.value.trim().length >= 3 && petName.value.trim().length <= 15) 
const toast   = useToastStore()
const router  = useRouter()

function getCookie (n) {
  const m = document.cookie.match(new RegExp('(^| )' + n + '=([^;]+)'))
  return m ? m[2] : null
}
const csrfToken = getCookie('csrf_access_token')

async function confirmBirth () {
  if (!nameValid.value) {
    toast.addToast('Имя должно быть от 3 до 15 символов', { type: 'error' })   
    return
  }
  try {
    const { data } = await api.post(
      '/inventory/hatch',
      { name: petName.value.trim(),
      incubation_id: props.incubationId
      },
      { withCredentials: true, headers: { 'X-CSRF-TOKEN': csrfToken } }
    )
    emit('hatched', data)
    emit('close')
    toast.addToast(`🎉 ${data.name} появился на свет!`, { type: 'success' })    
    router.push(`/pet/${data.id}`)
  } catch (err) {
    const msg = err.response?.data?.detail || 'Ошибка при рождении питомца'
    toast.addToast(msg, { type: 'error' })
    console.error(err)
  }
}

watch(() => props.visible, v => { if (!v) petName.value = '' })
</script>

<style scoped>
.invalid { border-color:#c33; }                          
.use-button:disabled { opacity:.4; cursor:not-allowed; } 
/* ───────────── BACKDROP ───────────── */
.pet-modal {
  position: fixed;
  inset: 0;
  display: flex;
  align-items: center;
  justify-content: center;

  backdrop-filter: blur(1px);
  z-index: 1000;
  animation: fadeInBg 0.3s ease forwards;
}
@keyframes fadeInBg {
  0%   { opacity: 0; }
  100% { opacity: 1; }
}

/* ───────────── CONTENT ───────────── */
.pet-modal-content {
  position: relative;
  backdrop-filter: blur(5px);
  background: rgba(24, 24, 24, 0.925);
  border-radius: 12px;
  padding: 24px 28px;
  min-width: 320px;
  max-width: 420px;
  box-shadow: 0 0 20px rgba(0, 0, 0, 0.705);
  animation: scaleIn 0.25s ease forwards;
  text-align: center;
  font-family: 'Fira Code', monospace;
}
@keyframes scaleIn {
  0%   { transform: scale(0.9); opacity: 0; }
  100% { transform: scale(1);   opacity: 1; }
}

.subtitle {
  margin-top: 4px;
  font-size: 0.9rem;
  color: #aaa;
}

/* input */
.pet-modal-content input {
  display: block;
  width: 90%;
  margin: 18px auto 14px;
  padding: 10px;
  font-family: inherit;
  font-size: 14px;
  background: #1e1e1e;
  border: 1px solid #444;
  border-radius: 6px;
  color: #ccc;
}

/* buttons */
.pet-modal-buttons {
  display: flex;
  justify-content: center;
  gap: 12px;
}

.use-button {
  background: linear-gradient(135deg, #22cc88, #075e41bd);
  color: #fff;
  border: none;
  max-width: 150px;
  padding: 8px 16px;
  border-radius: 8px;
  transition: 0.15s transform, 0.15s box-shadow;
}

.destroy-button {
  background: linear-gradient(135deg, #444, #000000ab);
  color: #fff;
  border: none;
  max-width: 150px;
  padding: 8px 16px;
  border-radius: 8px;
  transition: 0.15s transform, 0.15s box-shadow;
}

.use-button:hover {
  transform: translateY(-2px);
  box-shadow: 0 4px 10px rgba(0, 255, 150, 0.4);
}

.destroy-button:hover {
  transform: translateY(-2px);
  box-shadow: 0 4px 10px rgba(255, 0, 0, 0.3);
}

/* close button */
.close-modal-btn {
  position: absolute;
  top: 10px;
  right: 12px;
  background: transparent;
  color: #aaa;
  border: none;
  font-size: 18px;
  cursor: pointer;
  transition: color 0.2s;
}
.close-modal-btn:hover { color: #fff; }
</style>
